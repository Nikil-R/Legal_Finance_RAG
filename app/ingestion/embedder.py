"""
Embedder & Vector Store Manager — generates embeddings and persists them in ChromaDB.

Uses SentenceTransformer directly so we own the embedding step and can swap
models without touching ChromaDB's embedding-function interface.
"""

from __future__ import annotations

import math

import chromadb
from sentence_transformers import SentenceTransformer

from app.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "legal_finance_docs"
DEFAULT_BATCH_SIZE = 100


class VectorStoreManager:
    """Manages embedding generation and ChromaDB storage for document chunks."""

    def __init__(
        self,
        persist_dir: str,
        embedding_model: str,
        collection_name: str = COLLECTION_NAME,
    ) -> None:
        logger.info("Loading embedding model '%s' …", embedding_model)
        self._encoder = SentenceTransformer(embedding_model)

        logger.info("Connecting to ChromaDB at '%s' …", persist_dir)
        self._client = chromadb.PersistentClient(path=persist_dir)
        self.collection_name = collection_name
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            "Collection '%s' ready (%d existing document(s)).",
            self.collection_name,
            self._collection.count(),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_and_store(
        self, chunks: list[dict], batch_size: int = DEFAULT_BATCH_SIZE
    ) -> int:
        """
        Embed *chunks* and upsert them into ChromaDB.

        Processes in batches to keep memory usage bounded.
        Returns the total number of chunks stored.
        """
        if not chunks:
            logger.warning("No chunks provided to embed_and_store(); nothing to do.")
            return 0

        total = len(chunks)
        num_batches = math.ceil(total / batch_size)
        stored = 0

        for batch_num in range(num_batches):
            start = batch_num * batch_size
            end = min(start + batch_size, total)
            batch = chunks[start:end]

            texts = [c["content"] for c in batch]
            ids = [c["metadata"]["chunk_id"] for c in batch]
            metadatas = [c["metadata"] for c in batch]

            logger.info(
                "Embedding batch %d/%d (%d chunks) …",
                batch_num + 1,
                num_batches,
                len(batch),
            )
            embeddings = self._encoder.encode(texts, show_progress_bar=False).tolist()

            self._collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            stored += len(batch)
            logger.info(
                "Batch %d/%d stored. Running total: %d.",
                batch_num + 1,
                num_batches,
                stored,
            )

        return stored

    def get_collection_count(self) -> int:
        """Return the number of documents currently in the collection."""
        return self._collection.count()

    def clear_collection(self) -> None:
        """Delete and recreate the collection (for a clean re-ingestion)."""
        logger.warning("Clearing collection '%s' …", self.collection_name)
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("Collection '%s' recreated (empty).", self.collection_name)
