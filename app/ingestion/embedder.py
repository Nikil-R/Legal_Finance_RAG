"""
Embedder & Vector Store Manager — generates embeddings and persists them in ChromaDB.

Uses SentenceTransformer directly so we own the embedding step and can swap
models without touching ChromaDB's embedding-function interface.
"""

from __future__ import annotations

import math
import time

import chromadb

from app.utils.lightweight_models import load_sentence_encoder
from app.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "legal_finance_docs"

# Optimal batch size for CPU-based sentence-transformers on Windows.
# 256 balances memory usage and throughput. Do NOT use multiprocessing
# pools on Windows — the IPC serialization overhead makes it slower.
EMBED_BATCH_SIZE = 256

# ChromaDB upsert batch — keep ≤ 500 to avoid memory spikes on large corpora
CHROMA_BATCH_SIZE = 500


class VectorStoreManager:
    """Manages embedding generation and ChromaDB storage for document chunks."""

    def __init__(
        self,
        persist_dir: str,
        embedding_model: str,
        collection_name: str = COLLECTION_NAME,
    ) -> None:
        logger.info("Loading embedding model '%s' …", embedding_model)
        t0 = time.time()
        # device="cpu" is explicit — avoids a slow CUDA probe on machines without GPU.
        # If you have an NVIDIA GPU: change to device="cuda" for 10-20x speedup.
        self._encoder = load_sentence_encoder(
            embedding_model,
            device="cpu",
            logger=logger,
        )
        logger.info("Embedding model loaded in %.1fs.", time.time() - t0)

        logger.info("Connecting to ChromaDB at '%s' …", persist_dir)
        self._client = chromadb.PersistentClient(path=persist_dir)
        self.collection_name = collection_name
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self._collection_is_fresh = False  # Set to True after clear_collection()
        logger.info(
            "Collection '%s' ready (%d existing document(s)).",
            self.collection_name,
            self._collection.count(),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_and_store(
        self,
        chunks: list[dict],
        skip_existing: bool = True,
    ) -> int:
        """
        Embed *chunks* and upsert them into ChromaDB.

        Processes in batches to keep memory usage bounded.
        Returns the total number of chunks stored.
        """
        if not chunks:
            logger.warning("No chunks provided to embed_and_store(); nothing to do.")
            return 0

        # Skip the expensive get-all-IDs call if collection was just cleared —
        # it's empty by definition so no deduplication is needed.
        if skip_existing and not self._collection_is_fresh:
            logger.info("Checking for existing chunks to skip...")
            t_check = time.time()
            existing_ids = set(self._collection.get(include=[])["ids"])
            logger.info(
                "Existing ID check done in %.1fs. Found %d existing chunks.",
                time.time() - t_check,
                len(existing_ids),
            )
            chunks = [c for c in chunks if c["metadata"]["chunk_id"] not in existing_ids]
            logger.info("Remaining chunks to process after dedup: %d", len(chunks))
        else:
            if self._collection_is_fresh:
                logger.info("Collection is freshly cleared — skipping dedup check.")

        total = len(chunks)
        if total == 0:
            logger.info("All chunks already exist in DB. Nothing to store.")
            return 0

        logger.info(
            "Starting embedding + storage of %d chunks "
            "(embed_batch=%d, chroma_batch=%d) …",
            total, EMBED_BATCH_SIZE, CHROMA_BATCH_SIZE,
        )

        t_total_start = time.time()
        stored = 0
        num_embed_batches = math.ceil(total / EMBED_BATCH_SIZE)

        for batch_num in range(num_embed_batches):
            start = batch_num * EMBED_BATCH_SIZE
            end = min(start + EMBED_BATCH_SIZE, total)
            batch = chunks[start:end]

            texts = [c["content"] for c in batch]
            ids = [c["metadata"]["chunk_id"] for c in batch]
            metadatas = [c["metadata"] for c in batch]

            # --- Embed ---
            t_embed = time.time()
            embeddings = self._encoder.encode(
                texts,
                batch_size=EMBED_BATCH_SIZE,
                show_progress_bar=False,
                normalize_embeddings=True,   # cosine similarity — no L2 norm step later
                convert_to_numpy=True,
            ).tolist()
            embed_ms = (time.time() - t_embed) * 1000

            # --- Store in ChromaDB in sub-batches ---
            num_chroma_batches = math.ceil(len(batch) / CHROMA_BATCH_SIZE)
            for cb in range(num_chroma_batches):
                cs = cb * CHROMA_BATCH_SIZE
                ce = min(cs + CHROMA_BATCH_SIZE, len(batch))
                self._collection.upsert(
                    ids=ids[cs:ce],
                    documents=texts[cs:ce],
                    embeddings=embeddings[cs:ce],
                    metadatas=metadatas[cs:ce],
                )
            stored += len(batch)

            elapsed_total = time.time() - t_total_start
            pct = round(stored / total * 100, 1)
            eta_s = (elapsed_total / stored) * (total - stored) if stored > 0 else 0
            logger.info(
                "Batch %d/%d | %d chunks | embed %.0fms | "
                "stored %d/%d (%.1f%%) | ETA ~%.0fs",
                batch_num + 1, num_embed_batches,
                len(batch), embed_ms,
                stored, total, pct, eta_s,
            )

        logger.info(
            "Embedding + storage complete. Total: %d chunks in %.1fs.",
            stored,
            time.time() - t_total_start,
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
        self._collection_is_fresh = True  # Signal: skip dedup on next embed_and_store
        logger.info("Collection '%s' recreated (empty).", self.collection_name)
