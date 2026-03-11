"""
Cross-Encoder Re-ranker — scores (query, chunk) pairs for deep relevance ranking.

Uses sentence-transformers CrossEncoder (ms-marco-MiniLM-L-6-v2 by default),
which jointly encodes query + passage and produces a single relevance score.
"""

from __future__ import annotations

import time

from sentence_transformers import CrossEncoder

from app.utils.logger import get_logger

logger = get_logger(__name__)


class CrossEncoderReranker:
    """
    Re-ranks candidate chunks using a cross-encoder model.

    Unlike bi-encoders (used for vector search), a cross-encoder sees the
    full (query, document) pair together, giving much higher relevance accuracy
    at the cost of speed.
    """

    def __init__(self, model_name: str | None = None) -> None:
        if model_name is None:
            from app.config import settings

            model_name = settings.CROSS_ENCODER_MODEL

        self.model_name = model_name
        logger.info("Loading cross-encoder model: '%s' …", model_name)
        self._model = CrossEncoder(model_name, device="cpu")
        logger.info("Cross-encoder model loaded.")

    # ------------------------------------------------------------------

    def rerank(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 5,
    ) -> list[dict]:
        """
        Score every (query, candidate) pair and return the *top_k* best.

        Parameters
        ----------
        query:      Natural-language question.
        candidates: Chunks from hybrid retrieval (each must have "content").
        top_k:      Maximum results to return.

        Returns
        -------
        Candidates with an added ``rerank_score`` (float) field, sorted
        descending. If ``len(candidates) <= top_k`` all are returned.
        """
        if not candidates:
            return []

        logger.info(
            "Re-ranking %d candidates for query: '%s…'",
            len(candidates),
            query[:50],
        )

        t0 = time.perf_counter()

        pairs = [[query, c["content"]] for c in candidates]
        raw_scores = self._model.predict(pairs)  # numpy array

        # Attach Python-native float scores
        scored: list[dict] = []
        for candidate, raw in zip(candidates, raw_scores, strict=False):
            scored.append({**candidate, "rerank_score": float(raw)})

        # Sort descending by rerank_score
        scored.sort(key=lambda x: x["rerank_score"], reverse=True)

        top = scored[:top_k]

        elapsed = time.perf_counter() - t0
        top3_scores = [round(r["rerank_score"], 4) for r in top[:3]]
        logger.info("Top rerank scores: %s", top3_scores)
        logger.info("Re-ranking completed in %.2fs.", elapsed)

        return top

    # ------------------------------------------------------------------

    def rerank_with_threshold(
        self,
        query: str,
        candidates: list[dict],
        top_k: int = 5,
        min_score: float = 0.1,
    ) -> list[dict]:
        """
        Like :meth:`rerank`, but additionally filters out candidates whose
        ``rerank_score`` is below *min_score*.

        Parameters
        ----------
        min_score: Minimum cross-encoder score to keep (default 0.1).
                   Cross-encoder scores roughly range from -10 to +10;
                   positive values indicate genuine relevance.

        Returns
        -------
        Top-*top_k* candidates that pass the threshold, sorted descending.
        Empty list if nothing passes.
        """
        reranked = self.rerank(query, candidates, top_k=len(candidates) or top_k)

        filtered = [r for r in reranked if r["rerank_score"] >= min_score]

        if not filtered:
            logger.warning(
                "No candidates passed minimum score threshold of %.2f (best was %.4f).",
                min_score,
                reranked[0]["rerank_score"] if reranked else float("nan"),
            )

        return filtered[:top_k]
