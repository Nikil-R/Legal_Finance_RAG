"""
CLI entry-point for the ingestion pipeline.

Run from the project root:
    python -m app.ingestion.cli
    python -m app.ingestion.cli --clear
"""

import argparse
import sys

from app.ingestion.pipeline import run_ingestion_pipeline


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.ingestion.cli",
        description="Run the LegalFinance RAG document ingestion pipeline.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        default=False,
        help="Clear existing ChromaDB collection before ingesting (default: False).",
    )
    parser.add_argument(
        "--raw-dir",
        default="data/raw",
        metavar="PATH",
        help="Path to the raw documents directory (default: data/raw).",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    summary = run_ingestion_pipeline(
        raw_dir=args.raw_dir,
        clear_existing=args.clear,
    )

    print("\n" + "=" * 50)
    print("  Ingestion Summary")
    print("=" * 50)
    print(f"  Documents loaded  : {summary['documents_loaded']}")
    print(f"  Chunks created    : {summary['chunks_created']}")
    print(f"  Chunks stored     : {summary['chunks_stored']}")
    print(f"  Domain breakdown  : {summary['domain_breakdown']}")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    sys.exit(main())
