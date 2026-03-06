# Phase 3: Cross-Encoder Reranking

Retrieval (Phase 2) is great at finding a broad set of candidates (high recall), but it isn't always accurate (low precision). It might retrieve 20 chunks, but only 2 of them actually contain the numerical data needed to answer a specific tax question. 

Reranking is the "Precision Filter" of our RAG pipeline.

## 🏗️ Deep Dive: Bi-Encoders vs. Cross-Encoders

To understand reranking, we must distinguish between the two types of transformer models used:

| Feature | Bi-Encoder (Phase 2) | Cross-Encoder (Phase 3) |
|---|---|---|
| **Usage** | Creating Vectors (Similarity Search) | Scoring (Query, Chunk) pairs |
| **Input** | Encodes Query and Doc separately | Encodes Query and Doc *together* |
| **Speed** | Fast (can use pre-computed vectors) | Slow (must process pairs at runtime) |
| **Accuracy** | Good for broad matching | Excellent for semantic relevance |

### 1. The Reranker Model (`reranker.py`)
We use `cross-encoder/ms-marco-MiniLM-L-6-v2`. This model has been trained specifically on the MS MARCO dataset to predict whether a short "passage" successfully answers a given "query."

- **Joint Attention**: Because the query and chunk are processed in the same transformer block, the model can "see" how specific words in the query change the meaning of words in the chunk.
- **Scoring**: It produces a logit score (typically -10 to +10). A score > 0 typically indicates high relevance, while > 2.0 indicates an extremely strong match.

### 2. Intelligent Thresholding & Guardrails
Reranking acts as a security layer. If the best reranked score for a query is very low (e.g., < 0.15), it indicates that **the system does not have the documents needed to answer the question.**
- **Automatic Refusal**: Instead of letting the LLM hallucinate based on weak data, the pipeline can detect this low score and trigger a "No relevant information found" response.

### 3. Context Construction (`context_builder.py`)
Once we have our top 5 reranked chunks:
- **Formatting**: They are formatted into a clean string for the LLM.
- **Reference Tagging**: Each chunk is tagged with its source index (e.g., `[Source ID: 1]`).
- **Token Management**: The context builder ensures the final prompt stays within the context window of the generation model (typically 8k-128k tokens depending on the Groq model used).

## 🔄 The Reranking Workflow

1.  **Input**: Receive top 20 candidate chunks from Hybrid Retrieval.
2.  **Pairing**: Create 20 pairs of `(Query, Chunk Content)`.
3.  **Inference**: Run all 20 pairs through the Cross-Encoder model.
4.  **Sorting**: Sort descending by the Cross-Encoder score.
5.  **Pruning**: 
    - Keep only the top `TOP_K_RERANK` (default: 5).
    - Throw away anything below `GUARDRAIL_MIN_TOP_SCORE`.
6.  **Output**: Hand off the 5 most "factually dense" chunks to the LLM.

## 💡 Why 5 Chunks?
Research shows that providing more than 5-10 chunks to an LLM can lead to "lost in the middle" effects, where the model ignores information in the center of the context. By reranking down to the best 5, we maximize the LLM's focus on the most relevant data.
