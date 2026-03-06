# Phase 2: Hybrid Retrieval

Retrieval is the process of finding the most relevant information for a user's question. In legal and financial contexts, standard "Vector Search" (Semantic Search) is often not enough because users frequently search for specific section numbers (e.g., "Section 80C") or precise legal terms that vector models might treat as conceptually similar to other sections.

To solve this, LegalFinance RAG uses a **Hybrid Search** architecture.

## 🏗️ The Hybrid Components

### 1. Query Expansion & Rewriting (`query_rewriter.py`)
User queries are often ambiguous or informal (e.g., "gst rules for startups"). Before searching, the system uses an LLM to:
- **Normalize Terms**: Expand "gst" to "Goods and Services Tax".
- **Extract Domain**: Determine if the query is primarily Tax, Legal, or Financial.
- **Generate Synonyms**: Add keywords that increase the surface area for matching.

### 2. Dense Retrieval: Vector Search (`vector_search.py`)
- **Mechanism**: Converts the (rewritten) query into a vector using the same MiniLM model used during ingestion.
- **Goal**: Find chunks that are "conceptually" related. If a user asks about "tax savings," vector search will find "investment deductions" even if the word "savings" isn't present.
- **Metric**: Cosine Similarity.

### 3. Sparse Retrieval: BM25 Keyword Search (`bm25_search.py`)
- **Mechanism**: Uses the **Rank-BM25 (Okapi)** algorithm. 
- **The Index**: Unlike vector storage, the BM25 index is built on-the-fly from the text in ChromaDB (filtered by domain).
- **Goal**: Handle specific terminology and alphanumeric identifiers. It ensures that "Section 144" retrieves exactly those words.
- **Tokenization**: Splits text on non-alphanumeric characters and filters out very short words to focus on meaningful terms.

### 4. Reciprocal Rank Fusion: Merging the Result sets (`fusion.py`)
Since Vector Search and BM25 produce scores in different ranges (0-1 for vector vs. 0-100+ for BM25), they cannot be compared directly. We use **RRF (Reciprocal Rank Fusion)** to merge them.
- **Formula**: `RRF_score = Σ (1 / (k + rank))`
- **The Logic**: A document found by *both* retrievers at high positions gets a significantly higher "fused" score.
- **Constant `k` (60)**: A standard smoothing factor that prevents low-ranked items from having too much influence while keeping the merging stable.

## 🔄 The Retrieval Workflow

1.  **Incoming Query**: User asks a question (e.g., "What are the penalties for late GST filing?").
2.  **Domain Routing**: (Optional) Filter search to the "Tax" domain if specified.
3.  **Parallel Execution**:
    - **Vector Search** fetches top 20 chunks by semantic similarity.
    - **BM25 Search** fetches top 20 chunks by keyword frequency.
4.  **Deduplication & Fusion**: Merge chunks. If the same chunk appears in both lists, it is boosted.
5.  **Ranking**: Sort by the final RRF score and return the top `TOP_K_RETRIEVAL` results to the next phase.

## ⚙️ Key Configurations
- `TOP_K_RETRIEVAL` (20): The "Recall" phase—how many chunks do we consider?
- `ENABLE_QUERY_REWRITE`: Toggle the LLM-based pre-processing.
- `RRF_K` (60): The balance between vector and keyword prominence.
