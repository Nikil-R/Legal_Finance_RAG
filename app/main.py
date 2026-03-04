"""
LegalFinance RAG API — Main Application Entry Point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import (
    RequestLoggingMiddleware,
    global_exception_handler,
    http_exception_handler,
)
from app.api.routes import documents_router, health_router, query_router, user_documents_router
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    logger.info("=" * 50)
    logger.info("LegalFinance RAG API Starting…")
    logger.info("=" * 50)
    logger.info("Groq Model       : %s", settings.GROQ_MODEL)
    logger.info("ChromaDB Path    : %s", settings.CHROMA_PERSIST_DIR)
    logger.info("Embedding Model  : %s", settings.EMBEDDING_MODEL)

    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set — query endpoints will fail!")

    logger.info("API ready to accept requests")
    logger.info("=" * 50)

    yield  # Application runs here

    logger.info("LegalFinance RAG API shutting down…")


# ── Create FastAPI application ─────────────────────────────────────────────────

app = FastAPI(
    title="LegalFinance RAG API",
    description="""
A Retrieval-Augmented Generation (RAG) API for Indian Tax Laws,
Financial Regulations, and Legal Provisions.

## Features
- **Hybrid Search**: Combines vector similarity and BM25 keyword search
- **Cross-Encoder Reranking**: Precise relevance scoring with ms-marco
- **Grounded Answers**: Responses always cite source document numbers
- **Domain Filtering**: Search within tax, finance, or legal sub-corpora
- **Legal Disclaimer**: Automatically appended to every response
- **Isolated User Documents**: Upload and search personal docs in session-safe collections

## Quick Start
1. Ingest documents: `POST /api/v1/documents/ingest`
2. Query the system: `POST /api/v1/query`
""",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── Middleware ─────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)

# ── Exception handlers ─────────────────────────────────────────────────────────

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# ── Routers ────────────────────────────────────────────────────────────────────

app.include_router(health_router)                          # / and /health
app.include_router(query_router, prefix="/api/v1")         # /api/v1/query
app.include_router(documents_router, prefix="/api/v1")     # /api/v1/documents
app.include_router(user_documents_router, prefix="/api/v1") # /api/v1/user

# ── Run directly ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
