"""
Tests for the evaluation system.
"""

from datetime import datetime

import pytest

from evaluation.evaluator import EvaluationResult
from evaluation.golden_dataset import GoldenDataset
from evaluation.metrics.citation_quality import CitationQualityScorer
from evaluation.metrics.correctness import CorrectnessScorer
from evaluation.metrics.faithfulness import FaithfulnessScorer
from evaluation.metrics.retrieval import RetrievalRelevanceScorer
from evaluation.reporter import EvaluationReporter


class TestGoldenDataset:
    """Tests for the golden dataset loader."""

    @pytest.fixture(scope="class")
    def dataset(self):
        """Shared dataset fixture."""
        return GoldenDataset()

    def test_load_dataset(self, dataset):
        """Test dataset loads successfully."""
        assert len(dataset) > 0
        assert dataset.version != ""

    def test_dataset_summary(self, dataset):
        """Test dataset summary."""
        summary = dataset.summary()

        assert "total_questions" in summary
        assert "by_domain" in summary
        assert "by_difficulty" in summary
        assert summary["total_questions"] >= 30

    def test_filter_by_domain(self, dataset):
        """Test filtering by domain."""
        tax_questions = dataset.get_questions_by_domain("tax")

        assert len(tax_questions) > 0
        assert all(q.domain == "tax" for q in tax_questions)

    def test_filter_by_difficulty(self, dataset):
        """Test filtering by difficulty."""
        easy_questions = dataset.get_questions_by_difficulty("easy")

        assert len(easy_questions) > 0
        assert all(q.difficulty == "easy" for q in easy_questions)

    def test_get_question_by_id(self, dataset):
        """Test getting question by ID."""
        question = dataset.get_question_by_id("tax_001")

        assert question is not None
        assert question.id == "tax_001"
        assert question.domain == "tax"


class TestFaithfulnessScorer:
    """Tests for faithfulness scoring."""

    def test_faithful_answer(self):
        """Test scoring a faithful answer."""
        scorer = FaithfulnessScorer()

        context = "Section 80C allows deductions up to Rs 1,50,000 for investments in PPF, ELSS, and NSC."
        answer = "Under Section 80C, taxpayers can claim deductions up to Rs 1,50,000 for investments like PPF and ELSS."

        result = scorer.score(answer, context, [])

        assert result.score > 0.5
        assert result.is_grounded

    def test_unfaithful_answer(self):
        """Test scoring an unfaithful answer."""
        scorer = FaithfulnessScorer()

        context = "Section 80C allows deductions for PPF investments."
        answer = "Under Section 80D, taxpayers can claim unlimited deductions for all types of investments including cryptocurrency."

        result = scorer.score(answer, context, [])

        assert result.score < 0.5

    def test_empty_answer(self):
        """Test scoring empty answer."""
        scorer = FaithfulnessScorer()
        result = scorer.score("", "Some context", [])

        assert result.score == 0.0


class TestCorrectnessScorer:
    """Tests for correctness scoring."""

    def test_correct_answer(self):
        """Test scoring a correct answer."""
        scorer = CorrectnessScorer()

        answer = "Under Section 80C, deductions up to Rs 1,50,000 are allowed for PPF and ELSS investments."
        expected = "Section 80C allows deductions of Rs 1,50,000."
        keywords = ["80C", "1,50,000", "deduction"]

        result = scorer.score(answer, expected, keywords)

        assert result.score >= 0.6
        assert len(result.matched_keywords) > 0

    def test_missing_keywords(self):
        """Test scoring answer with missing keywords."""
        scorer = CorrectnessScorer()

        answer = "Taxpayers can invest in various schemes."
        expected = "Section 80C allows deductions."
        keywords = ["80C", "deduction", "1,50,000"]

        result = scorer.score(answer, expected, keywords)

        assert result.score < 0.5
        assert len(result.missing_keywords) > 0


class TestCitationQualityScorer:
    """Tests for citation quality scoring."""

    def test_good_citations(self):
        """Test scoring answer with good citations."""
        scorer = CitationQualityScorer()

        answer = """
        Section 80C allows deductions up to Rs 1,50,000 [1].
        Eligible investments include PPF and ELSS [1][2].
        
        ---
        **Disclaimer:** This is for educational purposes only.
        """

        result = scorer.score(answer, num_sources=3, expected_citations=1)

        assert result.has_citations
        assert result.has_disclaimer
        assert result.score >= 0.8

    def test_invalid_citations(self):
        """Test scoring answer with invalid citations."""
        scorer = CitationQualityScorer()

        answer = "According to the document [5], taxes are required."

        result = scorer.score(answer, num_sources=2, expected_citations=1)

        assert 5 in result.invalid_citations

    def test_missing_disclaimer(self):
        """Test scoring answer without disclaimer."""
        scorer = CitationQualityScorer()

        answer = "Section 80C allows deductions [1]."

        result = scorer.score(answer, num_sources=1, expected_citations=1)

        assert not result.has_disclaimer
        assert result.score < 1.0


class TestRetrievalRelevanceScorer:
    """Tests for retrieval relevance scoring."""

    def test_relevant_retrieval(self):
        """Test scoring relevant retrieval."""
        scorer = RetrievalRelevanceScorer()

        sources = [
            {
                "content": "Section 80C deductions for PPF",
                "domain": "tax",
                "relevance_score": 0.9,
            },
            {
                "content": "ELSS investments under 80C",
                "domain": "tax",
                "relevance_score": 0.8,
            },
        ]

        result = scorer.score(sources, "tax", ["80C", "PPF"])

        assert result.score > 0.5
        assert result.domain_match

    def test_no_retrieval(self):
        """Test scoring empty retrieval."""
        scorer = RetrievalRelevanceScorer()
        result = scorer.score([], "tax", ["80C"])

        assert result.score == 0.0
        assert result.chunks_retrieved == 0


class TestReporter:
    """Tests for report generation."""

    def test_console_report(self):
        """Test console report generation."""
        reporter = EvaluationReporter()

        result = EvaluationResult(
            timestamp=datetime.now(),
            dataset_version="1.0",
            total_questions=10,
            questions_passed=8,
            questions_failed=2,
            avg_faithfulness=0.8,
            avg_correctness=0.7,
            avg_citation_quality=0.9,
            avg_retrieval_relevance=0.6,
            avg_overall=0.75,
            pass_rate=0.8,
            domain_scores={"tax": {"count": 5, "avg_score": 0.8, "pass_rate": 0.8}},
            difficulty_scores={
                "easy": {"count": 5, "avg_score": 0.85, "pass_rate": 0.9}
            },
            question_results=[],
            total_time_seconds=60.0,
        )

        report = reporter.generate_console_report(result)

        assert "EVALUATION REPORT" in report
        assert "PASSED" in report
        assert "80.0%" in report or "0.8" in report

    def test_json_report(self):
        """Test JSON report generation."""
        reporter = EvaluationReporter()

        result = EvaluationResult(
            timestamp=datetime.now(),
            dataset_version="1.0",
            total_questions=10,
            questions_passed=8,
            questions_failed=2,
            avg_faithfulness=0.8,
            avg_correctness=0.7,
            avg_citation_quality=0.9,
            avg_retrieval_relevance=0.6,
            avg_overall=0.75,
            pass_rate=0.8,
            total_time_seconds=60.0,
        )
        report = reporter.generate_json_report(result)
        assert report["summary"]["total_questions"] == 10
