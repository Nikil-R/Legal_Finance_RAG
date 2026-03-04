"""
Tests for the hybrid retrieval system.

Prerequisites
-------------
The sample documents from Step 2 must already be ingested into ChromaDB:
    python -m app.ingestion.cli --clear

All tests use the real ChromaDB at settings.CHROMA_PERSIST_DIR so they
verify actual end-to-end behaviour with the sample corpus.
"""

from __future__ import annotations

import pytest

from app.retrieval.bm25_search import BM25Retriever
from app.retrieval.fusion import RRFusion
from app.retrieval.vector_search import VectorRetriever

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def vector_retriever():
    """Single VectorRetriever instance shared across tests (model load is expensive)."""
    from app.config import settings

    return VectorRetriever(
        persist_dir=settings.CHROMA_PERSIST_DIR,
        embedding_model=settings.EMBEDDING_MODEL,
    )


@pytest.fixture(scope="module")
def bm25_retriever():
    """Single BM25Retriever instance shared across tests."""
    from app.config import settings

    return BM25Retriever(persist_dir=settings.CHROMA_PERSIST_DIR)


# ── Vector Search Tests ───────────────────────────────────────────────────────


class TestVectorSearch:
    def test_vector_search_basic(self, vector_retriever: VectorRetriever):
        """search() should return a non-empty list for a relevant query."""
        results = vector_retriever.search("income tax deductions", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_vector_search_result_schema(self, vector_retriever: VectorRetriever):
        """Every result must have the required fields with correct types."""
        results = vector_retriever.search("income tax deductions", top_k=3)

        for r in results:
            assert "chunk_id" in r, "Missing chunk_id"
            assert "content" in r, "Missing content"
            assert "metadata" in r, "Missing metadata"
            assert "score" in r, "Missing score"
            assert "source" in r, "Missing source"
            assert r["source"] == "vector"
            assert isinstance(r["score"], float)
            assert 0.0 < r["score"] <= 1.0, f"Score out of bounds: {r['score']}"

    def test_vector_search_with_domain_filter(self, vector_retriever: VectorRetriever):
        """Results with domain_filter='tax' should all have domain='tax' in metadata."""
        results = vector_retriever.search(
            "tax deductions", top_k=10, domain_filter="tax"
        )

        assert len(results) > 0
        for r in results:
            assert (
                r["metadata"]["domain"] == "tax"
            ), f"Expected domain='tax', got '{r['metadata']['domain']}'"

    def test_vector_search_empty_query(self, vector_retriever: VectorRetriever):
        """Empty query string should return an empty list without crashing."""
        results = vector_retriever.search("", top_k=5)
        assert results == []

    def test_vector_search_scores_are_plain_floats(
        self, vector_retriever: VectorRetriever
    ):
        """Scores must be Python floats, not numpy floats (for JSON serialisability)."""
        results = vector_retriever.search("contract law", top_k=3)
        for r in results:
            assert type(r["score"]) is float, f"Expected float, got {type(r['score'])}"


# ── BM25 Search Tests ─────────────────────────────────────────────────────────


class TestBM25Search:
    def test_bm25_search_basic(self, bm25_retriever: BM25Retriever):
        """search() should return results for a keyword-rich query."""
        results = bm25_retriever.search("KYC guidelines banks", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_bm25_search_result_schema(self, bm25_retriever: BM25Retriever):
        """Every result must have the required fields."""
        results = bm25_retriever.search("KYC guidelines banks", top_k=3)

        for r in results:
            assert "chunk_id" in r
            assert "content" in r
            assert "metadata" in r
            assert "score" in r
            assert r["source"] == "bm25"
            assert isinstance(r["score"], float)

    def test_bm25_search_with_domain_filter(self, bm25_retriever: BM25Retriever):
        """Results with domain_filter='finance' should all have domain='finance'."""
        results = bm25_retriever.search("KYC banks", top_k=10, domain_filter="finance")

        assert len(results) > 0
        for r in results:
            assert (
                r["metadata"]["domain"] == "finance"
            ), f"Expected domain='finance', got '{r['metadata']['domain']}'"

    def test_bm25_empty_query(self, bm25_retriever: BM25Retriever):
        """Empty query should return an empty list without crashing."""
        results = bm25_retriever.search("", top_k=5)
        assert results == []

    def test_bm25_scores_are_plain_floats(self, bm25_retriever: BM25Retriever):
        """BM25 scores must be Python floats (numpy types break JSON serialisation)."""
        results = bm25_retriever.search("provident fund", top_k=5)
        for r in results:
            assert type(r["score"]) is float, f"Expected float, got {type(r['score'])}"


# ── RRF Fusion Tests ──────────────────────────────────────────────────────────


class TestRRFusion:
    """
    All tests use synthetic result lists so we can verify the maths precisely
    without depending on the live index.
    """

    @pytest.fixture()
    def mock_vector_results(self) -> list[dict]:
        return [
            {
                "chunk_id": "a",
                "content": "alpha",
                "metadata": {},
                "score": 0.9,
                "source": "vector",
            },
            {
                "chunk_id": "b",
                "content": "beta",
                "metadata": {},
                "score": 0.8,
                "source": "vector",
            },
            {
                "chunk_id": "c",
                "content": "gamma",
                "metadata": {},
                "score": 0.7,
                "source": "vector",
            },
        ]

    @pytest.fixture()
    def mock_bm25_results(self) -> list[dict]:
        return [
            {
                "chunk_id": "b",
                "content": "beta",
                "metadata": {},
                "score": 15.0,
                "source": "bm25",
            },
            {
                "chunk_id": "d",
                "content": "delta",
                "metadata": {},
                "score": 12.0,
                "source": "bm25",
            },
            {
                "chunk_id": "a",
                "content": "alpha",
                "metadata": {},
                "score": 10.0,
                "source": "bm25",
            },
        ]

    # RRF scores (k=60, 1-based rank):
    # a: 1/61 + 1/63 ≈ 0.03226   (rank 1 in vector, rank 3 in bm25)
    # b: 1/62 + 1/61 ≈ 0.03252   (rank 2 in vector, rank 1 in bm25)  ← highest
    # c: 1/63         ≈ 0.01587
    # d: 1/62         ≈ 0.01613

    def test_rrf_b_ranked_highest(self, mock_vector_results, mock_bm25_results):
        """'b' appears at rank 2 (vector) and rank 1 (BM25) → should be #1 overall."""
        fused = RRFusion(k=60).fuse(mock_vector_results, mock_bm25_results)
        assert (
            fused[0]["chunk_id"] == "b"
        ), f"Expected 'b' at rank 1, got '{fused[0]['chunk_id']}'"

    def test_rrf_a_ranked_second(self, mock_vector_results, mock_bm25_results):
        """'a' appears at rank 1 (vector) and rank 3 (BM25) → should be #2 overall."""
        fused = RRFusion(k=60).fuse(mock_vector_results, mock_bm25_results)
        assert (
            fused[1]["chunk_id"] == "a"
        ), f"Expected 'a' at rank 2, got '{fused[1]['chunk_id']}'"

    def test_rrf_found_by_both(self, mock_vector_results, mock_bm25_results):
        """Documents 'a' and 'b' appear in both lists → found_by='both'."""
        fused = RRFusion(k=60).fuse(mock_vector_results, mock_bm25_results)
        fused_map = {r["chunk_id"]: r for r in fused}

        assert fused_map["a"]["found_by"] == "both"
        assert fused_map["b"]["found_by"] == "both"

    def test_rrf_found_by_single_source(self, mock_vector_results, mock_bm25_results):
        """'c' is vector-only; 'd' is BM25-only."""
        fused = RRFusion(k=60).fuse(mock_vector_results, mock_bm25_results)
        fused_map = {r["chunk_id"]: r for r in fused}

        assert fused_map["c"]["found_by"] == "vector"
        assert fused_map["d"]["found_by"] == "bm25"

    def test_rrf_scores_are_floats(self, mock_vector_results, mock_bm25_results):
        """rrf_score must be a plain Python float."""
        fused = RRFusion(k=60).fuse(mock_vector_results, mock_bm25_results)
        for r in fused:
            assert type(r["rrf_score"]) is float

    def test_rrf_empty_inputs(self):
        """Both empty inputs should return an empty list."""
        fused = RRFusion().fuse([], [])
        assert fused == []

    def test_rrf_one_empty_input(self, mock_vector_results):
        """One empty list should return only the non-empty list's entries."""
        fused = RRFusion().fuse(mock_vector_results, [])
        assert len(fused) == len(mock_vector_results)
        for r in fused:
            assert r["found_by"] == "vector"


# ── Hybrid Retriever Integration Tests ───────────────────────────────────────


class TestHybridRetriever:
    @pytest.fixture(scope="class")
    def retriever(self):
        from app.retrieval.retriever import HybridRetriever

        return HybridRetriever()

    def test_hybrid_retriever_returns_results(self, retriever):
        """retrieve() should return a non-empty list for a relevant query."""
        results = retriever.retrieve("Section 80C tax deductions PPF", top_k=5)

        assert isinstance(results, list)
        assert len(results) > 0

    def test_hybrid_retriever_result_schema(self, retriever):
        """Every result must have rrf_score and found_by fields."""
        results = retriever.retrieve("Section 80C tax deductions PPF", top_k=3)

        for r in results:
            assert "chunk_id" in r
            assert "content" in r
            assert "metadata" in r
            assert "rrf_score" in r
            assert "found_by" in r
            assert type(r["rrf_score"]) is float
            assert r["found_by"] in {"vector", "bm25", "both"}

    def test_hybrid_retriever_top_results_are_tax_relevant(self, retriever):
        """Top results for an 80C query should be from the tax domain."""
        results = retriever.retrieve("Section 80C income tax deductions", top_k=5)

        assert len(results) > 0
        top_domains = [r["metadata"].get("domain") for r in results[:3]]
        assert (
            "tax" in top_domains
        ), f"Expected 'tax' in top-3 domains, got: {top_domains}"

    def test_hybrid_retriever_domain_filter(self, retriever):
        """retrieve(domain='legal') should return only legal-domain chunks."""
        results = retriever.retrieve(
            "contract agreement parties", domain="legal", top_k=5
        )

        assert len(results) > 0
        for r in results:
            assert (
                r["metadata"]["domain"] == "legal"
            ), f"Expected domain='legal', got '{r['metadata']['domain']}'"

    def test_hybrid_retriever_invalid_domain(self, retriever):
        """An invalid domain should not crash — should fall back to 'all'."""
        results = retriever.retrieve("tax penalty", domain="invalid_domain", top_k=5)

        # Should return results without raising
        assert isinstance(results, list)
        # Results may span multiple domains since we fell back to "all"

    def test_hybrid_retriever_empty_query(self, retriever):
        """Empty query should return empty list without crashing."""
        results = retriever.retrieve("", top_k=5)
        assert results == []

    def test_hybrid_retriever_get_stats(self, retriever):
        """get_stats() should return total_chunks > 0 and a domain breakdown."""
        stats = retriever.get_stats()

        assert "total_chunks" in stats
        assert "domains" in stats
        assert stats["total_chunks"] > 0
        assert isinstance(stats["domains"], dict)
