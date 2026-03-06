# Phase 1: Ingestion Pipeline

The Ingestion phase is the foundation of the LegalFinance RAG system. It is responsible for processing complex legal and financial documents—often in PDF format—into high-quality, searchable vector representations sitting in a persistent database.

## 🏗️ Deep Dive into Components

### 1. Advanced Document Loading (`loader.py`)
- **Format Support**: The system uses `PyPDF2` for structural text extraction from PDFs and standard UTF-8 reading for `.txt` files.
- **Hierarchical Domain Mapping**: Documents are not just loaded; they are categorized based on their filesystem location under `data/raw/`.
    - `data/raw/tax/` -> Domain: **Tax**
    - `data/raw/finance/` -> Domain: **Finance**
    - `data/raw/legal/` -> Domain: **Legal**
- **Robustness**: The loader includes error handling for corrupted PDF pages and empty files, ensuring the pipeline doesn't crash on "dirty" data.

### 2. Intelligent Document Chunking (`chunker.py`)
- **Recursive Splitting**: We use LangChain's `RecursiveCharacterTextSplitter`. Unlike a simple split, this attempts to break text at natural boundaries like double newlines (`\n\n`), single newlines, or periods, which is critical for legal clauses and financial sections.
- **Configurable Context Windows**:
    - `CHUNK_SIZE` (512): Small enough to fit in the model's token limit (MiniLM has a 256-512 token limit).
    - `CHUNK_OVERLAP` (50): Ensures that sentences split across chunks are "bridged," preventing loss of context at the edges.
- **Unique Identification**: Every chunk is assigned a deterministic `chunk_id` (e.g., `income_tax_act_chunk_42`) based on the source filename and its index. This allows for idempotent updates.

### 3. High-Performance Embedding (`embedder.py`)
- **The Model**: Uses `sentence-transformers/all-MiniLM-L6-v2`. It is chosen for its excellent balance of speed and semantic accuracy for English text.
- **Parallel Processing**: The embedder initializes a **Multi-process pool**. On multi-core systems, this distributes the heavy mathematical work of vector generation across all available CPUs, drastically reducing ingestion time for large datasets.
- **Batching**: Data is processed in batches (default: 1000) to optimize memory usage and database transaction speed.

### 4. Vector Storage: ChromaDB
- **Indexing**: We use ChromaDB's `PersistentClient` to ensure data survives restarts.
- **HNSW & Cosine Similarity**: The collection is configured with `hnsw:space: "cosine"`. This uses the Hierarchical Navigable Small World algorithm for lightning-fast approximate nearest neighbor (ANN) searches.
- **Idempotency**: The system implements an `upsert` logic. If you run ingestion twice, it checks for existing `chunk_id`s and skips them, saving time and API costs.

## 🔄 The Ingestion Workflow

1.  **Crawl**: Recursively scan `data/raw/` for supported files.
2.  **Extract**: Pull raw text and attach metadata (source, domain, file_path).
3.  **Chunk**: Break the text into 512-character overlapping segments.
4.  **Vectorize**: Convert text segments into 384-dimensional dense vectors.
5.  **Persist**: Store the `(Vector, Text, Metadata)` triplets in ChromaDB.

## 🛠️ Operational Commands

To perform a clean ingestion (wipes old data):
```bash
make ingest-clear
```

To update with new documents (skips existing):
```bash
make ingest
```
