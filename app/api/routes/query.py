"""
Query endpoints for the RAG system.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_pipeline, get_retrieval_pipeline, get_tool_orchestrator
from app.api.models import (
    ErrorResponse,
    QueryMetadata,
    QueryRequest,
    QueryResponse,
    RetrievalOnlyRequest,
    RetrievalResponse,
    SourceDocument,
    TokenUsage,
    ValidationResult,
)
from app.api.rate_limit import limiter
from app.api.security import AuthenticatedUser, require_role
from app.config import settings
from app.legal_disclaimers import LegalDisclaimers
from app.models.auth import Role
from app.observability import (
    metrics,
    query_counter,
    query_latency,
    tracer,
    logger as structlog_logger,
)
from app.reranking import RetrievalPipeline
from app.utils.logger import get_logger
from app.utils.pdf_gen import generate_query_report
from app.utils.pii_redactor import redact_pii
from app.utils.session_ownership import verify_session_ownership
from app.generation.tax_validator import TaxValidator

if TYPE_CHECKING:
    from app.generation import RAGPipeline, ToolOrchestrator

# Use structlog for structured logging throughout this module
logger = structlog_logger.bind(module="api.query")

router = APIRouter(tags=["Query"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class ExportRequest(QueryRequest):
    answer: str
    sources: List[Dict[str, Any]] = []


async def _run_with_timeout(fn: Any, *args: Any, timeout_seconds: int, **kwargs: Any) -> Any:
    """Run a sync function in a threadpool with a timeout."""
    return await asyncio.wait_for(
        run_in_threadpool(fn, *args, **kwargs),
        timeout=float(timeout_seconds),
    )


# ---------------------------------------------------------------------------
# Streaming endpoint (SSE)
# ---------------------------------------------------------------------------

@router.get(
    "/stream",
    summary="Stream query responses (SSE)",
    description="Server-Sent Events streaming endpoint for real-time answers"
)
@limiter.limit("60/hour")
async def stream_query(
    request: Request,
    question: str,
    domain: str = "all",
    session_id: Optional[str] = None,
    user: AuthenticatedUser = Depends(require_role(Role.QUERY, Role.INGEST, Role.ADMIN)),
    pipeline: Any = Depends(get_rag_pipeline),
    orchestrator: Any = Depends(get_tool_orchestrator),
):
    """Streaming query endpoint using Server-Sent Events."""
    
    processed_question = (
        redact_pii(question)
        if settings.PII_REDACTION_ENABLED
        else question
    )
    
    logger.info(
        "stream_query_received",
        question_preview=str(processed_question)[:50],
        domain=domain,
        session_id=session_id,
    )
    
    async def event_generator():
        try:
            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'question': processed_question})}\n\n"
            
            # Verify session ownership
            if session_id and not verify_session_ownership(
                session_id=session_id,
                owner_id=user.id,
                persist_dir=settings.CHROMA_PERSIST_DIR,
            ):
                yield f"data: {json.dumps({'type': 'error', 'error': 'Session does not belong to current user'})}\n\n"
                return
            
            # Get retrieval results
            yield f"data: {json.dumps({'type': 'status', 'message': 'Searching documents...'})}\n\n"
            
            retrieval_result = await asyncio.wait_for(
                run_in_threadpool(
                    pipeline.retrieval_pipeline.run,
                    query=processed_question,
                    domain=domain,
                    session_id=session_id,
                    owner_id=user.id,
                ),
                timeout=float(settings.REQUEST_TIMEOUT_SECONDS),
            )
            
            if not retrieval_result.get("success"):
                yield f"data: {json.dumps({'type': 'error', 'error': retrieval_result.get('error', 'Retrieval failed')})}\n\n"
                return
            
            sources = retrieval_result.get("sources", [])
            yield f"data: {json.dumps({'type': 'status', 'message': f'Found {len(sources)} relevant sources. Generating answer...'})}\n\n"
            
            # Generate answer with tool calling if enabled
            if settings.ENABLE_TOOL_CALLING:
                result = await asyncio.wait_for(
                    orchestrator.process_with_tools(
                        question=processed_question,
                        system_prompt=pipeline.generator.system_prompt,
                        context_chunks=sources if sources else None,
                    ),
                    timeout=float(settings.REQUEST_TIMEOUT_SECONDS),
                )
            else:
                # Traditional RAG flow
                result = await asyncio.wait_for(
                    run_in_threadpool(
                        pipeline.run,
                        question=processed_question,
                        domain=domain,
                        session_id=session_id,
                        owner_id=user.id,
                    ),
                    timeout=float(settings.REQUEST_TIMEOUT_SECONDS),
                )
            
            if not result.get("success"):
                yield f"data: {json.dumps({'type': 'error', 'error': result.get('error', 'Generation failed')})}\n\n"
                return
            
            # Stream the answer in chunks
            answer_text = str(result.get("answer", ""))
            chunk_size = 30  # Characters per chunk
            
            for i in range(0, len(answer_text), chunk_size):
                chunk = answer_text[i:i + chunk_size]
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                await asyncio.sleep(0.03)  # Delay for typing effect
            
            # Send sources
            formatted_sources = []
            for src in sources[:5]:  # Top 5 sources
                if isinstance(src, dict):
                    formatted_sources.append({
                        "reference_id": src.get("reference_id", 0),
                        "source": src.get("source", "unknown"),
                        "domain": src.get("domain", "unknown"),
                        "relevance_score": float(src.get("relevance_score") or src.get("rerank_score") or 0.0),
                        "excerpt": src.get("excerpt", src.get("content", "")[:200] + "..."),
                    })
            
            if formatted_sources:
                yield f"data: {json.dumps({'type': 'sources', 'sources': formatted_sources})}\n\n"
            
            # Send metadata
            raw_meta = result.get("metadata", {})
            meta = raw_meta if isinstance(raw_meta, dict) else {}
            
            metadata = {
                "model": str(meta.get("model", "unknown")),
                "total_time_ms": float(meta.get("total_time_ms", 0)),
                "token_usage": meta.get("token_usage", {}),
                "tool_calls": result.get("tool_calls_made", []) if settings.ENABLE_TOOL_CALLING else [],
            }
            
            yield f"data: {json.dumps({'type': 'metadata', 'metadata': metadata})}\n\n"
            
            # Select disclaimer based on domain
            if domain == "tax":
                disclaimer = LegalDisclaimers.get_tax_disclaimer()
            elif domain == "legal":
                disclaimer = LegalDisclaimers.get_court_case_disclaimer()
            elif domain == "finance":
                disclaimer = LegalDisclaimers.get_compliance_disclaimer()
            else:
                disclaimer = LegalDisclaimers.get_general_disclaimer()
            
            yield f"data: {json.dumps({'type': 'disclaimer', 'content': disclaimer})}\n\n"
            
            # Send completion
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
            # Post-generation Tax Validation
            if domain == "tax" or "tax" in str(processed_question).lower() or "income" in str(processed_question).lower():
                tax_validator = TaxValidator()
                validation = tax_validator.validate(answer_text, processed_question)
                if not validation["valid"]:
                    logger.warning("Yielding tax correction", correction=validation["warning"])
                    yield f"data: {json.dumps({'type': 'correction', 'message': validation['warning'], 'correct_answer': validation['correct_tax']})}\n\n"
            
            logger.info("stream_query_completed", user_id=user.id)
            
        except asyncio.TimeoutError:
            logger.error("stream_query_timeout", user_id=user.id)
            yield f"data: {json.dumps({'type': 'error', 'error': f'Request timed out after {settings.REQUEST_TIMEOUT_SECONDS}s'})}\n\n"
            
        except Exception as e:
            logger.error("stream_query_error", user_id=user.id, error=str(e), exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        }
    )


# ---------------------------------------------------------------------------
# Export endpoint
# ---------------------------------------------------------------------------

@router.post("/export", response_class=StreamingResponse)
async def export_query_result(
    export_req: ExportRequest,
    user: AuthenticatedUser = Depends(require_role(Role.QUERY, Role.ADMIN)),
) -> StreamingResponse:
    """Exports a query result to PDF."""
    try:
        pdf_buffer = generate_query_report(
            query=export_req.question,
            answer=export_req.answer,
            sources=export_req.sources,
        )
        filename = f"legal_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        logger.error("Export error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


# ---------------------------------------------------------------------------
# Main query endpoint
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=QueryResponse,
    responses={
        200: {"description": "Successful query response"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Ask a question to the RAG system",
    description="""
    Submit a question to the Legal/Finance RAG system.

    The system will:
    1. Search for relevant document chunks using hybrid retrieval
    2. Re-rank results using a cross-encoder
    3. Generate an answer using Llama 3.1 via Groq (or Gemini as fallback)
    4. Include citations and a legal disclaimer

    You can filter by domain (tax, finance, legal) or search all domains.
    """,
)
@limiter.limit("60/hour")
async def query(
    query_request: QueryRequest,
    request: Request,
    user: AuthenticatedUser = Depends(
        require_role(Role.QUERY, Role.INGEST, Role.ADMIN)
    ),
    pipeline: Any = Depends(get_rag_pipeline),
    orchestrator: Any = Depends(get_tool_orchestrator),
) -> QueryResponse:
    """Main RAG query endpoint with Tool Calling support."""
    processed_question = (
        redact_pii(query_request.question)
        if settings.PII_REDACTION_ENABLED
        else query_request.question
    )
    logger.info(
        "query_received",
        question_preview=str(processed_question)[:50],
        domain=query_request.domain,
        tool_calling=settings.ENABLE_TOOL_CALLING,
    )

    if query_request.session_id and not verify_session_ownership(
        session_id=query_request.session_id,
        owner_id=user.id,
        persist_dir=settings.CHROMA_PERSIST_DIR,
    ):
        raise HTTPException(
            status_code=403, detail="Session does not belong to current user."
        )

    start_time = time.time()
    with tracer.start_as_current_span("query_documents") as span:
        span.set_attribute("user.id", user.id)
        span.set_attribute("user.role", user.role.value)
        span.set_attribute("query.length", len(processed_question))
        span.set_attribute("tool_calling_enabled", settings.ENABLE_TOOL_CALLING)

        try:
            result: Dict[str, Any]

            if settings.ENABLE_TOOL_CALLING:
                # Tool-augmented flow: retrieval + orchestrator
                retrieval_result: Dict[str, Any] = await _run_with_timeout(
                    pipeline.retrieval_pipeline.run,
                    query=processed_question,
                    domain=query_request.domain.value,
                    session_id=query_request.session_id,
                    owner_id=user.id,
                    timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS,
                )

                result = await asyncio.wait_for(
                    orchestrator.process_with_tools(
                        question=processed_question,
                        system_prompt=pipeline.generator.system_prompt,
                        context_chunks=(
                            retrieval_result.get("sources", [])
                            if retrieval_result.get("success")
                            else None
                        ),
                    ),
                    timeout=float(settings.REQUEST_TIMEOUT_SECONDS),
                )

                if result.get("success"):
                    validation = pipeline.generator.validator.validate_response(
                        result["answer"],
                        len(result.get("sources", [])),
                        used_tools=len(result.get("tool_calls_made", [])) > 0,
                    )
                    result = {
                        "success": True,
                        "answer": str(result.get("answer", "")),
                        "sources": result.get("sources", []),
                        "validation": validation,
                        "metadata": {
                            "model": str(result.get("model", "unknown")),
                            "token_usage": result.get("usage", {}),
                            "total_time_ms": float(result.get("duration_ms", 0.0)),
                            "tool_calls": result.get("tool_calls_made", []),
                        },
                    }
            else:
                # Traditional RAG flow
                result = await _run_with_timeout(
                    pipeline.run,
                    question=processed_question,
                    domain=query_request.domain.value,
                    session_id=query_request.session_id,
                    owner_id=user.id,
                    timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS,
                )

            if result.get("success"):
                sources: List[SourceDocument] = []
                if query_request.include_sources:
                    raw_sources = result.get("sources", [])
                    if isinstance(raw_sources, list):
                        for src in raw_sources:
                            if isinstance(src, dict):
                                sources.append(
                                    SourceDocument(
                                        reference_id=src.get("reference_id", 0),
                                        source=src.get("source", "unknown"),
                                        domain=src.get("domain", "unknown"),
                                        relevance_score=float(
                                            src.get("relevance_score")
                                            or src.get("rerank_score")
                                            or 0.0
                                        ),
                                        origin=src.get("origin", "system"),
                                        excerpt=src.get(
                                            "excerpt",
                                            src.get("content", "")[:200] + "...",
                                        ),
                                        citation_spans=src.get("citation_spans", []),
                                    )
                                )

                raw_val = result.get("validation")
                val: Dict[str, Any] = raw_val if isinstance(raw_val, dict) else {}
                validation_result = ValidationResult(
                    overall_valid=bool(val.get("overall_valid", True)),
                    has_citations=bool(
                        val.get("citations", {}).get("has_citations", False)
                        if isinstance(val.get("citations"), dict)
                        else False
                    ),
                    has_disclaimer=bool(
                        val.get("disclaimer", {}).get("has_disclaimer", False)
                        if isinstance(val.get("disclaimer"), dict)
                        else False
                    ),
                    issues=list(val.get("issues", [])),
                )

                raw_meta = result.get("metadata")
                meta: Dict[str, Any] = raw_meta if isinstance(raw_meta, dict) else {}
                raw_token = meta.get("token_usage")
                token_usage: Dict[str, Any] = (
                    raw_token if isinstance(raw_token, dict) else {}
                )

                metadata = QueryMetadata(
                    retrieval_candidates=int(meta.get("retrieval_candidates", 0)),
                    reranked_chunks=int(meta.get("reranked_chunks", 0)),
                    top_relevance_score=float(meta.get("top_relevance_score", 0.0)),
                    model=str(meta.get("model", "unknown")),
                    prompt_version=str(meta.get("prompt_version", "v1")),
                    token_usage=TokenUsage(
                        prompt_tokens=int(token_usage.get("prompt_tokens", 0)),
                        completion_tokens=int(token_usage.get("completion_tokens", 0)),
                        total_tokens=int(token_usage.get("total_tokens", 0)),
                    ),
                    retrieval_time_ms=float(meta.get("retrieval_time_ms", 0)),
                    generation_time_ms=float(meta.get("generation_time_ms", 0)),
                    total_time_ms=float(meta.get("total_time_ms", 0)),
                    guardrails=dict(meta.get("guardrails", {})),
                    query_rewrite=dict(meta.get("query_rewrite", {})),
                    cache_hit=bool(meta.get("cache_hit", False)),
                )

                # Select disclaimer based on domain
                domain_val = query_request.domain.value
                if domain_val == "tax":
                    disclaimer = LegalDisclaimers.get_tax_disclaimer()
                elif domain_val == "legal":
                    disclaimer = LegalDisclaimers.get_court_case_disclaimer()
                elif domain_val == "finance":
                    disclaimer = LegalDisclaimers.get_compliance_disclaimer()
                else:
                    disclaimer = LegalDisclaimers.get_general_disclaimer()

                response = QueryResponse(
                    success=True,
                    question=processed_question,
                    domain=domain_val,
                    answer=result["answer"],
                    disclaimer=disclaimer,
                    sources=sources,
                    validation=validation_result,
                    metadata=metadata,
                    timestamp=datetime.now(timezone.utc),
                )

                duration = time.time() - start_time
                query_counter.labels(role=user.role.value, status="success").inc()
                query_latency.labels(endpoint="/api/v2/query").observe(duration)
                logger.info(
                    "query_completed",
                    user_id=user.id,
                    duration_ms=round(float(duration * 1000), 2),
                )
                return response

            return QueryResponse(
                success=False,
                question=processed_question,
                domain=query_request.domain.value,
                error=result.get("error", "Unknown error occurred"),
                timestamp=datetime.now(timezone.utc),
            )

        except TimeoutError:
            duration = time.time() - start_time
            metrics.inc("query_timeout_total")
            query_counter.labels(role=user.role.value, status="timeout").inc()
            logger.error(
                "query_timeout",
                user_id=user.id,
                duration_ms=round(float(duration * 1000), 2),
            )
            return QueryResponse(
                success=False,
                question=processed_question,
                domain=query_request.domain.value,
                error=f"Query timed out after {settings.REQUEST_TIMEOUT_SECONDS}s",
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as exc:
            duration = time.time() - start_time
            metrics.inc("query_failure_total")
            query_counter.labels(role=user.role.value, status="error").inc()
            logger.error(
                "query_failed",
                user_id=user.id,
                error=str(exc),
                duration_ms=round(float(duration * 1000), 2),
            )
            return QueryResponse(
                success=False,
                question=processed_question,
                domain=query_request.domain.value,
                error=str(exc),
                timestamp=datetime.now(timezone.utc),
            )


# ---------------------------------------------------------------------------
# Retrieval-only endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/retrieve",
    response_model=RetrievalResponse,
    summary="Retrieve relevant chunks without LLM generation",
    description=(
        "Returns the most relevant document chunks for a query, without generating "
        "an LLM response. Useful for debugging or custom processing."
    ),
)
@limiter.limit("60/hour")
async def retrieve_only(
    retrieval_request: RetrievalOnlyRequest,
    request: Request,
    user: AuthenticatedUser = Depends(
        require_role(Role.QUERY, Role.INGEST, Role.ADMIN)
    ),
    pipeline: Any = Depends(get_retrieval_pipeline),
) -> RetrievalResponse:
    """Retrieval-only endpoint (no LLM generation)."""
    processed_question = (
        redact_pii(retrieval_request.question)
        if settings.PII_REDACTION_ENABLED
        else retrieval_request.question
    )
    logger.info("retrieval_request", question_preview=str(processed_question)[:50])

    try:
        result: Dict[str, Any] = await _run_with_timeout(
            pipeline.run,
            query=processed_question,
            domain=retrieval_request.domain.value,
            rerank_top_k=retrieval_request.top_k,
            timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS,
        )

        if result.get("success"):
            chunks = [
                {
                    "reference_id": src["reference_id"],
                    "chunk_id": src.get("chunk_id", ""),
                    "source": src["source"],
                    "domain": src["domain"],
                    "relevance_score": src.get("rerank_score", 0.0),
                    "content": src.get("content", "")[:500],
                }
                for src in result.get("sources", [])
            ]
            return RetrievalResponse(
                success=True,
                question=processed_question,
                domain=retrieval_request.domain.value,
                chunks=chunks,
                total_found=result.get("candidates_found", 0),
                retrieval_time_ms=result.get("total_time_ms", 0),
            )

        return RetrievalResponse(
            success=False,
            question=processed_question,
            domain=retrieval_request.domain.value,
            chunks=[],
            total_found=0,
            retrieval_time_ms=0,
            error=result.get("error", "Retrieval failed"),
        )

    except TimeoutError:
        metrics.inc("retrieval_timeout_total")
        logger.error("retrieval_timeout", timeout=settings.REQUEST_TIMEOUT_SECONDS)
        return RetrievalResponse(
            success=False,
            question=processed_question,
            domain=retrieval_request.domain.value,
            chunks=[],
            total_found=0,
            retrieval_time_ms=0,
            error=f"Retrieval timed out after {settings.REQUEST_TIMEOUT_SECONDS}s",
        )

    except Exception as e:
        logger.error("retrieval_error", error=str(e), exc_info=True)
        return RetrievalResponse(
            success=False,
            question=processed_question,
            domain=retrieval_request.domain.value,
            chunks=[],
            total_found=0,
            retrieval_time_ms=0,
            error=str(e),
        )