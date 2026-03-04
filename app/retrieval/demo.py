"""
Quick interactive demo of the hybrid retrieval system.

Run from the project root (after ingestion):
    python -m app.retrieval.demo
"""

from __future__ import annotations

from app.retrieval import HybridRetriever


def main() -> None:
    retriever = HybridRetriever()

    print("\n=== LegalFinance RAG — Retrieval Demo ===\n")
    print(f"Index stats: {retriever.get_stats()}\n")

    test_queries = [
        ("What are the deductions under Section 80C?", "tax"),
        ("What are KYC requirements for banks?", "finance"),
        ("What is free consent in contract law?", "legal"),
        ("What are the penalties for non-compliance?", "all"),
    ]

    for query, domain in test_queries:
        print(f"Query : {query}")
        print(f"Domain: {domain}")
        print("-" * 60)

        results = retriever.retrieve(query, domain=domain, top_k=3)

        if not results:
            print("  (no results returned)\n")
        else:
            for i, result in enumerate(results, 1):
                print(
                    f"\n  [{i}] RRF score: {result['rrf_score']:.4f} | "
                    f"Found by: {result['found_by']}"
                )
                print(
                    f"       Source: {result['metadata'].get('source', '?')} | "
                    f"Domain: {result['metadata'].get('domain', '?')}"
                )
                print(f"       Content: {result['content'][:150]}…")

        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
