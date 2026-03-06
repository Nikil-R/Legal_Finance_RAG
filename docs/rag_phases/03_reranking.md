# Phase 3: Cross-Encoder Reranking

Reranking is a critical step that refines the results from the retrieval phase. While hybrid search is fast, it can sometimes include irrelevant "noise." Reranking uses a more powerful (and computationally expensive) model to sort the final candidates.

## 🏗️ Components

### 1. Cross-Encoder Reranker (`reranker.py`)
- **Model**: Uses a Cross-Encoder (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`).
- **Logic**: Unlike bi-encoders (vectors) which embed query and document separately, a Cross-Encoder processes `(Query, Document Chunk)` pairs together to predict relevance.
- **Goal**: Select the top-5 most relevant chunks from the top-20 candidates provided by retrieval.

### 2. Context Builder (`context_builder.py`)
- **Purpose**: Prepares the final payload for the LLM.
- **Functions**:
  - Dedupes chunks if necessary.
  - Formats chunks into a single string with clear indicators (e.g., `[Source 1]: ...`).
  - Limits context length to avoid token overflow.

## 🔄 Reranking Workflow

1. **Input Generation**: Take the top-20 results from Phase 2.
2. **Scoring**: Run each candidate through the Cross-Encoder model.
3. **Filtering**: Sort by score and keep only the top `TOP_K_RERANK` (default: 5) chunks.
4. **Final Selection**: Discard chunks that fall below a certain relevance threshold (`GUARDRAIL_MIN_TOP_SCORE`).

## 💡 Why Rerank?
- **Hybrid Retrieval** provides a high-recall "bucket" of information.
- **Reranking** provides high-precision "filtering" to ensure the LLM receives only the most accurate context, reducing hallucinations.
