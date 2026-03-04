"""
Unified Hybrid Retriever — public interface to the retrieval subsystem.

Combines VectorRetriever + BM25Retriever via RRFusion into a single call.
"""

from __future__ import annotations

import time

from app.config import settings
from app.retrieval.bm25_search import BM25Retriever
from app.retrieval.fusion import RRFusion
from app.retrieval.vector_search import VectorRetriever
from app.utils.logger import get_logger

logger = get_logger(__name__)

VALID_DOMAINS = {"tax", "finance", "legal", "all"}


class HybridRetriever:
    """
    High-level retrieval interface that runs vector + BM25 search in parallel
    and fuses the results with Reciprocal Rank Fusion.
    """

    def __init__(self) -> None:
        logger.info("Initialising HybridRetriever …")
        self._vector = VectorRetriever(
            persist_dir=settings.CHROMA_PERSIST_DIR,
            embedding_model=settings.EMBEDDING_MODEL,
        )
        self._bm25 = BM25Retriever(persist_dir=settings.CHROMA_PERSIST_DIR)
        self._rrf = RRFusion(k=60)
        logger.info("HybridRetriever ready.")

    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        domain: str = "all",
        top_k: int | None = None,
    ) -> list[dict]:
        """
        Run hybrid retrieval and return re-ranked results.

        Parameters
        ----------
        query:  Natural-language question.
        domain: "tax", "finance", "legal", or "all" (default).
        top_k:  Number of results to return (falls back to settings.TOP_K_RETRIEVAL).

        Returns
        -------
        List of RRF-ranked dicts with:
            chunk_id, content, metadata, rrf_score, found_by
        """
        if not query.strip():
            logger.warning("HybridRetriever.retrieve() received an empty query.")
            return []

        # Validate domain
        if domain not in VALID_DOMAINS:
            logger.warning(
                "Unknown domain '%s' — falling back to 'all'.",
                domain,
            )
            domain = "all"

        k = top_k if top_k is not None else settings.TOP_K_RETRIEVAL
        domain_filter = None if domain == "all" else domain

        start = time.perf_counter()

        vector_results = self._vector.search(query, top_k=k, domain_filter=domain_filter)
        bm25_results = self._bm25.search(query, top_k=k, domain_filter=domain_filter)

        fused = self._rrf.fuse(vector_results, bm25_results)
        top_results = fused[:k]

        elapsed_ms = (time.perf_counter() - start) * 1_000
        logger.info(
            "HybridRetriever: query='%s…' | domain=%s | returned %d results in %.1f ms.",
            query[:50],
            domain,
            len(top_results),
            elapsed_ms,
        )

        return top_results

    # ------------------------------------------------------------------

    def get_stats(self) -> dict:
        """
        Return basic index statistics.

        Returns
        -------
        {
            "total_chunks": int,
            "domains": {"tax": int, "finance": int, "legal": int}
        }
        """
        import chromadb  # local import — avoids duplicate client at module level

        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        try:
            col = client.get_collection("legal_finance_docs")
        except Exception:
            return {"total_chunks": 0, "domains": {}}

        total = col.count()
        domains: dict[str, int] = {}
        for domain in ("tax", "finance", "legal"):
            try:
                res = col.get(where={"domain": {"$eq": domain}}, include=[])
                domains[domain] = len(res["ids"])
            except Exception:
                domains[domain] = 0

        return {"total_chunks": total, "domains": domains}
