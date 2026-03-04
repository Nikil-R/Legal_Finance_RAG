"""
CLI runner for evaluation.
"""
import argparse
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from evaluation.evaluator import RAGEvaluator
from evaluation.reporter import EvaluationReporter
from evaluation.golden_dataset import GoldenDataset


def main():
    parser = argparse.ArgumentParser(
        description="Run evaluation on the LegalFinance RAG system"
    )
    
    parser.add_argument(
        "--domain",
        type=str,
        choices=["tax", "finance", "legal", "all"],
        default=None,
        help="Filter questions by domain"
    )
    
    parser.add_argument(
        "--difficulty",
        type=str,
        choices=["easy", "medium", "hard"],
        default=None,
        help="Filter questions by difficulty"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of questions to evaluate"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="evaluation/reports",
        help="Directory to save reports"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "txt", "all"],
        default="all",
        help="Report format"
    )
    
    parser.add_argument(
        "--ci",
        action="store_true",
        help="Run in CI mode (returns exit code based on pass/fail)"
    )
    
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only show summary, don't save reports"
    )
    
    parser.add_argument(
        "--dataset-info",
        action="store_true",
        help="Show dataset information and exit"
    )
    
    args = parser.parse_args()
    
    # Show dataset info
    if args.dataset_info:
        dataset = GoldenDataset()
        print("\n=== Golden Dataset Info ===")
        summary = dataset.summary()
        print(f"Version: {summary['version']}")
        print(f"Total Questions: {summary['total_questions']}")
        print(f"By Domain: {summary['by_domain']}")
        print(f"By Difficulty: {summary['by_difficulty']}")
        print(f"Thresholds: {summary['thresholds']}")
        return 0
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY environment variable not set!")
        return 1
    
    # Run evaluation
    print("\n=== Starting Evaluation ===\n")
    
    evaluator = RAGEvaluator()
    reporter = EvaluationReporter(output_dir=args.output_dir)
    
    # Apply filters
    domain_filter = args.domain if args.domain != "all" else None
    
    result = evaluator.evaluate_all(
        domain_filter=domain_filter,
        difficulty_filter=args.difficulty,
        limit=args.limit
    )
    
    # Print console report
    console_report = reporter.generate_console_report(result)
    print(console_report)
    
    # Save reports
    if not args.summary_only:
        saved_files = reporter.save_report(result, format=args.format)
        print(f"\nReports saved to:")
        for f in saved_files:
            print(f"  - {f}")
    
    # CI mode
    if args.ci:
        ci_output = reporter.generate_ci_output(result)
        print(f"\nCI Summary: {ci_output['summary']}")
        return ci_output["exit_code"]
    
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
