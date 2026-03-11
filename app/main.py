from __future__ import annotations

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
    user_documents_router,
)
from app.api.security import require_api_key
from app.config import settings
from app.observability import (
    configure_metrics,
    configure_tracing,
    logger,
    query_latency,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="LegalFinance RAG API",
        version="1.0.0",
        description="Production-ready RAG with observability.",
    )

    configure_tracing(app)
    configure_metrics(app)

    cors_origins = settings.CORS_ORIGINS
    if isinstance(cors_origins, str):
        cors_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(RequestLoggingMiddleware)

    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)

    app.include_router(health_router)
    app.include_router(query_router, prefix="/api/v1", dependencies=[Depends(require_api_key)])
    app.include_router(documents_router, prefix="/api/v1", dependencies=[Depends(require_api_key)])
    app.include_router(user_documents_router, prefix="/api/v1", dependencies=[Depends(require_api_key)])
    app.include_router(query_router, prefix="/api/v2", dependencies=[Depends(require_api_key)])
    app.include_router(documents_router, prefix="/api/v2", dependencies=[Depends(require_api_key)])
    app.include_router(user_documents_router, prefix="/api/v2", dependencies=[Depends(require_api_key)])

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        query_latency.labels(endpoint=request.url.path).observe(duration)
        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )
        return response

    @app.get("/")
    async def root():
        return {
            "name": "LegalFinance RAG API",
            "version": "1.0.0",
            "status": "operational",
            "docs_url": "/docs",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
