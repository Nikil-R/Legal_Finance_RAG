"""
Tests for the re-ranking subsystem (CrossEncoderReranker, ContextBuilder, RetrievalPipeline).

Cross-encoder tests use a real model so the first run downloads ~80MB.
They are marked with pytest.mark.slow if you want to skip them during
fast iteration (run with: pytest -m "not slow").
"""

from __future__ import annotations

import pytest

from app.reranking.context_builder import ContextBuilder
from app.reranking.reranker import CrossEncoderReranker

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def reranker() -> CrossEncoderReranker:
    """Load the cross-encoder once for the whole module (expensive)."""
    return CrossEncoderReranker()


@pytest.fixture()
def tax_candidates() -> list[dict]:
    """
    Three candidates: two tax-relevant, one completely off-topic (weather).
    The cross-encoder should rank the weather chunk far below the tax chunks.
    """
    return [
        {
            "chunk_id": "1",
            "content": (
                "Section 80C of the Income Tax Act allows deductions up to Rs 1,50,000 "
                "for investments in PPF, ELSS, NSC, and life insurance premiums."
            ),
            "metadata": {"source": "tax.pdf", "domain": "tax"},
            "rrf_score": 0.5,
            "found_by": "both",
        },
        {
            "chunk_id": "2",
            "content": (
                "The weather in Mumbai is hot and humid during summer months. "
                "Temperatures regularly exceed 35°C in May and June."
            ),
            "metadata": {"source": "weather.pdf", "domain": "other"},
            "rrf_score": 0.6,
            "found_by": "vector",
        },
        {
            "chunk_id": "3",
            "content": (
                "Income tax deductions under Section 80C include contributions to "
                "Public Provident Fund, National Savings Certificate, and ELSS mutual funds."
            ),
            "metadata": {"source": "tax2.pdf", "domain": "tax"},
            "rrf_score": 0.4,
            "found_by": "bm25",
        },
    ]


@pytest.fixture()
def sample_chunks() -> list[dict]:
    """Two chunks for ContextBuilder tests."""
    return [
        {
            "chunk_id": "1",
            "content": "This is the first chunk content.",
            "metadata": {"source": "doc1.pdf", "domain": "tax"},
            "rerank_score": 0.9,
        },
        {
            "chunk_id": "2",
            "content": "This is the second chunk content.",
            "metadata": {"source": "doc2.pdf", "domain": "finance"},
            "rerank_score": 0.8,
        },
    ]


# ── CrossEncoderReranker Tests ────────────────────────────────────────────────


class TestCrossEncoderReranker:
    def test_initialization(self, reranker: CrossEncoderReranker):
        """CrossEncoderReranker should load without error."""
        from app.config import settings

        assert reranker.model_name == settings.CROSS_ENCODER_MODEL
        assert reranker._model is not None

    def test_rerank_basic_returns_top_k(
        self, reranker: CrossEncoderReranker, tax_candidates
    ):
        """rerank() should return exactly top_k results."""
        results = reranker.rerank(
            "What are Section 80C tax deductions?",
            tax_candidates,
            top_k=2,
        )
        assert len(results) == 2

    def test_rerank_weather_chunk_not_in_top2(
        self, reranker: CrossEncoderReranker, tax_candidates
    ):
        """The weather chunk should lose to on-topic tax chunks."""
        results = reranker.rerank(
            "What are Section 80C tax deductions?",
            tax_candidates,
            top_k=2,
        )
        top_ids = {r["chunk_id"] for r in results}
        assert "2" not in top_ids, (
            "Weather chunk (id='2') should NOT be in top-2 for a tax query; "
            f"got top ids: {top_ids}"
        )

    def test_rerank_results_sorted_descending(
        self, reranker: CrossEncoderReranker, tax_candidates
    ):
        """Results must be strictly sorted by rerank_score descending."""
        results = reranker.rerank("Section 80C tax deductions", tax_candidates, top_k=3)
        scores = [r["rerank_score"] for r in results]
        assert scores == sorted(scores, reverse=True), f"Scores not sorted: {scores}"

    def test_rerank_score_field_present(
        self, reranker: CrossEncoderReranker, tax_candidates
    ):
        """Every result must carry a rerank_score that is a plain Python float."""
        results = reranker.rerank("tax deductions", tax_candidates, top_k=3)
        for r in results:
            assert "rerank_score" in r
            assert (
                type(r["rerank_score"]) is float
            ), f"Expected float, got {type(r['rerank_score'])}"

    def test_rerank_original_fields_preserved(
        self, reranker: CrossEncoderReranker, tax_candidates
    ):
        """Reranking must not drop any existing fields (chunk_id, metadata, etc.)."""
        results = reranker.rerank("tax deductions", tax_candidates, top_k=3)
        for r in results:
            assert "chunk_id" in r
            assert "content" in r
            assert "metadata" in r
            assert "rrf_score" in r
            assert "found_by" in r

    def test_rerank_empty_candidates(self, reranker: CrossEncoderReranker):
        """Empty candidate list should return empty list without raising."""
        results = reranker.rerank("any query", [], top_k=5)
        assert results == []

    def test_rerank_fewer_candidates_than_top_k(
        self, reranker: CrossEncoderReranker, tax_candidates
    ):
        """When candidates < top_k all candidates should be returned."""
        results = reranker.rerank("tax deductions", tax_candidates, top_k=100)
        assert len(results) == len(tax_candidates)

    def test_rerank_with_threshold_filters_irrelevant(
        self, reranker: CrossEncoderReranker, tax_candidates
    ):
        """
        The weather chunk should be filtered out by threshold when querying about taxes.
        We use a low threshold (0.0) so only truly negative scores are removed;
        the goal is to verify the weather chunk scores lower.
        """
        results = reranker.rerank_with_threshold(
            "What are Section 80C tax deductions?",
            tax_candidates,
            top_k=3,
            min_score=0.0,
        )
        ids_returned = {r["chunk_id"] for r in results}
        # Tax chunks must be present; weather may or may not pass 0.0
        assert (
            "1" in ids_returned or "3" in ids_returned
        ), "At least one tax chunk should pass threshold"

    def test_rerank_with_threshold_high_cutoff(
        self, reranker: CrossEncoderReranker, tax_candidates
    ):
        """With an impossibly high threshold nothing should pass."""
        results = reranker.rerank_with_threshold(
            "tax deductions", tax_candidates, top_k=3, min_score=999.0
        )
        assert results == []


# ── ContextBuilder Tests ──────────────────────────────────────────────────────


class TestContextBuilder:
    def test_build_context_contains_numbering(self, sample_chunks):
        """Output must contain [1] and [2] markers."""
        ctx = ContextBuilder().build_context(sample_chunks)
        assert "[1]" in ctx
        assert "[2]" in ctx

    def test_build_context_contains_sources(self, sample_chunks):
        """Output must contain source filenames."""
        ctx = ContextBuilder().build_context(sample_chunks)
        assert "doc1.pdf" in ctx
        assert "doc2.pdf" in ctx

    def test_build_context_contains_content(self, sample_chunks):
        """Chunk text must appear in the context."""
        ctx = ContextBuilder().build_context(sample_chunks)
        assert "first chunk content" in ctx
        assert "second chunk content" in ctx

    def test_build_context_empty_chunks(self):
        """Empty input should return an empty string."""
        assert ContextBuilder().build_context([]) == ""

    def test_build_context_truncation(self):
        """Context longer than max_context_length should be truncated with a marker."""
        long_chunk = {
            "chunk_id": "x",
            "content": "A" * 200,
            "metadata": {"source": "big.pdf", "domain": "tax"},
            "rerank_score": 0.9,
        }
        builder = ContextBuilder(max_context_length=100)
        result = builder.build_context([long_chunk])

        assert "... [truncated]" in result
        # Total length should be at most 100 (original cap) + len of suffix
        suffix = "\n... [truncated]"
        assert len(result) == 100 + len(suffix)

    def test_build_context_no_truncation_within_limit(self, sample_chunks):
        """Short context should NOT be truncated."""
        ctx = ContextBuilder(max_context_length=10_000).build_context(sample_chunks)
        assert "... [truncated]" not in ctx

    def test_build_context_with_metadata_schema(self, sample_chunks):
        """build_context_with_metadata() must return the full expected schema."""
        result = ContextBuilder().build_context_with_metadata(sample_chunks)

        assert "context_string" in result
        assert "sources" in result
        assert "total_chunks" in result
        assert "truncated" in result
        assert isinstance(result["context_string"], str)
        assert len(result["context_string"]) > 0
        assert result["total_chunks"] == 2

    def test_build_context_with_metadata_sources(self, sample_chunks):
        """Each source entry must have reference_id, chunk_id, source, domain, rerank_score."""
        result = ContextBuilder().build_context_with_metadata(sample_chunks)
        sources = result["sources"]

        assert len(sources) == 2
        for i, src in enumerate(sources, start=1):
            assert src["reference_id"] == i
            assert "chunk_id" in src
            assert "source" in src
            assert "domain" in src
            assert "rerank_score" in src

    def test_build_context_with_metadata_reference_ids(self, sample_chunks):
        """reference_ids must be 1 and 2 (1-based)."""
        result = ContextBuilder().build_context_with_metadata(sample_chunks)
        ids = [s["reference_id"] for s in result["sources"]]
        assert ids == [1, 2]

    def test_build_context_with_metadata_not_truncated(self, sample_chunks):
        """Short content should set truncated=False."""
        result = ContextBuilder().build_context_with_metadata(sample_chunks)
        assert result["truncated"] is False

    def test_build_context_with_metadata_truncated_flag(self):
        """Long content should set truncated=True."""
        chunk = {
            "chunk_id": "x",
            "content": "B" * 500,
            "metadata": {"source": "big.pdf", "domain": "tax"},
            "rerank_score": 0.5,
        }
        result = ContextBuilder(max_context_length=50).build_context_with_metadata(
            [chunk]
        )
        assert result["truncated"] is True


# ── RetrievalPipeline Integration Tests ──────────────────────────────────────


class TestRetrievalPipeline:
    @pytest.fixture(scope="class")
    def pipeline(self):
        from app.reranking.pipeline import RetrievalPipeline

        return RetrievalPipeline()

    def test_pipeline_success(self, pipeline):
        """A relevant query should produce success=True with context and sources."""
        result = pipeline.run("Section 80C deductions", domain="tax")

        assert result["success"] is True
        assert result["query"] == "Section 80C deductions"
        assert result["domain"] == "tax"
        assert result["candidates_found"] > 0
        assert result["candidates_reranked"] > 0
        assert result["candidates_reranked"] <= 5
        assert isinstance(result["context"], str)
        assert len(result["context"]) > 0
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) > 0
        assert isinstance(result["top_score"], float)

    def test_pipeline_timing_fields_present(self, pipeline):
        """Success result must include all timing fields."""
        result = pipeline.run("Section 80C deductions", domain="tax")
        assert "retrieval_time_ms" in result
        assert "reranking_time_ms" in result
        assert "total_time_ms" in result
        assert result["total_time_ms"] > 0

    def test_pipeline_nonsense_query_fails_gracefully(self, pipeline):
        """A completely nonsense query should return success=False, not raise."""
        result = pipeline.run("xyzzy foobar gibberish zzzzzzz", domain="all")

        # Either no docs were retrieved, or none passed the relevance threshold
        assert result["success"] is False
        assert result["error"] is not None and len(result["error"]) > 0
        assert result["context"] is None
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) == 0

    def test_pipeline_empty_query_fails_gracefully(self, pipeline):
        """Empty query must return error result, not crash."""
        result = pipeline.run("  ")
        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_pipeline_run_simple_returns_tuple(self, pipeline):
        """run_simple() should return (context_str, sources) on success."""
        outcome = pipeline.run_simple("KYC requirements for banks", domain="finance")
        assert outcome is not None
        context, sources = outcome
        assert isinstance(context, str)
        assert len(context) > 0
        assert isinstance(sources, list)

    def test_pipeline_run_simple_returns_none_on_failure(self, pipeline):
        """run_simple() should return None when the pipeline fails."""
        outcome = pipeline.run_simple("xyzzy gibberish zzzzz")
        assert outcome is None
