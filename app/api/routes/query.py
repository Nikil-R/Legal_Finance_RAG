"""
Query endpoints for the RAG system.
"""

import asyncio
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool

from app.api.dependencies import get_rag_pipeline, get_retrieval_pipeline
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
from app.api.security_decorators import require_role
from app.config import settings
from app.generation import RAGPipeline
from app.models.auth import Role, User
from app.observability import (
    logger as structlog_logger,
    metrics,
    query_counter,
    query_latency,
    tracer,
)
from app.reranking import RetrievalPipeline
from app.utils.pii_redactor import redact_pii
from app.utils.session_ownership import verify_session_ownership

router = APIRouter(prefix="/query", tags=["Query"])
logger = structlog_logger.bind(module="api.query")


async def _run_with_timeout(fn, *args, timeout_seconds: int, **kwargs):
    return await asyncio.wait_for(
        run_in_threadpool(fn, *args, **kwargs),
        timeout=float(timeout_seconds),
    )


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
    3. Generate an answer using Llama 3.1 via Groq
    4. Include citations and a legal disclaimer
    
    You can filter by domain (tax, finance, legal) or search all domains.
    """,
)
@limiter.limit("60/hour")
@require_role(Role.QUERY, Role.INGEST, Role.ADMIN)
async def query(
    request: QueryRequest,
    user: User,
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
) -> QueryResponse:
    """
    Main RAG query endpoint.
    """
    processed_question = (
        redact_pii(request.question)
        if settings.PII_REDACTION_ENABLED
        else request.question
    )
    logger.info(
        "Query received: '%s...' | Domain: %s",
        processed_question[:50],
        request.domain,
    )
    if request.session_id and not verify_session_ownership(
        session_id=request.session_id,
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

        try:
            result = await _run_with_timeout(
                pipeline.run,
                question=processed_question,
                domain=request.domain.value,
                session_id=request.session_id,
                owner_id=user.id,
                timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS,
            )

            if result["success"]:
                sources = []
                if request.include_sources:
                    for src in result.get("sources", []):
                        sources.append(
                            SourceDocument(
                                reference_id=src["reference_id"],
                                source=src["source"],
                                domain=src["domain"],
                                relevance_score=src.get("relevance_score", src.get("rerank_score", 0.0)),
                                origin=src.get("origin", "system"),
                                excerpt=src.get("excerpt", src.get("content", "")[:200] + "..."),
                                citation_spans=src.get("citation_spans", []),
                            )
                        )

                val = result.get("validation", {})
                validation = ValidationResult(
                    overall_valid=val.get("overall_valid", True),
                    has_citations=val.get("citations", {}).get("has_citations", False),
                    has_disclaimer=val.get("disclaimer", {}).get("has_disclaimer", False),
                    issues=val.get("issues", []),
                )

                meta = result.get("metadata", {})
                token_usage = meta.get("token_usage", {})
                metadata = QueryMetadata(
                    retrieval_candidates=meta.get("retrieval_candidates", 0),
                    reranked_chunks=meta.get("reranked_chunks", 0),
                    top_relevance_score=meta.get("top_relevance_score", 0.0),
                    model=meta.get("model", "unknown"),
                    prompt_version=meta.get("prompt_version", "v1"),
                    token_usage=TokenUsage(
                        prompt_tokens=token_usage.get("prompt_tokens", 0),
                        completion_tokens=token_usage.get("completion_tokens", 0),
                        total_tokens=token_usage.get("total_tokens", 0),
                    ),
                    retrieval_time_ms=meta.get("retrieval_time_ms", 0),
                    generation_time_ms=meta.get("generation_time_ms", 0),
                    total_time_ms=meta.get("total_time_ms", 0),
                    guardrails=meta.get("guardrails", {}),
                    query_rewrite=meta.get("query_rewrite", {}),
                    cache_hit=meta.get("cache_hit", False),
                )

                response = QueryResponse(
                    success=True,
                    question=processed_question,
                    domain=request.domain.value,
                    answer=result["answer"],
                    sources=sources,
                    validation=validation,
                    metadata=metadata,
                    timestamp=datetime.now(timezone.utc),
                )

                duration = time.time() - start_time
                query_counter.labels(user_role=user.role.value, status="success").inc()
                query_latency.labels(endpoint="/api/v1/query").observe(duration)
                logger.info(
                    "query_completed",
                    user_id=user.id,
                    duration_ms=round(duration * 1000, 2),
                )
                return response

            return QueryResponse(
                success=False,
                question=processed_question,
                domain=request.domain.value,
                error=result.get("error", "Unknown error occurred"),
                timestamp=datetime.now(timezone.utc),
            )
        except TimeoutError:
            duration = time.time() - start_time
            metrics.inc("query_timeout_total")
            query_counter.labels(user_role=user.role.value, status="timeout").inc()
            logger.error(
                "Query timed out",
                user_id=user.id,
                duration_ms=round(duration * 1000, 2),
            )
            return QueryResponse(
                success=False,
                question=processed_question,
                domain=request.domain.value,
                error=f"Query timed out after {settings.REQUEST_TIMEOUT_SECONDS}s",
                timestamp=datetime.now(timezone.utc),
            )
        except Exception as exc:
            duration = time.time() - start_time
            metrics.inc("query_failure_total")
            query_counter.labels(user_role=user.role.value, status="error").inc()
            logger.error(
                "query_failed",
                user_id=user.id,
                error=str(exc),
                duration_ms=round(duration * 1000, 2),
            )
            raise
@router.post(
    "/retrieve",
    response_model=RetrievalResponse,
    summary="Retrieve relevant chunks without LLM generation",
    description="Returns the most relevant document chunks for a query, without generating an LLM response. Useful for debugging or custom processing.",
)
@limiter.limit("60/hour")
@require_role(Role.QUERY, Role.INGEST, Role.ADMIN)
async def retrieve_only(
    request: RetrievalOnlyRequest,
    user: User,
    pipeline: RetrievalPipeline = Depends(get_retrieval_pipeline),
) -> RetrievalResponse:
    """
    Retrieval-only endpoint (no LLM generation).
    """
    processed_question = (
        redact_pii(request.question)
        if settings.PII_REDACTION_ENABLED
        else request.question
    )
    logger.info("Retrieval request: '%s...'", processed_question[:50])

    try:
        result = await _run_with_timeout(
            pipeline.run,
            query=processed_question,
            domain=request.domain.value,
            rerank_top_k=request.top_k,
            timeout_seconds=settings.REQUEST_TIMEOUT_SECONDS,
        )

        if result["success"]:
            # Format chunks for response
            chunks = []
            for src in result.get("sources", []):
                chunks.append(
                    {
                        "reference_id": src["reference_id"],
                        "chunk_id": src.get("chunk_id", ""),
                        "source": src["source"],
                        "domain": src["domain"],
                        "relevance_score": src.get("rerank_score", 0.0),
                        "content": src.get("content", "")[:500],
                    }
                )

            return RetrievalResponse(
                success=True,
                question=processed_question,
                domain=request.domain.value,
                chunks=chunks,
                total_found=result.get("candidates_found", 0),
                retrieval_time_ms=result.get("total_time_ms", 0),
            )
        else:
            return RetrievalResponse(
                success=False,
                question=processed_question,
                domain=request.domain.value,
                chunks=[],
                total_found=0,
                retrieval_time_ms=0,
                error=result.get("error", "Retrieval failed"),
            )

    except TimeoutError:
        metrics.inc("retrieval_timeout_total")
        logger.error("Retrieval timed out after %ss", settings.REQUEST_TIMEOUT_SECONDS)
        return RetrievalResponse(
            success=False,
            question=processed_question,
            domain=request.domain.value,
            chunks=[],
            total_found=0,
            retrieval_time_ms=0,
            error=f"Retrieval timed out after {settings.REQUEST_TIMEOUT_SECONDS}s",
        )
    except Exception as e:
        logger.error("Retrieval error: %s", str(e), exc_info=True)
        return RetrievalResponse(
            success=False,
            question=processed_question,
            domain=request.domain.value,
            chunks=[],
            total_found=0,
            retrieval_time_ms=0,
            error=str(e),
        )
