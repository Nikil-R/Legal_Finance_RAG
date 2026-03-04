"""
Unit tests for retrieval system.
"""

import pytest

from app.ingestion.embedder import VectorStoreManager
from app.retrieval.bm25_search import BM25Retriever
from app.retrieval.fusion import RRFusion
from app.retrieval.vector_search import VectorRetriever


class TestVectorRetriever:
    """Tests for VectorRetriever."""

    @pytest.fixture
    def populated_vector_store(self, chroma_test_dir, sample_chunks):
        """Create and populate a vector store."""
        persist_dir = str(chroma_test_dir / "retrieval_test")

        manager = VectorStoreManager(
            persist_dir=persist_dir,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        )
        manager.clear_collection()
        manager.embed_and_store(sample_chunks)

        return persist_dir

    def test_vector_search(self, populated_vector_store):
        """Test vector similarity search."""
        retriever = VectorRetriever(
            persist_dir=populated_vector_store,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        )

        results = retriever.search("Section 80C tax deductions", top_k=3)

        assert len(results) > 0
        assert all("score" in r for r in results)
        assert all("content" in r for r in results)

    def test_vector_search_with_domain_filter(self, populated_vector_store):
        """Test vector search with domain filter."""
        retriever = VectorRetriever(
            persist_dir=populated_vector_store,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        )

        results = retriever.search("deductions", top_k=5, domain_filter="tax")

        for result in results:
            assert result["metadata"]["domain"] == "tax"


class TestBM25Retriever:
    """Tests for BM25Retriever."""

    def test_bm25_search(self, chroma_test_dir, sample_chunks):
        """Test BM25 keyword search."""
        # Setup
        manager = VectorStoreManager(
            persist_dir=str(chroma_test_dir / "bm25_test"),
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        )
        manager.clear_collection()
        manager.embed_and_store(sample_chunks)

        # Test
        retriever = BM25Retriever(persist_dir=str(chroma_test_dir / "bm25_test"))
        results = retriever.search("Section 80C PPF deductions", top_k=3)

        assert len(results) > 0
        assert all("score" in r for r in results)


class TestRRFusion:
    """Tests for Reciprocal Rank Fusion."""

    def test_fusion_basic(self):
        """Test basic RRF fusion."""
        fusion = RRFusion(k=60)

        vector_results = [
            {
                "chunk_id": "a",
                "content": "A",
                "metadata": {},
                "score": 0.9,
                "source": "vector",
            },
            {
                "chunk_id": "b",
                "content": "B",
                "metadata": {},
                "score": 0.8,
                "source": "vector",
            },
        ]

        bm25_results = [
            {
                "chunk_id": "b",
                "content": "B",
                "metadata": {},
                "score": 10,
                "source": "bm25",
            },
            {
                "chunk_id": "c",
                "content": "C",
                "metadata": {},
                "score": 8,
                "source": "bm25",
            },
        ]

        fused = fusion.fuse(vector_results, bm25_results)

        # "b" appears in both, should rank higher
        assert fused[0]["chunk_id"] == "b"
        assert fused[0]["found_by"] == "both"

    def test_fusion_empty_lists(self):
        """Test fusion with empty lists."""
        fusion = RRFusion()
        result = fusion.fuse([], [])

        assert result == []

    def test_fusion_single_source(self):
        """Test fusion with only one source."""
        fusion = RRFusion()

        vector_results = [
            {
                "chunk_id": "a",
                "content": "A",
                "metadata": {},
                "score": 0.9,
                "source": "vector",
            },
        ]

        fused = fusion.fuse(vector_results, [])

        assert len(fused) == 1
        assert fused[0]["found_by"] == "vector"
