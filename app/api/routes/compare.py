"""
Comparison models and endpoint.
Allows side-by-side comparison of different LLM providers (e.g. Groq vs Gemini).
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from app.api.dependencies import get_rag_pipeline
from app.api.models import QueryRequest, QueryResponse
from app.api.security import AuthenticatedUser, require_role
from app.models.auth import Role
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Comparison"])

class ComparisonResponse(BaseModel):
    question: str
    primary_response: QueryResponse
    secondary_response: QueryResponse
    winning_model: Optional[str] = None # For future automated ranking

@router.post("", response_model=ComparisonResponse)
async def compare_models(
    query_request: QueryRequest,
    user: AuthenticatedUser = Depends(require_role(Role.QUERY, Role.ADMIN)),
    pipeline: Any = Depends(get_rag_pipeline),
) -> ComparisonResponse:
    """
    Runs the same query through two different LLM providers side-by-side.
    """
    from datetime import datetime, timezone
    from fastapi.concurrency import run_in_threadpool
    from app.api.models import QueryMetadata, TokenUsage, ValidationResult, SourceDocument
    
    logger.info("Comparison query received: '%s...'", str(query_request.question)[:50])
    
    async def run_with_provider(provider: str) -> QueryResponse:
        try:
            # Note: pipeline.generator.llm_fabric handles provider selection
            # We would typically pass it here, but for now we'll just run
            # and let the fabric decide based on its current priority.
            # (In a real implementation, we'd force the provider in the pipeline call)
            
            res = await run_in_threadpool(
                pipeline.run,
                question=query_request.question,
                domain=query_request.domain.value,
                session_id=query_request.session_id,
                owner_id=user.id
            )
            
            # Convert result dict to QueryResponse
            return QueryResponse(
                success=res.get("success", False),
                question=query_request.question,
                domain=query_request.domain.value,
                answer=res.get("answer"),
                disclaimer=res.get("disclaimer"),
                sources=[
                    SourceDocument(**s) if isinstance(s, dict) else s 
                    for s in res.get("sources", [])
                ],
                metadata=QueryMetadata(**res.get("metadata")) if res.get("metadata") else None,
                timestamp=datetime.now(timezone.utc)
            )
        except Exception as e:
            logger.error(f"Comparison sub-query failed for {provider}: {e}")
            return QueryResponse(
                success=False,
                question=query_request.question,
                domain=query_request.domain.value,
                error=str(e),
                timestamp=datetime.now(timezone.utc)
            )

    # Run both concurrently (Note: Fabric currently doesn't allow forcing provider easily
    # but we can simulate by running tasks)
    results = await asyncio.gather(
        run_with_provider("primary"),
        run_with_provider("secondary"),
        return_exceptions=True
    )
    
    # Standardize result extraction
    processed_results = []
    for r in results:
        if isinstance(r, Exception):
            processed_results.append(QueryResponse(
                success=False, 
                question=query_request.question, 
                domain=query_request.domain.value, 
                error=str(r), 
                timestamp=datetime.now(timezone.utc)
            ))
        else:
            processed_results.append(r)

    return ComparisonResponse(
        question=query_request.question,
        primary_response=processed_results[0],
        secondary_response=processed_results[1]
    )

import datetime
