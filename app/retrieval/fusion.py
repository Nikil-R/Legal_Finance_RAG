"""
Reciprocal Rank Fusion (RRF) — merges vector and BM25 result lists.

Formula
-------
    RRF_score(d) = Σ  1 / (k + rank_in_list_i)

where the sum is over every list that contains document d,
and rank is 1-based.

Key property: a document appearing in BOTH lists gets contributions from
two terms and therefore rises above documents found by only one method.
"""

from __future__ import annotations

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Standard RRF constant (Cormack et al., 2009)
DEFAULT_K = 60


class RRFusion:
    """Fuses ranked lists from multiple retrievers using Reciprocal Rank Fusion."""

    def __init__(self, k: int = DEFAULT_K) -> None:
        self._k = k

    # ------------------------------------------------------------------

    def fuse(
        self,
        vector_results: list[dict],
        bm25_results: list[dict],
    ) -> list[dict]:
        """
        Merge *vector_results* and *bm25_results* via RRF.

        Each input list must contain dicts with at least:
            chunk_id, content, metadata, score, source

        Returns a combined, re-ranked list of dicts with keys:
            chunk_id, content, metadata, rrf_score (float), found_by (str)
        """
        # accumulated RRF scores keyed by chunk_id
        rrf_scores: dict[str, float] = {}
        # for deduplication: keep the best content+metadata per chunk_id
        payload: dict[str, dict] = {}
        # track which lists contain each chunk
        sources: dict[str, set[str]] = {}

        def _accumulate(result_list: list[dict], list_name: str) -> None:
            for rank_0, item in enumerate(result_list):
                cid = item["chunk_id"]
                rrf_increment = 1.0 / (self._k + rank_0 + 1)  # rank is 1-based
                rrf_scores[cid] = rrf_scores.get(cid, 0.0) + rrf_increment
                sources.setdefault(cid, set()).add(list_name)
                if cid not in payload:
                    payload[cid] = {
                        "chunk_id": cid,
                        "content": item["content"],
                        "metadata": item["metadata"],
                    }

        _accumulate(vector_results, "vector")
        _accumulate(bm25_results, "bm25")

        # Sort by accumulated RRF score (descending)
        ranked_ids = sorted(rrf_scores, key=lambda cid: rrf_scores[cid], reverse=True)

        # Build output list
        fused: list[dict] = []
        for cid in ranked_ids:
            src_set = sources[cid]
            if "vector" in src_set and "bm25" in src_set:
                found_by = "both"
            elif "vector" in src_set:
                found_by = "vector"
            else:
                found_by = "bm25"

            fused.append(
                {
                    **payload[cid],
                    "rrf_score": float(rrf_scores[cid]),
                    "found_by": found_by,
                }
            )

        # Log breakdown
        n_vector_only = sum(1 for s in sources.values() if s == {"vector"})
        n_bm25_only = sum(1 for s in sources.values() if s == {"bm25"})
        n_both = sum(1 for s in sources.values() if len(s) == 2)
        logger.info(
            "RRF fusion: %d from vector only, %d from BM25 only, %d from both → %d total.",
            n_vector_only,
            n_bm25_only,
            n_both,
            len(fused),
        )

        return fused
