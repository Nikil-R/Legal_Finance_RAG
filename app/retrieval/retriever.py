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
        from app.retrieval.user_retriever import UserDocumentRetriever

        self._user_retriever = UserDocumentRetriever()
        self._rrf = RRFusion(k=60)
        logger.info("HybridRetriever ready.")

    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        domain: str = "all",
        top_k: int | None = None,
        session_id: str | None = None,
        owner_id: str | None = None,
    ) -> list[dict]:
        """
        Run hybrid retrieval and return re-ranked results.
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

        # System Search
        vector_results = self._vector.search(
            query, top_k=k, domain_filter=domain_filter
        )
        bm25_results = self._bm25.search(query, top_k=k, domain_filter=domain_filter)

        # Mark system results
        for r in vector_results:
            r["origin"] = "system"
        for r in bm25_results:
            r["origin"] = "system"

        # User Search
        user_vector_results = []
        user_bm25_results = []
        if session_id:
            user_results = self._user_retriever.search(
                query,
                session_id=session_id,
                owner_id=owner_id,
                top_k=k,
            )
            # user_results is a combined list, need to separate for RRF if possible
            # or just add them to the system lists
            user_vector_results = [
                r for r in user_results if r.get("source") == "vector"
            ]
            user_bm25_results = [r for r in user_results if r.get("source") == "bm25"]

        # Merge results for RRF fusion
        all_vector = vector_results + user_vector_results
        all_bm25 = bm25_results + user_bm25_results

        # Sort merged lists by their own scores before RRF
        # This prevents the appended user results from being penalized by their position
        all_vector.sort(key=lambda x: x.get("score", 0), reverse=True)
        all_bm25.sort(key=lambda x: x.get("score", 0), reverse=True)

        fused = self._rrf.fuse(all_vector, all_bm25)
        top_results = fused[:k]

        elapsed_ms = (time.perf_counter() - start) * 1_000
        logger.info(
            "HybridRetriever: query='%s…' | domain=%s | session=%s | results=%d | time=%.1fms.",
            query[:50],
            domain,
            session_id,
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
