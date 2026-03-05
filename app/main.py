"""
LegalFinance RAG API main application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import (
    RequestLoggingMiddleware,
    global_exception_handler,
    http_exception_handler,
)
from app.api.routes import (
    documents_router,
    health_router,
    query_router,
    user_documents_router,
)
from app.api.security import require_api_key
from app.config import settings
from app.infra import redis_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events."""
    logger.info("=" * 50)
    logger.info("LegalFinance RAG API starting")
    logger.info("=" * 50)
    logger.info("Groq model       : %s", settings.GROQ_MODEL)
    logger.info("ChromaDB path    : %s", settings.CHROMA_PERSIST_DIR)
    logger.info("Embedding model  : %s", settings.EMBEDDING_MODEL)

    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set; query endpoints will fail")
    if settings.API_AUTH_ENABLED and not settings.API_KEYS and not settings.API_KEYS_HASHED:
        logger.warning("API auth is enabled but no API keys are configured")
    if settings.REJECT_DEFAULT_API_KEYS and "replace_with_strong_key" in settings.API_KEYS:
        logger.warning("Default placeholder API keys detected; replace before production")
    if not settings.API_AUTH_ENABLED:
        logger.warning("API auth is disabled; do not use this in production")

    logger.info("Rate limit RPM   : %d", settings.RATE_LIMIT_RPM)
    logger.info("Request timeout  : %ss", settings.REQUEST_TIMEOUT_SECONDS)
    logger.info("LLM timeout      : %ss", settings.LLM_REQUEST_TIMEOUT_SECONDS)
    logger.info("LLM retries      : %d", settings.LLM_MAX_RETRIES)
    logger.info("Query cache      : %s", settings.ENABLE_QUERY_CACHE)
    logger.info("PII redaction    : %s", settings.PII_REDACTION_ENABLED)
    logger.info("Log format       : %s", settings.LOG_FORMAT)
    logger.info("Redis enabled    : %s", redis_store.enabled)

    logger.info("API ready to accept requests")
    logger.info("=" * 50)

    yield

    logger.info("LegalFinance RAG API shutting down")


app = FastAPI(
    title="LegalFinance RAG API",
    description="""
A Retrieval-Augmented Generation (RAG) API for legal and financial documents.

## Features
- Hybrid Search (vector + BM25)
- Cross-Encoder reranking
- Grounded answers with citations
- Domain filtering
- Runtime safety guardrails
- Isolated user documents
""",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

app.include_router(health_router)
app.include_router(query_router, prefix="/api/v1", dependencies=[Depends(require_api_key)])
app.include_router(
    documents_router, prefix="/api/v1", dependencies=[Depends(require_api_key)]
)
app.include_router(
    user_documents_router, prefix="/api/v1", dependencies=[Depends(require_api_key)]
)
app.include_router(query_router, prefix="/api/v2", dependencies=[Depends(require_api_key)])
app.include_router(
    documents_router, prefix="/api/v2", dependencies=[Depends(require_api_key)]
)
app.include_router(
    user_documents_router, prefix="/api/v2", dependencies=[Depends(require_api_key)]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    )
