"""
Demo script for the FULL RAG Pipeline.
"""

from __future__ import annotations

import os

from app.generation import RAGPipeline


def main() -> None:
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print("\nERROR: GROQ_API_KEY environment variable not set!")
        print("Please set it in your .env file or export it:")
        print("  $env:GROQ_API_KEY='your-api-key-here'  (PowerShell)")
        print("-" * 50)
        return

    print("\n=== LegalFinance RAG — Full Pipeline Demo ===\n")
    print("Initializing pipeline (loading models) …\n")

    pipeline = RAGPipeline()

    test_queries = [
        ("What deductions are available under Section 80C of the Income Tax Act?", "tax"),
        ("What are the KYC requirements mandated by RBI for banks?", "finance"),
        ("What constitutes free consent under the Indian Contract Act?", "legal"),
        ("What are the penalties for non-compliance?", "all"),
        ("What is the recipe for making pasta?", "all"),  # Should refuse - irrelevant
    ]

    for question, domain in test_queries:
        print(f"{'='*70}")
        print(f"QUESTION: {question}")
        print(f"DOMAIN  : {domain}")
        print(f"{'='*70}\n")

        result = pipeline.run(question, domain=domain)

        if result["success"]:
            print("ANSWER:")
            print(result["answer"])
            print(f"\n{'─'*50}")
            print("SOURCES:")
            for src in result["sources"]:
                score = src.get("relevance_score", "N/A")
                if isinstance(score, float):
                    score_str = f"{score:.4f}"
                else:
                    score_str = str(score)
                print(f"  [{src['reference_id']}] {src['source']} ({src['domain']}) — score: {score_str}")
            print(f"\n{'─'*50}")
            print("METADATA:")
            meta = result["metadata"]
            print(f"  Retrieval: {meta['retrieval_candidates']} candidates -> {meta['reranked_chunks']} chunks")
            print(f"  Top relevance score: {meta['top_relevance_score']:.4f}")
            print(f"  Model: {meta['model']}")
            print(f"  Tokens: {meta['token_usage']}")
            print(f"  Time: {meta['total_time_ms']:.0f} ms")
            print(f"\n{'─'*50}")
            print("VALIDATION:")
            val = result["validation"]
            print(f"  Overall valid: {val['overall_valid']}")
            print(f"  Citations found: {val['citations']['citations_found']}")
            print(f"  Has disclaimer: {val['disclaimer']['has_disclaimer']}")
            if val.get("issues"):
                print(f"  Issues: {val['issues']}")
        else:
            print(f"FAILED: {result.get('error', 'Unknown error')}")
            if "answer" in result:
                print(f"FALLBACK ANSWER: {result['answer']}")

        print("\n")

    print("Demo complete!")


if __name__ == "__main__":
    main()
