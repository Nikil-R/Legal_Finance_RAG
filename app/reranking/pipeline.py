"""
Retrieval + Re-ranking Pipeline — single entry point that runs the full
query → retrieve → rerank → context-build pipeline.
"""

from __future__ import annotations

import time

from app.reranking.context_builder import ContextBuilder
from app.reranking.reranker import CrossEncoderReranker
from app.retrieval import HybridRetriever
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _error_result(error: str, query: str, domain: str, candidates_found: int = 0, **extra) -> dict:
    """Build a standardised failure result dict."""
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
    """
    Orchestrates the complete retrieval + re-ranking pipeline:

        query
          └─► HybridRetriever  (vector + BM25 + RRF)  → ~20 candidates
                └─► CrossEncoderReranker               → top-5 precise hits
                      └─► ContextBuilder               → formatted context
    """

    def __init__(self) -> None:
        logger.info("Initialising RetrievalPipeline …")
        self._retriever = HybridRetriever()
        self._reranker = CrossEncoderReranker()
        self._context_builder = ContextBuilder()
        logger.info("RetrievalPipeline ready.")

    # ------------------------------------------------------------------

    def run(
        self,
        query: str,
        domain: str = "all",
        retrieval_top_k: int = 20,
        rerank_top_k: int = 5,
        min_relevance_score: float = 0.1,
        session_id: str | None = None,
    ) -> dict:
        """
        Execute the full pipeline and return a structured result.
        """
        pipeline_start = time.perf_counter()

        # ── 1. Input validation ───────────────────────────────────────
        query = query.strip() if query else ""
        if not query:
            return _error_result("Query must not be empty.", query, domain)

        # ── 2. Retrieval ──────────────────────────────────────────────
        retrieval_start = time.perf_counter()
        candidates = self._retriever.retrieve(
            query, 
            domain=domain, 
            top_k=retrieval_top_k, 
            session_id=session_id
        )
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1_000

        logger.info("Retrieved %d candidates in %.1f ms.", len(candidates), retrieval_ms)

        if not candidates:
            return _error_result(
                "No relevant documents found",
                query,
                domain,
                retrieval_time_ms=round(retrieval_ms, 1),
            )

        # ── 3. Re-ranking ─────────────────────────────────────────────
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
            )

        # ── 4. Context building ───────────────────────────────────────
        context_data = self._context_builder.build_context_with_metadata(reranked)

        total_ms = (time.perf_counter() - pipeline_start) * 1_000
        logger.info(
            "Pipeline complete — retrieval %.1f ms | reranking %.1f ms | total %.1f ms.",
            retrieval_ms,
            reranking_ms,
            total_ms,
        )

        # ── 5. Return success ─────────────────────────────────────────
        return {
            "success": True,
            "query": query,
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

    # ------------------------------------------------------------------

    def run_simple(
        self,
        query: str,
        domain: str = "all",
    ) -> tuple[str, list[dict]] | None:
        """
        Simplified interface: returns ``(context_string, sources)`` or
        ``None`` if the pipeline produced no usable results.
        """
        result = self.run(query, domain=domain)
        if not result["success"]:
            return None
        return result["context"], result["sources"]
