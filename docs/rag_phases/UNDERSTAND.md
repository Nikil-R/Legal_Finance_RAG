# UNDERSTAND.md

Implementation-accurate system understanding for `legal_finance_rag` (codebase inspected on March 11, 2026).

## 1. Project Overview

This project is a production-oriented Retrieval Augmented Generation (RAG) system for legal, tax, and finance question answering.

Core goal:
- Answer user questions with grounded evidence from indexed documents.
- Return source-backed responses with citation markers and a mandatory disclaimer.
- Support both system corpus documents and per-user uploaded documents (session-isolated).

Problem it solves:
- Legal/finance questions are high risk for hallucination.
- Pure LLM answers are hard to trust and audit.
- This system adds retrieval, reranking, validation, and policy guardrails so answers are evidence-linked and operationally measurable.

Domain scope in implementation:
- `tax`
- `finance`
- `legal`
- `all` (cross-domain)

## 2. System Architecture

### 2.1 High-Level Architecture

```text
User
  |
  v
Next.js Frontend (frontend-nextjs)
  |
  v
FastAPI API (app/main.py)
  |
  +--> Auth + RBAC + Rate limiting + Middleware + PII redaction
  |
  v
RAGPipeline (app/generation/pipeline.py)
  |
  +--> RetrievalPipeline (app/reranking/pipeline.py)
  |      |
  |      +--> Query rewrite (optional)
  |      +--> Hybrid retrieval:
  |      |      - VectorRetriever (Chroma + sentence-transformers)
  |      |      - BM25Retriever (rank-bm25 over Chroma docs)
  |      |      - RRF fusion
  |      +--> Cross-encoder reranking
  |      +--> ContextBuilder
  |
  +--> GuardrailEngine (input/retrieval/output checks)
  +--> RAGGenerator
         |
         +--> PromptManager (YAML prompt version)
         +--> Groq LLM client (Llama model)
         +--> ResponseValidator
         +--> CitationMapper (claim/source highlight spans)
  |
  v
Final response with answer + sources + metadata + validation
```

### 2.2 Required RAG Flow (as implemented)

```text
User Query
  -> Frontend capture (useChat hook)
  -> API /api/v2/query
  -> Query preprocessing (PII redaction, ownership check, auth)
  -> Query rewriting (optional)
  -> Embedding generation for query (dense path)
  -> Vector database retrieval (Chroma cosine)
  -> BM25 retrieval (lexical path)
  -> RRF fusion
  -> Cross-encoder reranking
  -> Context assembly + source metadata
  -> Prompt construction
  -> LLM generation (Groq)
  -> Output validation + disclaimer enforcement + citation mapping
  -> Final response to UI
```

### 2.3 Secondary Architecture: Ingestion

- System ingestion endpoint (`/api/v1|v2/documents/ingest`) enqueues async ingestion.
- User upload endpoint (`/api/v1|v2/user/upload`) enqueues async per-session ingestion.
- Queue backend is configurable:
  - `local` thread pool
  - `celery` worker (if broker configured)
  - `auto` (choose celery when broker URL exists; else local)

## 3. Technology Stack

### 3.1 Programming Language
- Python 3.11+ (backend pipeline and APIs)
- TypeScript/React (frontend)

### 3.2 Backend Frameworks
- FastAPI: API routing, schema-driven interfaces, dependency injection.
- Pydantic + pydantic-settings: typed request/response models and env config.
- Uvicorn: ASGI runtime.

### 3.3 Retrieval and RAG Libraries
- ChromaDB: persistent local vector store (`PersistentClient`).
- sentence-transformers:
  - Embedding model: `sentence-transformers/all-MiniLM-L6-v2`
  - Reranker model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- rank-bm25: sparse keyword retrieval over tokenized chunk corpus.
- LangChain text splitter (`RecursiveCharacterTextSplitter`): chunking.

### 3.4 LLM and Prompting
- Groq Python SDK:
  - Default model: `llama-3.1-8b-instant` (configurable).
- YAML prompt versioning (`app/prompts/system_prompt_v1.yaml`) via `PromptManager`.

### 3.5 Frontend Stack
- Next.js 15 + React 19 + TypeScript.
- Tailwind CSS + Radix UI primitives.
- react-markdown + remark-gfm for formatted assistant responses.
- react-dropzone for file upload UX.

### 3.6 Infrastructure, Deployment, and Ops
- Dockerfiles for API and frontend containers.
- GitHub Actions:
  - CI (lint/test/security/build/evaluation gate)
  - deploy workflow (build/push, ECS update for production)
  - scheduled evaluation workflow
- Redis (optional):
  - distributed cache
  - distributed rate-limiter storage
  - async ingestion job state storage fallback target
- Celery (optional):
  - background ingestion workers
- Prometheus/Grafana configs for monitoring stack.

### 3.7 Why these technologies were chosen (in code behavior)
- Hybrid retrieval (dense + BM25) improves recall for both semantic and exact legal references.
- Cross-encoder reranking improves precision before LLM generation.
- ChromaDB persistent client keeps deployment simple for local/small-prod use.
- FastAPI provides clear typed APIs and operational middleware hooks.
- Next.js provides a richer web UI than prior documented Streamlit/Chainlit paths.
- Redis/Celery are optional so local setup works without full distributed infra.

## 4. Project Folder Structure

Top-level structure and purpose:

- `app/`
  - Core backend code.
  - `api/`: routes, auth, dependencies, middleware, rate limits.
  - `ingestion/`: loading, chunking, embedding, ingestion orchestration.
  - `retrieval/`: vector search, BM25 search, RRF, query rewrite.
  - `reranking/`: cross-encoder reranking and context builder.
  - `generation/`: guardrails, LLM client, response validator, top-level RAG pipeline.
  - `prompts/`: versioned prompt YAML and manager.
  - `infra/`: Redis store and async job stores.
  - `observability/`: logging, metrics, tracing bridge.
  - `utils/`: cache, PII redaction, session ownership, secret manager, lightweight fallback models.

- `frontend-nextjs/`
  - Next.js UI.
  - `app/`: root page/layout.
  - `components/`: chat UI, sources panel, sidebar upload UX, settings, markdown renderer.
  - `hooks/`: `useChat`, `useHealth`, `useFileUpload`.
  - `lib/`: API client and shared types.

- `data/`
  - `core/`: default ingestion source path used by pipeline (`data/core`).
  - `raw/`: larger domain dataset source tree and downloaded corpora.
  - `user_uploads/`: persisted per-session uploaded files.
  - `user_upload_jobs/`: staged upload files for async job workers.
  - `chroma/`: additional persisted Chroma artifacts.

- `chroma_db/`
  - Default Chroma persistence path used at runtime (`settings.CHROMA_PERSIST_DIR`).

- `evaluation/`
  - Golden dataset, metric scorers, evaluator, reporters, CLI runner.

- `tests/`
  - Unit, integration, security, load, and API tests (mixed maturity; some legacy expectations).

- `docker/`
  - Compose files and Dockerfiles for API/frontend/monitoring.

- `docs/`
  - Operations, security/compliance docs, and generated theory-first RAG phase docs.

- `scripts/`
  - Ingestion/evaluation wrappers, health checks, load test, backup/cleanup utilities, doc generation scripts.

## 5. Data Pipeline

Implemented ingestion flow (`app/ingestion/pipeline.py`):

1. Document loading:
- `DocumentLoader.load_directory(raw_dir)` recursively scans files.
- Supported system formats: `.pdf`, `.txt`.
- Domain is inferred from first relative folder under `raw_dir`.

2. Text extraction:
- PDF via `pypdf.PdfReader` per page.
- TXT via UTF-8 read with `errors="ignore"`.

3. Text cleaning/chunking strategy:
- `RecursiveCharacterTextSplitter`.
- Defaults:
  - `CHUNK_SIZE=1024`
  - `CHUNK_OVERLAP=200`
- Separators order: paragraph, line, sentence-ish, word, fallback char.

4. Metadata creation:
- Per document:
  - `source`, `domain`, `file_path`
- Per chunk:
  - `chunk_index`
  - deterministic `chunk_id` (`<source_sanitized>_chunk_<n>`)

5. Embedding generation:
- Batch encoding with sentence-transformers.
- Normalized embeddings for cosine-like behavior.

6. Vector database storage:
- Upsert into Chroma collection `legal_finance_docs`.
- Metadata and raw chunk text are stored with embeddings.

Async ingestion wrappers:
- System docs: `/documents/ingest` -> job queue -> `run_ingestion_pipeline`.
- User docs: `/user/upload` -> staged file -> async worker -> session-specific collection.

## 6. Embedding Pipeline

### 6.1 Embedding model used
- Default: `sentence-transformers/all-MiniLM-L6-v2`.
- Loaded via helper `load_sentence_encoder`.

### 6.2 Generation process
- `VectorStoreManager.embed_and_store()` batches chunks.
- Embedding params:
  - `batch_size=256`
  - `normalize_embeddings=True`
  - `convert_to_numpy=True`

### 6.3 Chunk-to-vector conversion
- Input text chunks come from `DocumentChunker`.
- Each chunk produces one vector and one `id` (`chunk_id`).

### 6.4 Storage details
- Chroma upsert batch size: 500.
- Collection metadata uses cosine space (`{"hnsw:space": "cosine"}`).
- Dedup behavior:
  - By default checks existing IDs and skips duplicates.
  - If collection was just cleared, skip dedup check for speed.

### 6.5 Fallback behavior
- If transformer models fail to load, code falls back to deterministic local lightweight models:
  - Hash-based sentence encoder (384-dim).
  - Lexical-overlap cross-encoder fallback.

## 7. Vector Database

### 7.1 Database used
- ChromaDB `PersistentClient` (local persistence path, default `./chroma_db`).

### 7.2 Indexing behavior
- Collection name (system corpus): `legal_finance_docs`.
- Session collections (user docs): `user_docs_<session_id>`.
- IDs are deterministic chunk IDs from chunk metadata.

### 7.3 Similarity search
- Dense search uses query embedding and Chroma `query(...)`.
- Domain filter for system docs uses metadata `where={"domain": {"$eq": ...}}`.
- Distance-to-score conversion:
  - `score = 1 / (1 + distance)` where Chroma returns cosine distance.

### 7.4 Retrieval output shape
- Returned fields include:
  - `chunk_id`, `content`, `metadata`, `score`, `source="vector"`

## 8. Retrieval System

### 8.1 Retriever architecture
- `HybridRetriever` orchestrates:
  - VectorRetriever (dense semantic)
  - BM25Retriever (sparse lexical)
  - UserDocumentRetriever (session-isolated personal docs)
  - RRF fusion

### 8.2 Top-k retrieval
- System retrieval default in pipeline: `retrieval_top_k=20`.
- Rerank output default: `rerank_top_k=5`.
- Retrieval-only API accepts `top_k` (1 to 20) for reranked output count.

### 8.3 Similarity/keyword logic
- Dense path:
  - Query embedding against Chroma vectors.
- Sparse path:
  - Builds BM25 index from Chroma corpus on demand.
  - Tokenization by non-alphanumeric split, min token length 2.
  - Filters by domain when requested.

### 8.4 Query embedding generation
- Query text is embedded by same embedding model as documents.

### 8.5 Query rewriting
- If enabled (`ENABLE_QUERY_REWRITE=true`):
  - query normalized/lowercased
  - domain hint terms injected
  - alias expansion for terms like `80c`, `gst`, `kyc`, `tds`, `rbi`, `sebi`

### 8.6 Fusion
- Reciprocal Rank Fusion (RRF), `k=60`:
  - Combines ranks from vector and BM25 lists.
  - Boosts chunks found by both retrieval methods.

## 9. Reranking System

### 9.1 Why reranking is used
- Retrieval prioritizes recall.
- Reranking improves precision by scoring full `(query, chunk)` pairs.

### 9.2 Reranker model
- Default cross-encoder:
  - `cross-encoder/ms-marco-MiniLM-L-6-v2`

### 9.3 Reranking process
- For each candidate:
  - create `(query, content)` pair
  - predict relevance score
  - add `rerank_score`
- Sort descending and keep top-N.

### 9.4 Selection threshold
- `rerank_with_threshold` drops chunks below `min_score` (default 0.1 in RetrievalPipeline).
- If no chunk passes threshold, pipeline returns safe retrieval failure.

## 10. Context Construction

Context assembly is handled by `ContextBuilder`.

### 10.1 Formatting
- Each chunk is rendered as:
  - `[n] Source: <file> | Origin: <System/User Upload> | Domain: <domain>`
  - followed by chunk text

### 10.2 Source payload
- For each context item:
  - `reference_id`, `chunk_id`, `source`, `domain`, `origin`, `rerank_score`, `content`, `excerpt`

### 10.3 Limits
- Context size is constrained by character count, not token count.
- `max_context_length=3000` characters.
- If exceeded:
  - context is truncated
  - suffix added: `... [truncated]`

### 10.4 Token-related generation limits
- Prompt YAML sets `max_tokens: 2048` for completion.
- LLM response includes token usage metadata (prompt/completion/total).

## 11. LLM Generation

### 11.1 LLM used
- Groq chat completion client.
- Default model: `llama-3.1-8b-instant` (configurable).

### 11.2 Prompt construction
- System prompt and user template loaded from versioned YAML (`system_prompt_v1.yaml`).
- User prompt injects:
  - assembled context
  - question
  - generation instructions.

### 11.3 Answer generation
- `GroqClient.generate()` with retry/backoff/timeout controls:
  - `LLM_REQUEST_TIMEOUT_SECONDS`
  - `LLM_MAX_RETRIES`
  - `LLM_RETRY_BACKOFF_SECONDS`

### 11.4 Hallucination and safety reduction
- Multi-layer controls:
  - Input guardrails (prompt-injection and illegal intent detection).
  - Retrieval guardrails (minimum evidence strength/quantity).
  - Output guardrails (validation and unsafe-claim checks).
  - ResponseValidator checks citations/disclaimer/refusal patterns.
  - Disclaimer auto-appended if missing.
  - CitationMapper links claims to source excerpt spans for UI transparency.

## 12. Frontend System

Implementation is Next.js-based (not Streamlit/Chainlit runtime code).

### 12.1 UI layer
- Main page (`frontend-nextjs/app/page.tsx`) composes:
  - Header/status
  - Sidebar (upload)
  - Chat area
  - Sources panel
  - Input composer

### 12.2 Query capture
- `useChat` hook:
  - creates session UUID client-side.
  - on send:
    - appends user message
    - shows typing placeholder
    - calls `POST /api/v2/query` via `sendQuery(question, sessionId)`.

### 12.3 Response display
- Assistant output rendered via Markdown (`react-markdown`).
- Citation badges `[n]` are interactive in markdown renderer.
- Sources panel shows latest assistant message sources:
  - filename/domain
  - excerpt
  - confidence bar from `relevance_score`.

### 12.4 Upload UX
- Sidebar drag/drop upload to `/api/v2/user/upload`.
- Progress and local upload status shown in UI.

## 13. End-to-End Query Flow

1. User enters query in chat input.
2. Frontend sends request to `/api/v2/query` with `question` and `session_id`.
3. API authenticates request (unless auth disabled), applies middleware/rate limits.
4. Query text is PII-redacted when configured.
5. Session ownership is checked if `session_id` present.
6. RAGPipeline input guardrails run.
7. Query cache is checked (domain+owner+session+question hash key).
8. RetrievalPipeline rewrites query (if enabled).
9. Dense vector search runs on Chroma.
10. BM25 search runs over indexed corpus.
11. User session collection retrieval is also attempted when session exists.
12. RRF fuses ranked lists.
13. Cross-encoder reranks fused candidates and filters by threshold.
14. ContextBuilder creates formatted context and source references.
15. Retrieval guardrails validate evidence sufficiency.
16. PromptManager builds system/user prompts from YAML.
17. Groq model generates answer.
18. ResponseValidator checks citation/disclaimer/refusal.
19. Output guardrails validate final safety/compliance.
20. CitationMapper adds source highlight spans.
21. Final response is returned with answer, sources, validation, metadata.
22. Frontend replaces typing indicator with assistant message and source panel.

## 14. Performance Considerations

### 14.1 Retrieval speed
- Vector retrieval is fast for semantic matching via Chroma.
- BM25 index is built from Chroma data and cached by docs hash.
- Hybrid + RRF increases quality but adds compute.

### 14.2 Embedding efficiency
- Embedding batch size (`256`) and Chroma upsert batch (`500`) reduce overhead.
- Dedup by chunk ID avoids repeated embedding work during re-ingestion.

### 14.3 Reranking tradeoff
- Cross-encoder gives better relevance than pure retrieval scores.
- It is CPU-heavy; top-K retrieval cap and rerank top-N reduce cost.

### 14.4 Context optimization
- Context truncation currently uses fixed char length (3000 chars), not tokenizer-aware budgeting.
- Completion limit (`max_tokens`) is applied at LLM call level.

### 14.5 Caching and resilience
- Query response cache (local TTL, optional Redis-backed) reduces repeated LLM calls.
- Local fallback models allow degraded operation when transformer models are unavailable.
- Async ingestion offloads expensive indexing from request path.

## 15. Limitations and Future Improvements

### 15.1 Current implementation limitations

- Frontend upload session mismatch:
  - Chat uses client-generated session ID.
  - Upload API call does not pass chat session ID.
  - Uploaded docs may land in a different session collection than query retrieval uses.

- Config values partly not wired into hot path:
  - `settings.TEMPERATURE`, `TOP_K_RETRIEVAL`, `TOP_K_RERANK` are exposed but query path relies on hardcoded pipeline defaults in several places.

- Domain labeling risk in default ingestion source:
  - Pipeline defaults to `data/core`.
  - Most files there are root-level (no domain folder), so domain becomes `unknown`.
  - Domain-filtered queries can lose recall for those documents.

- Deployment/doc drift:
  - Some docs/scripts still reference Streamlit/Chainlit and missing files (`chainlit_app`, `Dockerfile.chainlit`), while active frontend is Next.js.

- Frontend/backend policy mismatch risk:
  - Backend auth defaults to enabled.
  - Frontend API client does not attach API key headers by default.
  - Works only when auth disabled or external key injection is configured.

- Context budget is character-based, not token-based.
- `useHealth` is used in multiple components, causing duplicate polling.

### 15.2 Recommended future improvements

Better rerankers:
- Evaluate stronger cross-encoders or domain-finetuned rerankers.
- Add latency-aware reranker model selection.

Hybrid search improvements:
- Keep current dense+sparse retrieval, then add weighted fusion tuning and query-intent-based dynamic weighting.

Multi-vector retrieval:
- Add document-level + section-level + clause-level embeddings.
- Consider late interaction models for legal references.

Agent-based RAG:
- Add tool-using orchestration for:
  - statute lookup
  - amendment recency checks
  - citation verification workflows.

Evaluation pipeline hardening:
- Keep golden set gate; add production trace replay benchmarks.
- Add regression dashboards that compare retrieval/reranking/generation separately.
- Add automated checks for session upload/query linkage correctness.

Token-aware context packing:
- Replace char truncation with tokenizer-aware packing and per-source budget allocation.

Deployment consistency:
- Remove stale Chainlit/Streamlit artifacts or restore missing files.
- Align Docker compose, Makefile, Quickstart, and README with one canonical runtime path.

