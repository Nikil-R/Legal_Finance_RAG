# Phase 2: Hybrid Retrieval

The Retrieval phase finds the most relevant document chunks based on a user's query. This system uses a **Hybrid Search** strategy to combine the strengths of semantic understanding and keyword matching.

## 🏗️ Components

### 1. Query Rewriting (`query_rewriter.py`)
- **Purpose**: Enhances the user's raw query before retrieval.
- **Logic**: Uses a lightweight LLM prompt to expand abbreviations (e.g., "IT Act" -> "Income Tax Act") and focus on domain-specific terminology.

### 2. Semantic Search (`vector_search.py`)
- **Engine**: ChromaDB.
- **Mechanism**: Calculates the cosine similarity between the query embedding and stored document embeddings.
- **Strength**: Captures conceptual meaning even if exact words don't match.

### 3. Keyword Search (`bm25_search.py`)
- **Engine**: Rank-BM25.
- **Mechanism**: Traditional TF-IDF based keyword search.
- **Strength**: Handles precise legal terms, section numbers, and specific statutory names that vector models might overlook.

### 4. Reciprocal Rank Fusion (`fusion.py`)
- **Mechanism**: A mathematical formula to merge ranked lists from Vector and BM25 search.
- **Formula**: `1 / (rank + k)` where `k=60`.
- **Outcome**: A single, unified list of the top-N retrieved chunks sorted by a balanced relevance score.

## 🔄 Retrieval Workflow

1. **Query Expansion**: The raw query is rewritten for better domain alignment.
2. **Parallel Search**:
   - Query ChromaDB for top-20 semantic matches.
   - Query BM25 index for top-20 keyword matches.
3. **RRF Fusion**: Merge the results into a single list of candidate chunks.
4. **Filtering**: If a specific domain (Tax/Finance/Legal) is requested, results are filtered to match.

## ⚙️ Configuration
- `TOP_K_RETRIEVAL`: Number of chunks returned (default: 20).
- `ENABLE_QUERY_REWRITE`: Toggle query expansion (default: true).
