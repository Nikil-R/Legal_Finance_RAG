"""
Main evaluation orchestrator.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.generation import RAGPipeline
from app.utils.logger import get_logger
from evaluation.golden_dataset import GoldenDataset, GoldenQuestion
from evaluation.metrics import (
    CitationQualityScorer,
    CorrectnessScorer,
    FaithfulnessScorer,
    RetrievalRelevanceScorer,
)

logger = get_logger(__name__)


@dataclass
class QuestionResult:
    """Result for a single question evaluation."""

    question_id: str
    question: str
    domain: str
    difficulty: str

    # Generated outputs
    answer: Optional[str] = None
    sources: list = field(default_factory=list)
    context: Optional[str] = None

    # Metric scores
    faithfulness_score: float = 0.0
    correctness_score: float = 0.0
    citation_quality_score: float = 0.0
    retrieval_relevance_score: float = 0.0

    # Detailed results
    faithfulness_details: dict = field(default_factory=dict)
    correctness_details: dict = field(default_factory=dict)
    citation_details: dict = field(default_factory=dict)
    retrieval_details: dict = field(default_factory=dict)

    # Status
    success: bool = False
    error: Optional[str] = None
    time_ms: float = 0.0

    @property
    def overall_score(self) -> float:
        """Calculate overall score as average of all metrics."""
        scores = [
            self.faithfulness_score,
            self.correctness_score,
            self.citation_quality_score,
            self.retrieval_relevance_score,
        ]
        return sum(scores) / len(scores) if scores else 0.0

    @property
    def passed(self) -> bool:
        """Check if this question passed all thresholds."""
        return (
            self.success
            and self.faithfulness_score >= 0.7
            and self.correctness_score >= 0.6
            and self.citation_quality_score >= 0.8
            and self.retrieval_relevance_score >= 0.5
        )


@dataclass
class EvaluationResult:
    """Complete evaluation result."""

    timestamp: datetime
    dataset_version: str
    total_questions: int
    questions_passed: int
    questions_failed: int

    # Aggregate scores
    avg_faithfulness: float
    avg_correctness: float
    avg_citation_quality: float
    avg_retrieval_relevance: float
    avg_overall: float

    # Pass rates
    pass_rate: float

    # By domain
    domain_scores: dict = field(default_factory=dict)

    # By difficulty
    difficulty_scores: dict = field(default_factory=dict)

    # Individual results
    question_results: list[QuestionResult] = field(default_factory=list)

    # Timing
    total_time_seconds: float = 0.0

    @property
    def passed(self) -> bool:
        """Check if overall evaluation passed."""
        return self.pass_rate >= 0.8  # 80% pass rate required


class RAGEvaluator:
    """
    Evaluates the RAG system against a golden dataset.
    """

    def __init__(self, dataset_path: str = None):
        """
        Initialize evaluator.

        Args:
            dataset_path: Optional path to golden dataset YAML
        """
        self.dataset = GoldenDataset(dataset_path)

        # Initialize scorers
        self.faithfulness_scorer = FaithfulnessScorer()
        self.correctness_scorer = CorrectnessScorer()
        self.citation_scorer = CitationQualityScorer()
        self.retrieval_scorer = RetrievalRelevanceScorer()

        # Initialize RAG pipeline
        self.pipeline = None

    def _ensure_pipeline(self):
        """Lazily initialize RAG pipeline."""
        if self.pipeline is None:
            logger.info("Initializing RAG pipeline for evaluation...")
            self.pipeline = RAGPipeline()
            logger.info("RAG pipeline initialized")

    def evaluate_question(self, question: GoldenQuestion) -> QuestionResult:
        """
        Evaluate a single question.

        Args:
            question: The golden question to evaluate

        Returns:
            QuestionResult with all metrics
        """
        self._ensure_pipeline()

        result = QuestionResult(
            question_id=question.id,
            question=question.question,
            domain=question.domain,
            difficulty=question.difficulty,
        )

        start_time = time.time()

        try:
            # Run RAG pipeline
            logger.info(f"Evaluating: {question.id} - {question.question[:50]}...")

            rag_result = self.pipeline.run(
                question=question.question, domain=question.domain
            )

            result.time_ms = (time.time() - start_time) * 1000

            if not rag_result.get("success"):
                result.error = rag_result.get("error", "Unknown error")
                result.success = False
                return result

            # Store outputs
            result.answer = rag_result.get("answer", "")
            result.sources = rag_result.get("sources", [])
            result.context = rag_result.get("metadata", {}).get("context", "")
            result.success = True

            # Score faithfulness
            faith_result = self.faithfulness_scorer.score(
                answer=result.answer,
                context=result.context
                or self._build_context_from_sources(result.sources),
                sources=result.sources,
            )
            result.faithfulness_score = faith_result.score
            result.faithfulness_details = {
                "is_grounded": faith_result.is_grounded,
                "claims_found": faith_result.claims_found,
                "claims_supported": faith_result.claims_supported,
                "explanation": faith_result.explanation,
            }

            # Score correctness
            correct_result = self.correctness_scorer.score(
                answer=result.answer,
                expected_answer=question.expected_answer,
                required_keywords=question.required_keywords,
            )
            result.correctness_score = correct_result.score
            result.correctness_details = {
                "keyword_matches": correct_result.keyword_matches,
                "keywords_expected": correct_result.keywords_expected,
                "matched": correct_result.matched_keywords,
                "missing": correct_result.missing_keywords,
                "explanation": correct_result.explanation,
            }

            # Score citation quality
            citation_result = self.citation_scorer.score(
                answer=result.answer,
                num_sources=len(result.sources),
                expected_citations=question.expected_citations,
            )
            result.citation_quality_score = citation_result.score
            result.citation_details = {
                "has_citations": citation_result.has_citations,
                "citations_found": citation_result.citations_found,
                "invalid_citations": citation_result.invalid_citations,
                "has_disclaimer": citation_result.has_disclaimer,
                "explanation": citation_result.explanation,
            }

            # Score retrieval relevance
            retrieval_result = self.retrieval_scorer.score(
                sources=result.sources,
                expected_domain=question.domain,
                required_keywords=question.required_keywords,
            )
            result.retrieval_relevance_score = retrieval_result.score
            result.retrieval_details = {
                "chunks_retrieved": retrieval_result.chunks_retrieved,
                "relevant_chunks": retrieval_result.relevant_chunks,
                "top_score": retrieval_result.top_score,
                "domain_match": retrieval_result.domain_match,
                "explanation": retrieval_result.explanation,
            }

        except Exception as e:
            result.error = str(e)
            result.success = False
            result.time_ms = (time.time() - start_time) * 1000
            logger.error(f"Error evaluating {question.id}: {e}")

        return result

    def _build_context_from_sources(self, sources: list[dict]) -> str:
        """Build context string from sources if not available."""
        parts = []
        for src in sources:
            content = src.get("content") or src.get("excerpt") or ""
            parts.append(content)
        return "\n\n".join(parts)

    def evaluate_all(
        self,
        domain_filter: str = None,
        difficulty_filter: str = None,
        limit: int = None,
    ) -> EvaluationResult:
        """
        Evaluate all questions in the dataset.

        Args:
            domain_filter: Optional domain to filter by
            difficulty_filter: Optional difficulty to filter by
            limit: Maximum number of questions to evaluate

        Returns:
            EvaluationResult with aggregate metrics
        """
        start_time = time.time()

        # Get questions
        questions = self.dataset.get_all_questions()

        if domain_filter:
            questions = [q for q in questions if q.domain == domain_filter]

        if difficulty_filter:
            questions = [q for q in questions if q.difficulty == difficulty_filter]

        if limit:
            questions = questions[:limit]

        logger.info(f"Starting evaluation of {len(questions)} questions...")

        # Evaluate each question
        results = []
        for i, question in enumerate(questions):
            logger.info(f"Progress: {i+1}/{len(questions)}")
            result = self.evaluate_question(question)
            results.append(result)

        # Aggregate results
        total_time = time.time() - start_time

        passed = [r for r in results if r.passed]
        failed = [r for r in results if not r.passed]

        # Calculate averages
        successful_results = [r for r in results if r.success]

        avg_faith = (
            sum(r.faithfulness_score for r in successful_results)
            / len(successful_results)
            if successful_results
            else 0.0
        )
        avg_correct = (
            sum(r.correctness_score for r in successful_results)
            / len(successful_results)
            if successful_results
            else 0.0
        )
        avg_citation = (
            sum(r.citation_quality_score for r in successful_results)
            / len(successful_results)
            if successful_results
            else 0.0
        )
        avg_retrieval = (
            sum(r.retrieval_relevance_score for r in successful_results)
            / len(successful_results)
            if successful_results
            else 0.0
        )
        avg_overall = (
            sum(r.overall_score for r in successful_results) / len(successful_results)
            if successful_results
            else 0.0
        )

        # Calculate domain scores
        domain_scores = {}
        for domain in ["tax", "finance", "legal"]:
            domain_results = [r for r in successful_results if r.domain == domain]
            if domain_results:
                domain_scores[domain] = {
                    "count": len(domain_results),
                    "avg_score": sum(r.overall_score for r in domain_results)
                    / len(domain_results),
                    "pass_rate": len([r for r in domain_results if r.passed])
                    / len(domain_results),
                }

        # Calculate difficulty scores
        difficulty_scores = {}
        for difficulty in ["easy", "medium", "hard"]:
            diff_results = [r for r in successful_results if r.difficulty == difficulty]
            if diff_results:
                difficulty_scores[difficulty] = {
                    "count": len(diff_results),
                    "avg_score": sum(r.overall_score for r in diff_results)
                    / len(diff_results),
                    "pass_rate": len([r for r in diff_results if r.passed])
                    / len(diff_results),
                }

        return EvaluationResult(
            timestamp=datetime.now(),
            dataset_version=self.dataset.version,
            total_questions=len(results),
            questions_passed=len(passed),
            questions_failed=len(failed),
            avg_faithfulness=avg_faith,
            avg_correctness=avg_correct,
            avg_citation_quality=avg_citation,
            avg_retrieval_relevance=avg_retrieval,
            avg_overall=avg_overall,
            pass_rate=len(passed) / len(results) if results else 0.0,
            domain_scores=domain_scores,
            difficulty_scores=difficulty_scores,
            question_results=results,
            total_time_seconds=total_time,
        )
