"""
Query endpoints for the RAG system.
"""
from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from app.api.models import (
    QueryRequest,
    QueryResponse,
    RetrievalOnlyRequest,
    RetrievalResponse,
    SourceDocument,
    ValidationResult,
    TokenUsage,
    QueryMetadata,
    ErrorResponse
)
from app.api.dependencies import get_rag_pipeline, get_retrieval_pipeline
from app.generation import RAGPipeline
from app.reranking import RetrievalPipeline
from app.utils.logger import get_logger

router = APIRouter(prefix="/query", tags=["Query"])
logger = get_logger(__name__)


@router.post(
    "",
    response_model=QueryResponse,
    responses={
        200: {"description": "Successful query response"},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
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
    """
)
async def query(
    request: QueryRequest,
    pipeline: RAGPipeline = Depends(get_rag_pipeline)
) -> QueryResponse:
    """
    Main RAG query endpoint.
    """
    logger.info("Query received: '%s...' | Domain: %s", request.question[:50], request.domain)
    
    try:
        # Run the RAG pipeline
        result = pipeline.run(
            question=request.question,
            domain=request.domain.value
        )
        
        # Build response
        if result["success"]:
            # Build sources list
            sources = []
            if request.include_sources:
                for src in result.get("sources", []):
                    sources.append(SourceDocument(
                        reference_id=src["reference_id"],
                        source=src["source"],
                        domain=src["domain"],
                        relevance_score=src.get("relevance_score", src.get("rerank_score", 0.0)),
                        excerpt=src.get("excerpt", src.get("content", "")[:200] + "...")
                    ))
            
            # Build validation result
            val = result.get("validation", {})
            validation = ValidationResult(
                overall_valid=val.get("overall_valid", True),
                has_citations=val.get("citations", {}).get("has_citations", False),
                has_disclaimer=val.get("disclaimer", {}).get("has_disclaimer", False),
                issues=val.get("issues", [])
            )
            
            # Build metadata
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
                    total_tokens=token_usage.get("total_tokens", 0)
                ),
                retrieval_time_ms=meta.get("retrieval_time_ms", 0),
                generation_time_ms=meta.get("generation_time_ms", 0),
                total_time_ms=meta.get("total_time_ms", 0)
            )
            
            response = QueryResponse(
                success=True,
                question=request.question,
                domain=request.domain.value,
                answer=result["answer"],
                sources=sources,
                validation=validation,
                metadata=metadata,
                timestamp=datetime.now(timezone.utc)
            )
            
            logger.info("Query successful | Time: %.0fms | Tokens: %d", meta.get('total_time_ms', 0), token_usage.get('total_tokens', 0))
            return response
        
        else:
            # Query failed (no results, etc.)
            return QueryResponse(
                success=False,
                question=request.question,
                domain=request.domain.value,
                error=result.get("error", "Unknown error occurred"),
                timestamp=datetime.now(timezone.utc)
            )
    
    except Exception as e:
        logger.error("Query error: %s", str(e), exc_info=True)
        return QueryResponse(
            success=False,
            question=request.question,
            domain=request.domain.value,
            error=str(e),
            timestamp=datetime.now(timezone.utc)
        )


@router.post(
    "/retrieve",
    response_model=RetrievalResponse,
    summary="Retrieve relevant chunks without LLM generation",
    description="Returns the most relevant document chunks for a query, without generating an LLM response. Useful for debugging or custom processing."
)
async def retrieve_only(
    request: RetrievalOnlyRequest,
    pipeline: RetrievalPipeline = Depends(get_retrieval_pipeline)
) -> RetrievalResponse:
    """
    Retrieval-only endpoint (no LLM generation).
    """
    logger.info("Retrieval request: '%s...'", request.question[:50])
    
    try:
        result = pipeline.run(
            query=request.question,
            domain=request.domain.value,
            rerank_top_k=request.top_k
        )
        
        if result["success"]:
            # Format chunks for response
            chunks = []
            for src in result.get("sources", []):
                chunks.append({
                    "reference_id": src["reference_id"],
                    "chunk_id": src.get("chunk_id", ""),
                    "source": src["source"],
                    "domain": src["domain"],
                    "relevance_score": src.get("rerank_score", 0.0),
                    "content": src.get("content", "")[:500]
                })
            
            return RetrievalResponse(
                success=True,
                question=request.question,
                domain=request.domain.value,
                chunks=chunks,
                total_found=result.get("candidates_found", 0),
                retrieval_time_ms=result.get("total_time_ms", 0)
            )
        else:
            return RetrievalResponse(
                success=False,
                question=request.question,
                domain=request.domain.value,
                chunks=[],
                total_found=0,
                retrieval_time_ms=0,
                error=result.get("error", "Retrieval failed")
            )
    
    except Exception as e:
        logger.error("Retrieval error: %s", str(e), exc_info=True)
        return RetrievalResponse(
            success=False,
            question=request.question,
            domain=request.domain.value,
            chunks=[],
            total_found=0,
            retrieval_time_ms=0,
            error=str(e)
        )
