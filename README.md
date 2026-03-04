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

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│    FastAPI      │
│   Frontend      │◀────│    Backend      │
└─────────────────┘     └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
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
                        │  Groq (Llama)   │
                        │  Generation     │
                        └─────────────────┘
```

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

# 3. In another terminal, start the frontend
make run-frontend

# Open http://localhost:8501 in your browser
```

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
├── app/                    # FastAPI backend
│   ├── api/               # API routes and models
│   ├── ingestion/         # Document loading and chunking
│   ├── retrieval/         # Vector + BM25 search
│   ├── reranking/         # Cross-encoder reranking
│   ├── generation/        # LLM generation with Groq
│   └── prompts/           # Versioned prompt templates
├── frontend/              # Streamlit UI
├── evaluation/            # Golden dataset and metrics
├── data/raw/              # Source documents by domain
├── tests/                 # Test suite
└── docker/                # Docker configuration
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

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Faithfulness | Is the answer grounded in sources? | ≥ 0.70 |
| Correctness | Does it match expected answer? | ≥ 0.60 |
| Citation Quality | Are citations valid and present? | ≥ 0.80 |
| Retrieval Relevance | Are retrieved chunks relevant? | ≥ 0.50 |

## 🔧 Configuration

Key environment variables (`.env`):

```bash
# Required
GROQ_API_KEY=your-api-key

# Optional (with defaults)
GROQ_MODEL=llama-3.1-8b-instant
CHUNK_SIZE=512
TOP_K_RETRIEVAL=20
TOP_K_RERANK=5
TEMPERATURE=0.0
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
