# Phase 1: Ingestion Pipeline

The Ingestion phase is responsible for transforming raw legal and financial documents into a searchable vector database. This phase ensures that the system has a high-quality, structured representation of the knowledge base.

## 🏗️ Components

### 1. Document Loading (`loader.py`)
- **Purpose**: Reads source files from `data/raw/` in various formats (`.pdf`, `.txt`).
- **Domain Awareness**: Automatically categorizes documents into **Tax**, **Finance**, and **Legal** domains based on their folder structure.
- **Metadata Extraction**: Captures essential metadata like filename, page numbers, and domain for each document.

### 2. Document Chunking (`chunker.py`)
- **Strategy**: Uses a character-based splitter with overlapping windows.
- **Configuration**:
  - `CHUNK_SIZE`: 512 characters (default).
  - `CHUNK_OVERLAP`: 50 characters (default).
- **Goal**: Ensures that chunks are small enough for precise retrieval while maintaining enough context across chunk boundaries.

### 3. Embedding & Vector Storage (`embedder.py`)
- **Model**: Uses `sentence-transformers/all-MiniLM-L6-v2` (or configured model) provided by HuggingFace.
- **Vector DB**: ChromaDB is used for persistent storage of embeddings and metadata.
- **Optimization**: Implements batch processing for faster ingestion and logic to skip redundant data.

## 🔄 Ingestion Workflow

1. **Scan Directory**: Iterate through `data/raw/{domain}` folders.
2. **Read Content**: Extract text and metadata from files.
3. **Split Text**: Break documents into overlapping chunks.
4. **Generate Embeddings**: Convert text chunks into numerical vectors.
5. **Index in ChromaDB**: Store vectors alongside their original text and metadata for retrieval.

## 🛠️ Usage

To trigger the ingestion pipeline:
```bash
make ingest-clear
```
This command clears the existing database and re-indexes all documents in the `data/raw` directory.
