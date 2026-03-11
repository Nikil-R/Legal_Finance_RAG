# ⚖️ LegalFinance RAG

An AI-powered Retrieval-Augmented Generation (RAG) system for Indian tax laws, financial regulations, and legal provisions.

![CI](https://github.com/yourusername/legal-finance-rag/workflows/CI/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

## 🌟 Features

- **Hybrid Search**: Combines vector similarity (semantic) and BM25 (keyword) search
- **Cross-Encoder Reranking**: Precise relevance scoring for retrieved documents
- **Grounded Answers**: All responses cite source documents with `[1]`, `[2]` references
- **Domain Filtering**: Search within Tax, Finance, Legal, or All domains
- **Mandatory Disclaimers**: Legal/financial disclaimer on every response
- **Evaluation System**: Automated quality metrics with CI integration
- **Runtime Guardrails**: Input, retrieval, and output safety checks
- **Query Rewriting**: Domain-aware rewrite for stronger hybrid retrieval
- **Source Highlighting**: Citation claim-to-source highlight spans for UI
- **API v2**: Versioned API surface (`/api/v2/...`)
- **Operational Controls**: Rate limiting, API key auth, query cache, metrics endpoint
- **Distributed Runtime Support**: Optional Redis backend for shared cache/rate limiting
- **Prometheus Export**: `/metrics/prometheus` endpoint for observability stacks

## 🏗️ Architecture

```
┌─────────────────────┐     ┌─────────────────┐
│   Chainlit          │────▶│    FastAPI      │
│   Frontend (8501)   │◀────│    Backend      │
│   (Web UI)          │     │    (8000)       │
└─────────────────────┘     └────────┬────────┘
                                     │
         ┌───────────────────────────┼───────────────────────┐
         ▼                           ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Vector Search  │     │  BM25 Search    │     │  Cross-Encoder  │
│  (ChromaDB)     │     │  (rank-bm25)    │     │  Reranking      │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                        ┌─────────────────┐
                        │   RRF Fusion    │
                        └────────┬────────┘
                                 ▼
                        ┌─────────────────┐
                        │   Groq (Llama)  │
                        │  Generation     │
                        └─────────────────┘
```

> **Note:** As of March 2026, the frontend has been migrated from **Streamlit** to **Chainlit** for improved UX and enterprise capabilities. See [CHAINLIT_README.md](CHAINLIT_README.md) for migration details and setup instructions.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Groq API Key ([Get one free](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/legal-finance-rag.git
cd legal-finance-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Running the Application

```bash
# 1. Ingest documents
make ingest-clear

# 2. Start the API server
make run-api

# 3. In another terminal, start the Chainlit frontend
chainlit run chainlit_app/app.py --port 8501

# Open http://localhost:8501 in your browser
```

For detailed Chainlit setup and configuration, see [CHAINLIT_README.md](CHAINLIT_README.md).

### Using Docker

```bash
# Build and start all services
make docker-build
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

## 📁 Project Structure

```
legal_finance_rag/
├── app/                    # FastAPI backend (UNTOUCHED)
│   ├── api/               # API routes and models
│   ├── ingestion/         # Document loading and chunking
│   ├── retrieval/         # Vector + BM25 search
│   ├── reranking/         # Cross-encoder reranking
│   ├── generation/        # LLM generation with Groq
│   └── prompts/           # Versioned prompt templates
├── chainlit_app/          # ✨ Chainlit frontend (NEW)
│   ├── app.py            # Main Chainlit application
│   ├── api_client.py     # HTTP client to backend
│   ├── config.py         # Configuration
│   └── public/           # Branding assets
├── chainlit.md           # Welcome screen markdown
├── frontend/             # [DEPRECATED] Old Streamlit UI (kept for reference)
├── evaluation/           # Golden dataset and metrics
├── data/raw/             # Source documents by domain
├── tests/                # Test suite
└── docker/               # Docker configuration
```

## 📊 Adding Documents

Place documents in the appropriate domain folder:

```
data/raw/
├── tax/          # Tax-related documents (Income Tax Act, GST, etc.)
├── finance/      # Financial regulations (RBI guidelines, SEBI rules)
└── legal/        # Legal provisions (Contract Act, Companies Act)
```

Supported formats: `.pdf`, `.txt`

Then run ingestion:

```bash
make ingest-clear
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage
make test-cov

# Run linters
make lint
```

## 📈 Evaluation

The system includes an evaluation framework with a golden dataset of 30 Q&A pairs.

```bash
# Run evaluation
make evaluate

# View detailed results
cat evaluation/reports/latest.txt
```

### Metrics

| Metric              | Description                        | Threshold |
| ------------------- | ---------------------------------- | --------- |
| Faithfulness        | Is the answer grounded in sources? | ≥ 0.70    |
| Correctness         | Does it match expected answer?     | ≥ 0.60    |
| Citation Quality    | Are citations valid and present?   | ≥ 0.80    |
| Retrieval Relevance | Are retrieved chunks relevant?     | ≥ 0.50    |

## 🔧 Configuration

Key environment variables (`.env`):

```bash
# Required
GROQ_API_KEY=your-api-key

# Optional (with defaults)
GROQ_MODEL=llama-3.1-8b-instant
CHUNK_SIZE=1024
TOP_K_RETRIEVAL=20
TOP_K_RERANK=5
TEMPERATURE=0.0
ENABLE_GUARDRAILS=true
ENABLE_QUERY_REWRITE=true
GUARDRAIL_MIN_TOP_SCORE=0.15
RATE_LIMIT_RPM=120
API_AUTH_ENABLED=true
API_KEYS=
REDIS_URL=
REDIS_KEY_PREFIX=legal_finance_rag
ENABLE_QUERY_CACHE=true
QUERY_CACHE_TTL_SECONDS=300
EVAL_GATE_MIN_PASS_RATE=0.8
```

### Operations Endpoints

- `GET /metrics`: in-memory counters + p95/p99 timing snapshots
- `GET /metrics/prometheus`: Prometheus-formatted metrics
- `GET /health`: includes component readiness
- `POST /api/v1/query` and `POST /api/v2/query`: equivalent versioned routes

### Evaluation Quality Gate

```bash
python scripts/evaluation_gate.py --min-pass-rate 0.8
```

## 📝 API Reference

### Query Endpoint

```bash
POST /api/v1/query
{
  "question": "What are Section 80C deductions?",
  "domain": "tax",
  "include_sources": true
}
```

### Response

```json
{
  "success": true,
  "answer": "Under Section 80C of the Income Tax Act...[1]",
  "sources": [
    {
      "reference_id": 1,
      "source": "income_tax_act.pdf",
      "relevance_score": 0.92
    }
  ],
  "metadata": {
    "total_time_ms": 1500,
    "model": "llama-3.1-8b-instant"
  }
}
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## ⚠️ Disclaimer

This tool is for **educational purposes only**. It should not be considered as professional legal, tax, or financial advice. Always consult qualified professionals for advice specific to your situation.

## Production Hardening

### Reliability

- Configure request timeout and LLM retry controls:
  - `REQUEST_TIMEOUT_SECONDS`
  - `LLM_REQUEST_TIMEOUT_SECONDS`
  - `LLM_MAX_RETRIES`
  - `LLM_RETRY_BACKOFF_SECONDS`
- Run load test:
  - `python scripts/load_test.py --base-url http://localhost:8000 --requests 200 --concurrency 20 --api-key <key>`

### Security

- Keep API auth enabled (`API_AUTH_ENABLED=true`).
- Use hashed keys in production (`API_KEYS_HASHED`) and rotate keys regularly.
- CI now runs `pip-audit`, `bandit`, and `gitleaks`.

### Observability

- Structured logs: `LOG_FORMAT=json`
- Request correlation headers: `X-Request-ID`, `X-Trace-ID`
- Prometheus endpoint: `/metrics/prometheus`
- Optional monitoring stack:
  - `docker compose -f docker/docker-compose.yml -f docker/docker-compose.monitoring.yml up -d`

### Evaluation Gate

- CI enforces pass rate and metric floors:
  - pass rate >= 0.8
  - faithfulness >= 0.7
  - correctness >= 0.6
  - citation quality >= 0.8
  - retrieval relevance >= 0.5

### Operations and Compliance

- Runbook: `docs/operations/runbook.md`
- Backup/restore: `docs/operations/backup_restore.md`
- Security operations: `docs/security/security_operations.md`
- Data safety policy: `docs/compliance/data_safety.md`
- Backup command:
  - `python scripts/backup_chroma.py --source ./chroma_db --target-dir ./backups`
