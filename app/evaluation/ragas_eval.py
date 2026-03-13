"""
RAGAS-inspired Evaluation Module
Implements Faithfulness, Answer Relevancy, and Context Precision metrics
without requiring an external RAGAS API key — runs locally using sentence-transformers.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from sentence_transformers import SentenceTransformer, util as st_util

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Shared embedding model (lazy loaded once)
# ---------------------------------------------------------------------------
_EMBED_MODEL: Optional[SentenceTransformer] = None


def _embed_model() -> SentenceTransformer:
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        logger.info("Loading sentence-transformer for RAGAS evaluation…")
        _EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _EMBED_MODEL


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RAGASResult:
    """Single evaluation result for one query."""

    question: str
    answer: str
    contexts: List[str]
    ground_truth: Optional[str] = None

    # Computed metrics (0–1)
    faithfulness: float = 0.0
    answer_relevancy: float = 0.0
    context_precision: float = 0.0
    context_recall: float = 0.0         # Only if ground_truth provided

    # Meta
    latency_ms: float = 0.0
    model: str = "unknown"
    domain: str = "all"
    passed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "answer_preview": self.answer[:200] + "…" if len(self.answer) > 200 else self.answer,
            "metrics": {
                "faithfulness": round(self.faithfulness, 4),
                "answer_relevancy": round(self.answer_relevancy, 4),
                "context_precision": round(self.context_precision, 4),
                "context_recall": round(self.context_recall, 4) if self.ground_truth else None,
            },
            "overall_score": round(self.overall_score, 4),
            "passed": self.passed,
            "latency_ms": round(self.latency_ms, 1),
            "model": self.model,
            "domain": self.domain,
        }

    @property
    def overall_score(self) -> float:
        scores = [self.faithfulness, self.answer_relevancy, self.context_precision]
        if self.ground_truth:
            scores.append(self.context_recall)
        return sum(scores) / len(scores)


@dataclass
class RAGASBatchResult:
    """Aggregated results from evaluating multiple queries."""

    results: List[RAGASResult] = field(default_factory=list)
    total_time_ms: float = 0.0

    @property
    def avg_faithfulness(self) -> float:
        return _avg([r.faithfulness for r in self.results])

    @property
    def avg_answer_relevancy(self) -> float:
        return _avg([r.answer_relevancy for r in self.results])

    @property
    def avg_context_precision(self) -> float:
        return _avg([r.context_precision for r in self.results])

    @property
    def avg_context_recall(self) -> float:
        recall_scores = [r.context_recall for r in self.results if r.ground_truth]
        return _avg(recall_scores) if recall_scores else 0.0

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    def summary(self) -> Dict[str, Any]:
        return {
            "num_samples": len(self.results),
            "avg_faithfulness": round(self.avg_faithfulness, 4),
            "avg_answer_relevancy": round(self.avg_answer_relevancy, 4),
            "avg_context_precision": round(self.avg_context_precision, 4),
            "avg_context_recall": round(self.avg_context_recall, 4),
            "pass_rate": round(self.pass_rate, 4),
            "total_time_ms": round(self.total_time_ms, 1),
            "individual": [r.to_dict() for r in self.results],
        }


def _avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# ---------------------------------------------------------------------------
# Core evaluator
# ---------------------------------------------------------------------------

class RAGASEvaluator:
    """
    Local RAGAS-inspired evaluator.

    Metrics implemented:
      - Faithfulness: Does the answer only contain claims from the context?
      - Answer Relevancy: How well does the answer address the question?
      - Context Precision: Are the top-ranked contexts actually useful?
      - Context Recall: (When ground-truth available) How much GT is covered?
    """

    PASS_THRESHOLD = 0.70   # 70 % overall score to "pass"

    def __init__(self) -> None:
        self._model = _embed_model()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        question: str,
        answer: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        domain: str = "all",
        model: str = "unknown",
        latency_ms: float = 0.0,
    ) -> RAGASResult:
        """Evaluate a single RAG response."""
        result = RAGASResult(
            question=question,
            answer=answer,
            contexts=contexts,
            ground_truth=ground_truth,
            domain=domain,
            model=model,
            latency_ms=latency_ms,
        )
        result.faithfulness = self._faithfulness(answer, contexts)
        result.answer_relevancy = self._answer_relevancy(question, answer)
        result.context_precision = self._context_precision(question, contexts)
        if ground_truth:
            result.context_recall = self._context_recall(ground_truth, contexts)
        result.passed = result.overall_score >= self.PASS_THRESHOLD
        return result

    def evaluate_batch(
        self, samples: List[Dict[str, Any]]
    ) -> RAGASBatchResult:
        """
        Evaluate a batch of samples.

        Each sample dict must contain:
          - question (str)
          - answer (str)
          - contexts (List[str])
        Optional keys:
          - ground_truth (str)
          - domain (str)
          - model (str)
          - latency_ms (float)
        """
        batch = RAGASBatchResult()
        start = time.perf_counter()
        for sample in samples:
            res = self.evaluate(
                question=sample["question"],
                answer=sample["answer"],
                contexts=sample.get("contexts", []),
                ground_truth=sample.get("ground_truth"),
                domain=sample.get("domain", "all"),
                model=sample.get("model", "unknown"),
                latency_ms=sample.get("latency_ms", 0.0),
            )
            batch.results.append(res)
        batch.total_time_ms = (time.perf_counter() - start) * 1000
        return batch

    # ------------------------------------------------------------------
    # Metric implementations
    # ------------------------------------------------------------------

    def _faithfulness(self, answer: str, contexts: List[str]) -> float:
        """
        Faithfulness — fraction of answer sentences that are
        semantically supported by at least one context chunk.
        Uses cosine similarity with a threshold.
        """
        if not contexts:
            return 0.0

        sentences = _split_sentences(answer)
        if not sentences:
            return 0.0

        THRESHOLD = 0.40
        supported = 0

        ctx_embs = self._model.encode(contexts, convert_to_tensor=True)

        for sent in sentences:
            sent_emb = self._model.encode(sent, convert_to_tensor=True)
            scores = st_util.cos_sim(sent_emb, ctx_embs)[0]
            if float(scores.max()) >= THRESHOLD:
                supported += 1

        return supported / len(sentences)

    def _answer_relevancy(self, question: str, answer: str) -> float:
        """
        Answer Relevancy — cosine similarity between the question
        and the answer embeddings.
        """
        if not answer.strip():
            return 0.0
        q_emb = self._model.encode(question, convert_to_tensor=True)
        a_emb = self._model.encode(answer, convert_to_tensor=True)
        return float(st_util.cos_sim(q_emb, a_emb)[0][0])

    def _context_precision(self, question: str, contexts: List[str]) -> float:
        """
        Context Precision — fraction of provided contexts that are
        actually relevant to the question (similarity > threshold).
        """
        if not contexts:
            return 0.0

        THRESHOLD = 0.35
        q_emb = self._model.encode(question, convert_to_tensor=True)
        ctx_embs = self._model.encode(contexts, convert_to_tensor=True)
        scores = st_util.cos_sim(q_emb, ctx_embs)[0]
        relevant = sum(1 for s in scores if float(s) >= THRESHOLD)
        return relevant / len(contexts)

    def _context_recall(self, ground_truth: str, contexts: List[str]) -> float:
        """
        Context Recall — how many GT sentences are covered by the contexts.
        """
        if not contexts:
            return 0.0

        gt_sentences = _split_sentences(ground_truth)
        if not gt_sentences:
            return 0.0

        THRESHOLD = 0.40
        ctx_embs = self._model.encode(contexts, convert_to_tensor=True)
        covered = 0
        for sent in gt_sentences:
            s_emb = self._model.encode(sent, convert_to_tensor=True)
            scores = st_util.cos_sim(s_emb, ctx_embs)[0]
            if float(scores.max()) >= THRESHOLD:
                covered += 1

        return covered / len(gt_sentences)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _split_sentences(text: str) -> List[str]:
    """Simple sentence splitter."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 15]


# ---------------------------------------------------------------------------
# Curated test dataset (legal/finance domain)
# ---------------------------------------------------------------------------

EVAL_DATASET: List[Dict[str, Any]] = [
    {
        "question": "What is the income tax rate for income between ₹6 lakh and ₹9 lakh under the new tax regime for FY 2026-27?",
        "ground_truth": "Under the new tax regime for FY 2026-27, income between ₹6 lakh and ₹9 lakh is taxed at 10%.",
        "domain": "tax",
    },
    {
        "question": "What is the GST rate on gold in India?",
        "ground_truth": "Gold attracts a GST rate of 3% in India.",
        "domain": "tax",
    },
    {
        "question": "What did the Supreme Court rule in the Kesavananda Bharati case?",
        "ground_truth": (
            "The Supreme Court held in Kesavananda Bharati v. State of Kerala (1973) "
            "that while Parliament has wide power to amend the Constitution, it cannot "
            "alter its 'basic structure'."
        ),
        "domain": "legal",
    },
    {
        "question": "What is the standard deduction available to salaried employees for FY 2026-27?",
        "ground_truth": "Salaried employees can claim a standard deduction of ₹75,000 under the new regime for FY 2026-27.",
        "domain": "tax",
    },
    {
        "question": "What rights does Article 21 of the Indian Constitution guarantee?",
        "ground_truth": (
            "Article 21 guarantees the right to life and personal liberty. "
            "The Supreme Court has interpreted it broadly to include the right to privacy, "
            "dignity, livelihood, and a healthy environment."
        ),
        "domain": "legal",
    },
    {
        "question": "What is the rebate u/s 87A for FY 2026-27?",
        "ground_truth": "Under Section 87A, individuals with taxable income up to ₹12 lakh get a full tax rebate under the new regime for FY 2026-27.",
        "domain": "tax",
    },
    {
        "question": "What is SEBI's role in regulating mutual funds?",
        "ground_truth": (
            "SEBI (Securities and Exchange Board of India) regulates mutual funds through "
            "the SEBI (Mutual Funds) Regulations, 1996. It mandates NAV disclosure, "
            "expense ratio limits, and investor grievance mechanisms."
        ),
        "domain": "finance",
    },
]
