"""
Demo script for the retrieval + re-ranking pipeline.

Run from the project root (after ingestion):
    python -m app.reranking.demo
"""

from __future__ import annotations

import time

from app.reranking import RetrievalPipeline


def main() -> None:
    print("=== LegalFinance RAG — Retrieval + Reranking Demo ===\n")
    print("Loading models (first run will download cross-encoder) …\n")

    t0 = time.time()
    pipeline = RetrievalPipeline()
    print(f"Pipeline initialised in {time.time() - t0:.2f}s\n")

    test_queries = [
        ("What deductions are available under Section 80C?", "tax"),
        ("What are the KYC requirements for banks in India?", "finance"),
        ("What constitutes free consent in a contract?", "legal"),
        ("What are the penalties for non-compliance with regulations?", "all"),
        ("xyzzy gibberish nonsense query", "all"),  # graceful failure
    ]

    for query, domain in test_queries:
        print(f"Query : {query}")
        print(f"Domain: {domain}")
        print("-" * 60)

        result = pipeline.run(query, domain=domain)

        if result["success"]:
            print(
                f"✓ Found {result['candidates_found']} candidates, "
                f"reranked to {result['candidates_reranked']}"
            )
            print(f"  Top score : {result['top_score']:.4f}")
            print(f"  Time      : {result['total_time_ms']:.0f} ms")

            preview = result["context"]
            print(f"\nContext preview:\n{preview[:500]}{'…' if len(preview) > 500 else ''}")

            print("\nSources:")
            for src in result["sources"]:
                print(
                    f"  [{src['reference_id']}] {src['source']} "
                    f"({src['domain']}) — score: {src['rerank_score']:.4f}"
                )
        else:
            print(f"✗ Failed : {result['error']}")
            print(f"  Candidates found: {result['candidates_found']}")

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
