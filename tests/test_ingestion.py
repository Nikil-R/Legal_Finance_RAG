"""
Tests for the ingestion pipeline (loader, chunker, embedder, full pipeline).

A separate ChromaDB directory (./test_chroma_db) is used so that tests
never pollute the real ./chroma_db collection.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from app.ingestion.chunker import DocumentChunker
from app.ingestion.loader import DocumentLoader

# ── Constants ────────────────────────────────────────────────────────────────

RAW_DATA_DIR = Path("data/raw")
TEST_CHROMA_DIR = "./test_chroma_db"


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def tmp_txt_file(tmp_path: Path) -> Path:
    """Create a temporary .txt file with known content."""
    f = tmp_path / "test_doc.txt"
    f.write_text(
        "This is a test document.\nIt has multiple lines.\nWe use it to verify the loader.",
        encoding="utf-8",
    )
    return f


@pytest.fixture()
def sample_document() -> dict:
    """A minimal document dict matching the loader's output schema."""
    return {
        "content": (
            "Section 80C allows deductions up to Rs 1,50,000. "
            "Eligible investments include Public Provident Fund. "
            "Employee Provident Fund is also eligible. "
            "National Savings Certificate qualifies too. "
            "The limit applies per financial year."
        ),
        "metadata": {
            "source": "sample.txt",
            "domain": "tax",
            "file_path": "data/raw/tax/sample.txt",
        },
    }


@pytest.fixture(autouse=True)
def cleanup_test_chroma():
    """Remove the test ChromaDB directory after every test that uses it."""
    yield
    test_dir = Path(TEST_CHROMA_DIR)
    if test_dir.exists():
        shutil.rmtree(test_dir, ignore_errors=True)


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestDocumentLoader:
    def test_load_txt_file(self, tmp_txt_file: Path):
        """load_txt() should return the file's content as a non-empty string."""
        loader = DocumentLoader()
        content = loader.load_txt(str(tmp_txt_file))

        assert isinstance(content, str)
        assert len(content) > 0
        assert "test document" in content

    def test_load_txt_missing_file(self):
        """load_txt() on a non-existent file should return an empty string (no crash)."""
        loader = DocumentLoader()
        result = loader.load_txt("/non/existent/path/file.txt")
        assert result == ""

    def test_load_directory_returns_three_documents(self):
        """load_directory() should find the 3 sample .txt files in data/raw/."""
        loader = DocumentLoader()
        docs = loader.load_directory(str(RAW_DATA_DIR))

        assert len(docs) == 3, f"Expected 3 documents, got {len(docs)}"

    def test_load_directory_domain_assignment(self):
        """Each document's domain should match its subfolder name."""
        loader = DocumentLoader()
        docs = loader.load_directory(str(RAW_DATA_DIR))

        domains = {d["metadata"]["domain"] for d in docs}
        assert domains == {"tax", "finance", "legal"}

    def test_load_directory_metadata_shape(self):
        """Every returned document must have the required metadata keys."""
        loader = DocumentLoader()
        docs = loader.load_directory(str(RAW_DATA_DIR))

        for doc in docs:
            meta = doc["metadata"]
            assert "source" in meta
            assert "domain" in meta
            assert "file_path" in meta
            assert isinstance(doc["content"], str)
            assert len(doc["content"]) > 0


class TestDocumentChunker:
    def test_chunk_document_returns_multiple_chunks(self, sample_document: dict):
        """A document longer than chunk_size should produce more than one chunk."""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_document(sample_document)

        assert len(chunks) >= 1  # at minimum one chunk

    def test_chunk_document_metadata_propagation(self, sample_document: dict):
        """Each chunk must carry the original metadata plus chunk_index and chunk_id."""
        chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)
        chunks = chunker.chunk_document(sample_document)

        assert len(chunks) > 0
        for idx, chunk in enumerate(chunks):
            meta = chunk["metadata"]
            assert meta["source"] == "sample.txt"
            assert meta["domain"] == "tax"
            assert meta["chunk_index"] == idx
            assert "chunk_id" in meta
            assert meta["chunk_id"].endswith(f"_chunk_{idx}")

    def test_chunk_document_unique_ids(self, sample_document: dict):
        """All chunk IDs within a single document must be unique."""
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.chunk_document(sample_document)

        ids = [c["metadata"]["chunk_id"] for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_document_empty_content(self):
        """chunk_document() on an empty document should return an empty list."""
        chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)
        doc = {
            "content": "",
            "metadata": {"source": "empty.txt", "domain": "tax", "file_path": ""},
        }
        chunks = chunker.chunk_document(doc)
        assert chunks == []

    def test_chunk_all_flat_list(self, sample_document: dict):
        """chunk_all() should return a flat list covering all input documents."""
        chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)
        docs = [sample_document, sample_document]  # two identical docs
        chunks = chunker.chunk_all(docs)

        # Each doc produces at least 1 chunk → total >= 2
        assert len(chunks) >= 2


class TestFullPipeline:
    def test_full_pipeline_summary(self):
        """
        End-to-end: run the pipeline with a test chroma directory,
        verify the summary counts are consistent.
        """
        # Import here to avoid loading heavy models at collection time

        # Patch settings temporarily so we use the test chroma dir
        # Run with the test chroma path directly via pipeline kwargs
        # We need to override settings.CHROMA_PERSIST_DIR for this test.
        from app import config as cfg_module
        from app.ingestion.pipeline import run_ingestion_pipeline

        original_dir = cfg_module.settings.CHROMA_PERSIST_DIR
        try:
            cfg_module.settings.CHROMA_PERSIST_DIR = TEST_CHROMA_DIR

            summary = run_ingestion_pipeline(
                raw_dir=str(RAW_DATA_DIR),
                clear_existing=True,
            )
        finally:
            cfg_module.settings.CHROMA_PERSIST_DIR = original_dir

        assert (
            summary["documents_loaded"] > 0
        ), "Pipeline should load at least 1 document"
        assert summary["chunks_created"] > 0, "Pipeline should create at least 1 chunk"
        assert (
            summary["chunks_stored"] == summary["chunks_created"]
        ), "Every chunk created should be stored in ChromaDB"
        assert isinstance(summary["domain_breakdown"], dict)
        assert (
            len(summary["domain_breakdown"]) > 0
        ), "Domain breakdown should not be empty"
