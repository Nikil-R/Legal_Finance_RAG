# RAG Process Documentation (Theory-First)

This directory explains the full Retrieval-Augmented Generation (RAG) pipeline in a
theoretical, system-design oriented way.

RAG is easiest to understand as two coupled pipelines:

1. `Offline indexing pipeline` (build knowledge memory):
   - Parse and normalize source documents
   - Chunk content into retrieval units
   - Create search indexes (dense and/or sparse)
2. `Online question-answering pipeline` (serve a user query):
   - Retrieve candidate evidence
   - Rerank by fine-grained relevance
   - Generate an answer constrained by retrieved evidence
   - Measure quality and monitor failures

## Phase Map

1. **[Phase 0: Architecture Blueprint](./00_architecture.md)**  
   End-to-end production architecture that connects phases 1 through 5.

2. **[Phase 1: Ingestion](./01_ingestion.md)**  
   How raw legal or financial content becomes a clean, structured knowledge base.

3. **[Phase 2: Retrieval](./02_retrieval.md)**  
   How candidate evidence is fetched with dense, sparse, or hybrid search.

4. **[Phase 3: Reranking](./03_reranking.md)**  
   How coarse retrieved candidates are reordered into high-precision context.

5. **[Phase 4: Generation and Guardrails](./04_generation.md)**  
   How the LLM generates grounded answers with citation and policy constraints.

6. **[Phase 5: Evaluation](./05_evaluation.md)**  
   How to measure retrieval quality, grounding quality, answer quality, and reliability.

## End-to-End Dataflow

1. `Documents` -> parsing, cleanup, metadata enrichment.
2. `Normalized text` -> chunking and indexing.
3. `User query` -> retrieval of top-K candidates.
4. `Candidates` -> reranking to top-N evidence.
5. `Evidence + query` -> constrained generation.
6. `Answer + traces` -> automated and human evaluation.

For project setup and execution details, see [README](../../README.md).
