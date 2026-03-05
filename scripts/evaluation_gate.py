"""
CI quality gate for RAG evaluation.
Fails with non-zero exit code if pass rate is below configured threshold.
"""

from __future__ import annotations

import argparse
import sys

from app.config import settings
from evaluation.evaluator import RAGEvaluator


def main() -> int:
    parser = argparse.ArgumentParser(description="Run evaluation gate for RAG.")
    parser.add_argument("--dataset", default=None, help="Optional dataset path")
    parser.add_argument(
        "--min-pass-rate",
        type=float,
        default=settings.EVAL_GATE_MIN_PASS_RATE,
        help="Minimum pass rate required to pass the gate",
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument(
        "--min-faithfulness",
        type=float,
        default=settings.EVAL_GATE_MIN_FAITHFULNESS,
    )
    parser.add_argument(
        "--min-correctness",
        type=float,
        default=settings.EVAL_GATE_MIN_CORRECTNESS,
    )
    parser.add_argument(
        "--min-citation-quality",
        type=float,
        default=settings.EVAL_GATE_MIN_CITATION_QUALITY,
    )
    parser.add_argument(
        "--min-retrieval-relevance",
        type=float,
        default=settings.EVAL_GATE_MIN_RETRIEVAL_RELEVANCE,
    )
    args = parser.parse_args()

    evaluator = RAGEvaluator(dataset_path=args.dataset)
    result = evaluator.evaluate_all(limit=args.limit)
    pass_rate = result.pass_rate
    print(f"Evaluation pass rate: {pass_rate:.3f} (threshold={args.min_pass_rate:.3f})")

    failures: list[str] = []
    if pass_rate < args.min_pass_rate:
        failures.append(
            f"pass_rate={pass_rate:.3f} < threshold={args.min_pass_rate:.3f}"
        )
    if result.avg_faithfulness < args.min_faithfulness:
        failures.append(
            f"faithfulness={result.avg_faithfulness:.3f} < threshold={args.min_faithfulness:.3f}"
        )
    if result.avg_correctness < args.min_correctness:
        failures.append(
            f"correctness={result.avg_correctness:.3f} < threshold={args.min_correctness:.3f}"
        )
    if result.avg_citation_quality < args.min_citation_quality:
        failures.append(
            "citation_quality="
            f"{result.avg_citation_quality:.3f} < threshold={args.min_citation_quality:.3f}"
        )
    if result.avg_retrieval_relevance < args.min_retrieval_relevance:
        failures.append(
            "retrieval_relevance="
            f"{result.avg_retrieval_relevance:.3f} < threshold={args.min_retrieval_relevance:.3f}"
        )

    if failures:
        print("Evaluation gate FAILED:")
        for reason in failures:
            print(f"- {reason}")
        return 1
    print("Evaluation gate PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
