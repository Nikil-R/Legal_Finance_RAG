"""
Retrieval + reranking pipeline. (v1.1)
"""

from __future__ import annotations

import time

from app.config import settings
from app.reranking.context_builder import ContextBuilder
from app.reranking.reranker import CrossEncoderReranker
from app.retrieval import HybridRetriever
from app.retrieval.query_rewriter import QueryRewriter
from app.retrieval.graph_retriever import GraphRetriever
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _error_result(
    error: str, query: str, domain: str, candidates_found: int = 0, **extra
) -> dict:
    return {
        "success": False,
        "error": error,
        "query": query,
        "domain": domain,
        "candidates_found": candidates_found,
        "context": None,
        "sources": [],
        **extra,
    }


class RetrievalPipeline:
    def __init__(self) -> None:
        logger.info("Initialising RetrievalPipeline...")
        self._retriever = HybridRetriever()
        self._reranker = CrossEncoderReranker()
        self._context_builder = ContextBuilder()
        self._rewriter = QueryRewriter()
        self._graph_retriever = GraphRetriever()
        logger.info("RetrievalPipeline ready.")

    def run(
        self,
        query: str,
        domain: str = "all",
        retrieval_top_k: int | None = None,
        rerank_top_k: int | None = None,
        min_relevance_score: float = -5.0,
        session_id: str | None = None,
        owner_id: str | None = None,
    ) -> dict:
        pipeline_start = time.perf_counter()
        
        # Use settings if not provided
        if retrieval_top_k is None:
            retrieval_top_k = settings.TOP_K_RETRIEVAL
        if rerank_top_k is None:
            rerank_top_k = settings.TOP_K_RERANK

        query = query.strip() if query else ""
        if not query:
            return _error_result("Query must not be empty.", query, domain)

        rewritten_query = query
        rewrite_meta = {"original_query": query, "rewritten_query": query}
        if settings.ENABLE_QUERY_REWRITE:
            rewrite_meta = self._rewriter.rewrite(query, domain=domain)
            rewritten_query = rewrite_meta["rewritten_query"]

        retrieval_start = time.perf_counter()
        candidates = self._retriever.retrieve(
            rewritten_query,
            domain=domain,
            top_k=retrieval_top_k,
            session_id=session_id,
            owner_id=owner_id,
        )
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1_000
        logger.info("Retrieved %d candidates in %.1f ms.", len(candidates), retrieval_ms)

        if not candidates:
            return _error_result(
                "No relevant documents found",
                query,
                domain,
                retrieval_time_ms=round(float(retrieval_ms), 1),
                rewritten_query=rewritten_query,
                query_rewrite=rewrite_meta,
            )

        reranking_start = time.perf_counter()
        reranked = self._reranker.rerank_with_threshold(
            query,
            candidates,
            top_k=rerank_top_k,
            min_score=min_relevance_score,
        )
        reranking_ms = (time.perf_counter() - reranking_start) * 1_000
        logger.info("Reranked to %d chunks in %.1f ms.", len(reranked), reranking_ms)

        if not reranked:
            return _error_result(
                "No sufficiently relevant documents found",
                query,
                domain,
                candidates_found=len(candidates),
                candidates_passed_threshold=0,
                retrieval_time_ms=round(retrieval_ms, 1),
                reranking_time_ms=round(reranking_ms, 1),
                rewritten_query=rewritten_query,
                query_rewrite=rewrite_meta,
            )

        context_data = self._context_builder.build_context_with_metadata(reranked)
        
        # --- Graph Expansion ---
        graph_expansion = self._graph_retriever.get_context_expansion(query)
        if graph_expansion:
            context_data["context_string"] = f"{graph_expansion}\n\n{context_data['context_string']}"
            
        total_ms = (time.perf_counter() - pipeline_start) * 1_000

        return {
            "success": True,
            "query": query,
            "rewritten_query": rewritten_query,
            "query_rewrite": rewrite_meta,
            "domain": domain,
            "candidates_found": len(candidates),
            "candidates_reranked": len(reranked),
            "context": context_data["context_string"],
            "sources": context_data["sources"],
            "truncated": context_data["truncated"],
            "top_score": reranked[0]["rerank_score"],
            "retrieval_time_ms": round(retrieval_ms, 1),
            "reranking_time_ms": round(reranking_ms, 1),
            "total_time_ms": round(total_ms, 1),
        }

    def run_simple(self, query: str, domain: str = "all") -> tuple[str, list[dict]] | None:
        result = self.run(query, domain=domain)
        if not result["success"]:
            return None
        return result["context"], result["sources"]
