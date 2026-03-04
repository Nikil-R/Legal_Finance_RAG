"""
Vector Similarity Search — queries ChromaDB using SentenceTransformer embeddings.
"""

from __future__ import annotations

import chromadb
from sentence_transformers import SentenceTransformer

from app.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "legal_finance_docs"
VALID_DOMAINS = {"tax", "finance", "legal"}


class VectorRetriever:
    """Dense retriever: embeds a query and fetches nearest neighbours from ChromaDB."""

    def __init__(
        self,
        persist_dir: str,
        embedding_model: str,
        collection_name: str = COLLECTION_NAME,
    ) -> None:
        logger.info("VectorRetriever: loading embedding model '%s' …", embedding_model)
        self._encoder = SentenceTransformer(embedding_model)

        logger.info("VectorRetriever: connecting to ChromaDB at '%s' …", persist_dir)
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
            "VectorRetriever ready (%d chunks indexed in '%s').",
            self._collection.count(),
            self.collection_name,
        )

    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 20,
        domain_filter: str | None = None,
    ) -> list[dict]:
        """
        Embed *query* and return the *top_k* most similar chunks.

        Parameters
        ----------
        query:         Natural-language question.
        top_k:         Maximum number of results to return.
        domain_filter: One of "tax", "finance", "legal", or None (no filter).

        Returns
        -------
        List of result dicts with keys:
            chunk_id, content, metadata, score (float in (0, 1]), source="vector"
        """
        if not query.strip():
            logger.warning("VectorRetriever.search() called with an empty query.")
            return []

        # Embed the query
        query_embedding = self._encoder.encode(query, show_progress_bar=False).tolist()

        # Build optional metadata filter
        where: dict | None = None
        if domain_filter and domain_filter in VALID_DOMAINS:
            where = {"domain": {"$eq": domain_filter}}

        # ChromaDB requires n_results <= collection size
        n_results = min(top_k, self._collection.count())
        if n_results == 0:
            return []

        raw = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        ids = raw["ids"][0]
        documents = raw["documents"][0]
        metadatas = raw["metadatas"][0]
        distances = raw["distances"][0]

        results: list[dict] = []
        for chunk_id, content, metadata, distance in zip(
            ids, documents, metadatas, distances, strict=False
        ):
            # Convert chromadb cosine distance [0, 2] → similarity score (0, 1]
            score = float(1.0 / (1.0 + distance))
            results.append(
                {
                    "chunk_id": chunk_id,
                    "content": content,
                    "metadata": dict(metadata),
                    "score": score,
                    "source": "vector",
                }
            )

        logger.info(
            "Vector search returned %d results for query: '%s…'",
            len(results),
            query[:50],
        )
        return results
