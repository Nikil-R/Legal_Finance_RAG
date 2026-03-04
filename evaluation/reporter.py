"""
Evaluation report generation.
"""

import json
from datetime import datetime
from pathlib import Path

from evaluation.evaluator import EvaluationResult


class EvaluationReporter:
    """Generates evaluation reports in various formats."""

    def __init__(self, output_dir: str = "evaluation/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_console_report(self, result: EvaluationResult) -> str:
        """Generate a console-friendly report."""
        lines = []

        # Header
        lines.append("=" * 70)
        lines.append("           LEGALFINANCE RAG - EVALUATION REPORT")
        lines.append("=" * 70)
        lines.append("")

        # Summary
        lines.append(f"Timestamp:        {result.timestamp.isoformat()}")
        lines.append(f"Dataset Version:  {result.dataset_version}")
        lines.append(f"Total Questions:  {result.total_questions}")
        lines.append(f"Time Taken:       {result.total_time_seconds:.1f}s")
        lines.append("")

        # Pass/Fail
        status_icon = "✅" if result.passed else "❌"
        lines.append(
            f"Overall Status:   {status_icon} {'PASSED' if result.passed else 'FAILED'}"
        )
        lines.append(
            f"Pass Rate:        {result.pass_rate:.1%} ({result.questions_passed}/{result.total_questions})"
        )
        lines.append("")

        # Metric Scores
        lines.append("-" * 70)
        lines.append("METRIC SCORES")
        lines.append("-" * 70)
        lines.append(
            f"  Faithfulness:       {result.avg_faithfulness:.3f}  {'✓' if result.avg_faithfulness >= 0.7 else '✗'}"
        )
        lines.append(
            f"  Correctness:        {result.avg_correctness:.3f}  {'✓' if result.avg_correctness >= 0.6 else '✗'}"
        )
        lines.append(
            f"  Citation Quality:   {result.avg_citation_quality:.3f}  {'✓' if result.avg_citation_quality >= 0.8 else '✗'}"
        )
        lines.append(
            f"  Retrieval Relevance:{result.avg_retrieval_relevance:.3f}  {'✓' if result.avg_retrieval_relevance >= 0.5 else '✗'}"
        )
        lines.append(f"  Overall Average:    {result.avg_overall:.3f}")
        lines.append("")

        # By Domain
        lines.append("-" * 70)
        lines.append("SCORES BY DOMAIN")
        lines.append("-" * 70)
        for domain, scores in result.domain_scores.items():
            lines.append(
                f"  {domain.upper():12} | Questions: {scores['count']:2} | Avg: {scores['avg_score']:.3f} | Pass: {scores['pass_rate']:.1%}"
            )
        lines.append("")

        # By Difficulty
        lines.append("-" * 70)
        lines.append("SCORES BY DIFFICULTY")
        lines.append("-" * 70)
        for diff, scores in result.difficulty_scores.items():
            lines.append(
                f"  {diff.upper():12} | Questions: {scores['count']:2} | Avg: {scores['avg_score']:.3f} | Pass: {scores['pass_rate']:.1%}"
            )
        lines.append("")

        # Failed Questions
        failed = [r for r in result.question_results if not r.passed]
        if failed:
            lines.append("-" * 70)
            lines.append(f"FAILED QUESTIONS ({len(failed)})")
            lines.append("-" * 70)
            for r in failed[:10]:  # Show top 10
                lines.append(f"  {r.question_id}: {r.question[:50]}...")
                lines.append(
                    f"    Faith: {r.faithfulness_score:.2f} | Correct: {r.correctness_score:.2f} | Citation: {r.citation_quality_score:.2f} | Retrieval: {r.retrieval_relevance_score:.2f}"
                )
                if r.error:
                    lines.append(f"    Error: {r.error[:50]}...")
            if len(failed) > 10:
                lines.append(f"  ... and {len(failed) - 10} more")
            lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_json_report(self, result: EvaluationResult) -> dict:
        """Generate a JSON-serializable report."""
        return {
            "summary": {
                "timestamp": result.timestamp.isoformat(),
                "dataset_version": result.dataset_version,
                "total_questions": result.total_questions,
                "questions_passed": result.questions_passed,
                "questions_failed": result.questions_failed,
                "pass_rate": result.pass_rate,
                "passed": result.passed,
                "total_time_seconds": result.total_time_seconds,
            },
            "metrics": {
                "avg_faithfulness": result.avg_faithfulness,
                "avg_correctness": result.avg_correctness,
                "avg_citation_quality": result.avg_citation_quality,
                "avg_retrieval_relevance": result.avg_retrieval_relevance,
                "avg_overall": result.avg_overall,
            },
            "by_domain": result.domain_scores,
            "by_difficulty": result.difficulty_scores,
            "questions": [
                {
                    "id": r.question_id,
                    "question": r.question,
                    "domain": r.domain,
                    "difficulty": r.difficulty,
                    "success": r.success,
                    "passed": r.passed,
                    "scores": {
                        "faithfulness": r.faithfulness_score,
                        "correctness": r.correctness_score,
                        "citation_quality": r.citation_quality_score,
                        "retrieval_relevance": r.retrieval_relevance_score,
                        "overall": r.overall_score,
                    },
                    "time_ms": r.time_ms,
                    "error": r.error,
                }
                for r in result.question_results
            ],
        }

    def save_report(
        self,
        result: EvaluationResult,
        format: str = "all",
        filename_prefix: str = "eval",
    ) -> list[Path]:
        """
        Save report to files.

        Args:
            result: The evaluation result
            format: "json", "txt", or "all"
            filename_prefix: Prefix for the filename

        Returns:
            List of paths to saved files
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []

        if format in ("json", "all"):
            json_path = self.output_dir / f"{filename_prefix}_{timestamp}.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(self.generate_json_report(result), f, indent=2)
            saved_files.append(json_path)

        if format in ("txt", "all"):
            txt_path = self.output_dir / f"{filename_prefix}_{timestamp}.txt"
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self.generate_console_report(result))
            saved_files.append(txt_path)

        return saved_files

    def generate_ci_output(self, result: EvaluationResult) -> dict:
        """
        Generate output suitable for CI systems.

        Returns dict with:
        - exit_code: 0 for pass, 1 for fail
        - summary: One-line summary
        - metrics: Key metrics for CI display
        """
        return {
            "exit_code": 0 if result.passed else 1,
            "summary": f"{'PASSED' if result.passed else 'FAILED'}: {result.pass_rate:.1%} pass rate ({result.questions_passed}/{result.total_questions})",
            "metrics": {
                "pass_rate": result.pass_rate,
                "faithfulness": result.avg_faithfulness,
                "correctness": result.avg_correctness,
                "citation_quality": result.avg_citation_quality,
                "retrieval_relevance": result.avg_retrieval_relevance,
            },
        }
