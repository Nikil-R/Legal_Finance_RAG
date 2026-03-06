# RAG Phases Documentation

This directory contains detailed explanations for each phase of the LegalFinance RAG system.

1.  **[Phase 1: Ingestion](./01_ingestion.md)** - How documents are loaded, chunked, and stored in the vector database.
2.  **[Phase 2: Retrieval](./02_retrieval.md)** - Understanding Hybrid Search (Vector + BM25) and Query Rewriting.
3.  **[Phase 3: Reranking](./03_reranking.md)** - Precision filtering using Cross-Encoder models.
4.  **[Phase 4: Generation & Guardrails](./04_generation.md)** - LLM integration, citation mapping, and safety checks.
5.  **[Phase 5: Automated Evaluation](./05_evaluation.md)** - How system quality is monitored using golden datasets and metrics.

---
*For a high-level project overview, see the root [README](../../README.md).*
