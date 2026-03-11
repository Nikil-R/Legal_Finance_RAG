"""
Ingestion Pipeline Orchestrator — ties together loading, chunking, and embedding.

Usage (from project root):
    from app.ingestion.pipeline import run_ingestion_pipeline
    summary = run_ingestion_pipeline()
"""

from __future__ import annotations

import time
from collections import Counter

from app.config import settings
from app.ingestion.chunker import DocumentChunker
from app.ingestion.embedder import VectorStoreManager
from app.ingestion.loader import DocumentLoader
from app.utils.logger import get_logger

logger = get_logger(__name__)

RAW_DATA_DIR = "data/core"


def run_ingestion_pipeline(
    *,
    raw_dir: str = RAW_DATA_DIR,
    clear_existing: bool = False,
) -> dict:
    """
    Run the full ingestion pipeline end-to-end.

    Steps
    -----
    1. Load all documents from *raw_dir*.
    2. Chunk every document.
    3. Embed chunks and store them in ChromaDB.

    Parameters
    ----------
    raw_dir:
        Path to the root data directory (default: ``data/raw``).
    clear_existing:
        When ``True`` the ChromaDB collection is wiped before ingestion.

    Returns
    -------
    dict with keys:
        ``documents_loaded``, ``chunks_created``, ``chunks_stored``,
        ``domain_breakdown`` (Counter).
    """
    t_pipeline_start = time.time()

    logger.info("=" * 60)
    logger.info("Starting LegalFinance RAG ingestion pipeline …")
    logger.info("  raw_dir        : %s", raw_dir)
    logger.info("  clear_existing : %s", clear_existing)
    logger.info("=" * 60)

    # ── 1. Load ──────────────────────────────────────────────────────
    t0 = time.time()
    loader = DocumentLoader()
    documents = loader.load_directory(raw_dir)
    t_load = time.time() - t0
    logger.info("⏱  STAGE 1 — Load: %.1fs | %d doc(s)", t_load, len(documents))

    if not documents:
        logger.warning("No documents found in '%s'. Pipeline aborted.", raw_dir)
        return {
            "documents_loaded": 0,
            "chunks_created": 0,
            "chunks_stored": 0,
            "domain_breakdown": {},
        }

    # ── 2. Chunk ─────────────────────────────────────────────────────
    t0 = time.time()
    chunker = DocumentChunker(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    chunks = chunker.chunk_all(documents)
    t_chunk = time.time() - t0
    logger.info("⏱  STAGE 2 — Chunk: %.1fs | %d chunk(s)", t_chunk, len(chunks))

    # ── 3. Embed & Store ─────────────────────────────────────────────
    t0 = time.time()
    vsm = VectorStoreManager(
        persist_dir=settings.CHROMA_PERSIST_DIR,
        embedding_model=settings.EMBEDDING_MODEL,
    )

    if clear_existing:
        vsm.clear_collection()

    stored = vsm.embed_and_store(chunks)
    t_embed = time.time() - t0
    logger.info("⏱  STAGE 3 — Embed+Store: %.1fs | %d chunk(s) stored", t_embed, stored)

    # ── 4. Summary ───────────────────────────────────────────────────
    domain_breakdown = dict(Counter(c["metadata"]["domain"] for c in chunks))
    t_total = time.time() - t_pipeline_start

    logger.info("=" * 60)
    logger.info("Ingestion pipeline complete.")
    logger.info("  Documents loaded  : %d  (%.1fs)", len(documents), t_load)
    logger.info("  Chunks created    : %d  (%.1fs)", len(chunks), t_chunk)
    logger.info("  Chunks stored     : %d  (%.1fs)", stored, t_embed)
    logger.info("  Domain breakdown  : %s", domain_breakdown)
    logger.info("  ⏱  TOTAL TIME    : %.1fs (%.1f min)", t_total, t_total / 60)
    logger.info("=" * 60)

    return {
        "documents_loaded": len(documents),
        "chunks_created": len(chunks),
        "chunks_stored": stored,
        "domain_breakdown": domain_breakdown,
    }
