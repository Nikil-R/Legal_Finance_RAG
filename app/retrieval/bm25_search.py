"""
BM25 Keyword Search — builds a BM25Okapi index from ChromaDB-stored chunks on demand.

The index is (re)built from whatever is currently in ChromaDB so it is always
consistent with the vector store, even after re-ingestion.
"""

from __future__ import annotations

import re

import chromadb
import numpy as np
from rank_bm25 import BM25Okapi

from app.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "legal_finance_docs"
VALID_DOMAINS = {"tax", "finance", "legal"}

# Minimum token length to keep during tokenisation
_MIN_TOKEN_LEN = 2


class BM25Retriever:
    """Sparse retriever: builds a BM25 index over ChromaDB chunks and scores them."""

    def __init__(
        self, persist_dir: str, collection_name: str = COLLECTION_NAME
    ) -> None:
        logger.info("BM25Retriever: connecting to ChromaDB at '%s' …", persist_dir)
        client = chromadb.PersistentClient(path=persist_dir)
        self.collection_name = collection_name

        try:
            self._collection = client.get_collection(name=self.collection_name)
        except Exception as e:
            raise RuntimeError(
                f"ChromaDB collection '{self.collection_name}' not found. "
                "Please run the ingestion pipeline first:\n"
                "  python -m app.ingestion.cli"
            ) from e

        logger.info(
            "BM25Retriever ready (%d chunks available in '%s').",
            self._collection.count(),
            self.collection_name,
        )

        # These are populated by _build_index()
        self._corpus_tokens: list[list[str]] = []
        self._corpus_ids: list[str] = []
        self._corpus_texts: list[str] = []
        self._corpus_metadatas: list[dict] = []
        self._bm25: BM25Okapi | None = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Lowercase, split on non-alphanumeric chars, remove short tokens."""
        tokens = re.split(r"[^a-zA-Z0-9]", text.lower())
        return [t for t in tokens if len(t) >= _MIN_TOKEN_LEN]

    # ------------------------------------------------------------------
    # Index building
    # ------------------------------------------------------------------

    def _build_index(self, domain_filter: str | None = None) -> None:
        """
        Fetch all (filtered) documents from ChromaDB and build a BM25Okapi index.

        Called before every search so the index stays in sync with the store.
        """
        where: dict | None = None
        if domain_filter and domain_filter in VALID_DOMAINS:
            where = {"domain": {"$eq": domain_filter}}

        # get() with no ids fetches everything; limit is ChromaDB's internal max
        raw = self._collection.get(
            where=where,
            include=["documents", "metadatas"],
        )

        ids: list[str] = raw["ids"]
        texts: list[str] = raw["documents"]
        metadatas: list[dict] = raw["metadatas"]

        if not texts:
            logger.warning(
                "BM25Retriever: no documents found in collection (filter=%s).",
                domain_filter,
            )
            self._corpus_tokens = []
            self._corpus_ids = []
            self._corpus_texts = []
            self._corpus_metadatas = []
            self._bm25 = None
            return

        self._corpus_tokens = [self._tokenize(t) for t in texts]
        self._corpus_ids = ids
        self._corpus_texts = texts
        self._corpus_metadatas = [dict(m) for m in metadatas]
        self._bm25 = BM25Okapi(self._corpus_tokens)

        logger.debug(
            "BM25 index built: %d documents (filter=%s).",
            len(texts),
            domain_filter,
        )

    # ------------------------------------------------------------------
    # Public search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 20,
        domain_filter: str | None = None,
    ) -> list[dict]:
        """
        Score all indexed documents against *query* and return the *top_k* best.

        Parameters
        ----------
        query:         Natural-language question.
        top_k:         Maximum number of results to return.
        domain_filter: One of "tax", "finance", "legal", or None (no filter).

        Returns
        -------
        List of result dicts with keys:
            chunk_id, content, metadata, score (raw BM25 float), source="bm25"
        """
        if not query.strip():
            logger.warning("BM25Retriever.search() called with an empty query.")
            return []

        # Rebuild index for this domain (cheap for small corpora)
        self._build_index(domain_filter=domain_filter)

        if self._bm25 is None:
            return []

        tokenized_query = self._tokenize(query)
        scores: np.ndarray = self._bm25.get_scores(tokenized_query)

        # Clamp to available corpus size
        k = min(top_k, len(scores))
        # argsort ascending → take last k (highest scores)
        top_indices: np.ndarray = np.argsort(scores)[::-1][:k]

        results: list[dict] = []
        for idx in top_indices:
            raw_score = float(scores[idx])  # convert numpy float → Python float
            if raw_score <= 0.0:
                continue  # skip documents with no BM25 relevance
            results.append(
                {
                    "chunk_id": self._corpus_ids[idx],
                    "content": self._corpus_texts[idx],
                    "metadata": self._corpus_metadatas[idx],
                    "score": raw_score,
                    "source": "bm25",
                }
            )

        logger.info(
            "BM25 search returned %d results for query: '%s…'",
            len(results),
            query[:50],
        )
        return results
