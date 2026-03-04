"""
Golden dataset loading and management.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class GoldenQuestion:
    """A single question from the golden dataset."""

    id: str
    question: str
    domain: str
    expected_answer: str
    required_keywords: list[str]
    expected_citations: int
    difficulty: str

    def __post_init__(self):
        if self.required_keywords is None:
            self.required_keywords = []


@dataclass
class EvaluationThresholds:
    """Thresholds for evaluation metrics."""

    faithfulness_min: float = 0.7
    correctness_min: float = 0.6
    citation_quality_min: float = 0.8
    retrieval_relevance_min: float = 0.5
    overall_pass_rate: float = 0.8


class GoldenDataset:
    """Loader and manager for the golden Q&A dataset."""

    def __init__(self, dataset_path: str | Path = None):
        """
        Initialize the golden dataset.

        Args:
            dataset_path: Path to the YAML file. Defaults to evaluation/data/golden_qa.yaml
        """
        if dataset_path is None:
            dataset_path = Path(__file__).parent / "data" / "golden_qa.yaml"

        self.dataset_path = Path(dataset_path)
        self.questions: list[GoldenQuestion] = []
        self.thresholds: EvaluationThresholds = EvaluationThresholds()
        self.version: str = ""
        self.description: str = ""

        self._load_dataset()

    def _load_dataset(self):
        """Load the dataset from YAML file."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Golden dataset not found: {self.dataset_path}")

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self.version = data.get("version", "unknown")
        self.description = data.get("description", "")

        # Load questions
        for q in data.get("questions", []):
            self.questions.append(
                GoldenQuestion(
                    id=q["id"],
                    question=q["question"],
                    domain=q["domain"],
                    expected_answer=q["expected_answer"],
                    required_keywords=q.get("required_keywords", []),
                    expected_citations=q.get("expected_citations", 1),
                    difficulty=q.get("difficulty", "medium"),
                )
            )

        # Load thresholds
        thresholds = data.get("evaluation_thresholds", {})
        self.thresholds = EvaluationThresholds(
            faithfulness_min=thresholds.get("faithfulness_min", 0.7),
            correctness_min=thresholds.get("correctness_min", 0.6),
            citation_quality_min=thresholds.get("citation_quality_min", 0.8),
            retrieval_relevance_min=thresholds.get("retrieval_relevance_min", 0.5),
            overall_pass_rate=thresholds.get("overall_pass_rate", 0.8),
        )

    def get_all_questions(self) -> list[GoldenQuestion]:
        """Get all questions in the dataset."""
        return self.questions

    def get_questions_by_domain(self, domain: str) -> list[GoldenQuestion]:
        """Get questions filtered by domain."""
        return [q for q in self.questions if q.domain == domain]

    def get_questions_by_difficulty(self, difficulty: str) -> list[GoldenQuestion]:
        """Get questions filtered by difficulty."""
        return [q for q in self.questions if q.difficulty == difficulty]

    def get_question_by_id(self, question_id: str) -> Optional[GoldenQuestion]:
        """Get a specific question by ID."""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None

    def __len__(self) -> int:
        return len(self.questions)

    def __iter__(self):
        return iter(self.questions)

    def summary(self) -> dict:
        """Get a summary of the dataset."""
        domains = {}
        difficulties = {}

        for q in self.questions:
            domains[q.domain] = domains.get(q.domain, 0) + 1
            difficulties[q.difficulty] = difficulties.get(q.difficulty, 0) + 1

        return {
            "version": self.version,
            "total_questions": len(self.questions),
            "by_domain": domains,
            "by_difficulty": difficulties,
            "thresholds": {
                "faithfulness_min": self.thresholds.faithfulness_min,
                "correctness_min": self.thresholds.correctness_min,
                "citation_quality_min": self.thresholds.citation_quality_min,
                "retrieval_relevance_min": self.thresholds.retrieval_relevance_min,
                "overall_pass_rate": self.thresholds.overall_pass_rate,
            },
        }
