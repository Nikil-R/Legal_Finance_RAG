from __future__ import annotations

import os
import sys

# CRITICAL: Skip heavy initialization on import
os.environ.setdefault("SKIP_STARTUP_CHECKS", "true")
os.environ.setdefault("LAZY_LOAD", "true")

import time

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.middleware import (
    RequestLoggingMiddleware,
    global_exception_handler,
    http_exception_handler,
)
from app.api.rate_limit import limiter, rate_limit_exceeded_handler
from app.api.routes import (
    documents_router,
    health_router,
    query_router,
    tools_router,
    user_documents_router,
)
from app.api.security import require_api_key
from app.config import settings
try:
    from app.observability import (
        configure_metrics,
        configure_tracing,
        logger,
        metrics,
        query_latency,
    )
except Exception as e:
    print(f"Warning: Could not load observability: {e}")
    # Create dummy functions to avoid crashing if called
    def configure_metrics(app): pass
    def configure_tracing(app): pass
    logger = None
    metrics = None
    query_latency = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="LegalFinance RAG API",
        version="1.0.0",
        description="Production-ready RAG API",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict later
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Simple logging
    app.add_middleware(RequestLoggingMiddleware)

    # Error handlers
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

    # Routes - NO AUTH for deployment
    app.include_router(health_router)
    app.include_router(query_router, prefix="/api/v1")
    app.include_router(tools_router, prefix="/api/v1")
    app.include_router(documents_router, prefix="/api/v1")
    app.include_router(user_documents_router, prefix="/api/v1")
    
    app.include_router(query_router, prefix="/api/v2")
    app.include_router(documents_router, prefix="/api/v2")
    app.include_router(user_documents_router, prefix="/api/v2")

    @app.get("/")
    async def root():
        return {
            "name": "LegalFinance RAG API",
            "version": "1.0.0",
            "status": "operational",
            "docs_url": "/docs",
        }

    @app.get("/config")
    async def public_config():
        """Expose non-sensitive runtime configuration values."""
        return {
            "groq_model": settings.GROQ_MODEL,
            "embedding_model": settings.EMBEDDING_MODEL,
            "cross_encoder_model": settings.CROSS_ENCODER_MODEL,
            "chunk_size": settings.CHUNK_SIZE,
            "chunk_overlap": settings.CHUNK_OVERLAP,
            "top_k_retrieval": settings.TOP_K_RETRIEVAL,
            "top_k_rerank": settings.TOP_K_RERANK,
            "temperature": settings.TEMPERATURE,
            "api_auth_enabled": settings.API_AUTH_ENABLED,
            "enable_tool_calling": settings.ENABLE_TOOL_CALLING,
            "tool_calling_max_rounds": settings.TOOL_CALLING_MAX_ROUNDS,
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
