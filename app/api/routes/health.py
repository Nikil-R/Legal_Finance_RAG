from __future__ import annotations

import asyncio
import time
from datetime import datetime
from typing import Dict, Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["Observability"])


class ComponentHealth(BaseModel):
    status: Literal["healthy", "unhealthy"]
    latency_ms: float
    message: str = ""


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded", "unhealthy"]
    timestamp: datetime
    checks: Dict[str, ComponentHealth]


# ── Individual component checks ──────────────────────────────────────


async def check_redis() -> ComponentHealth:
    from redis.asyncio import Redis
    from app.config import settings

    start = time.time()
    try:
        redis = Redis.from_url(
            settings.REDIS_URL,
            socket_timeout=1.0,
            socket_connect_timeout=1.0,
        )
        await redis.ping()
        await redis.close()
        latency = (time.time() - start) * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2), message="Redis OK")
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=str(exc))


async def check_celery() -> ComponentHealth:
    from app.tasks import celery_app

    start = time.time()
    try:
        inspect = celery_app.control.inspect(timeout=1.0)
        active = await asyncio.to_thread(inspect.active)

        if not active:
            return ComponentHealth(
                status="unhealthy",
                latency_ms=0,
                message="No active Celery workers",
            )

        latency = (time.time() - start) * 1000
        return ComponentHealth(
            status="healthy",
            latency_ms=round(latency, 2),
            message=f"{len(active)} workers active",
        )
    except Exception as exc:
        return ComponentHealth(
            status="unhealthy", latency_ms=0, message=f"Celery check failed: {exc}"
        )


_chroma_client = None


async def check_chroma() -> ComponentHealth:
    from app.config import settings
    import chromadb
    global _chroma_client

    start = time.time()
    try:
        if _chroma_client is None:
            _chroma_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

        _chroma_client.heartbeat()
        latency = (time.time() - start) * 1000
        return ComponentHealth(
            status="healthy",
            latency_ms=round(latency, 2),
            message="ChromaDB heartbeat OK",
        )
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=str(exc))


async def check_groq() -> ComponentHealth:
    """Lightweight Groq API key validation — does NOT make a full LLM call."""
    from app.config import settings

    start = time.time()
    try:
        api_key = settings.GROQ_API_KEY
        if not api_key or api_key == "test_groq_key":
            return ComponentHealth(status="unhealthy", latency_ms=0, message="Groq API key not configured")

        # Just verify the key exists and is non-empty — a real LLM call is too slow for health checks
        latency = (time.time() - start) * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2), message="Groq API Key Configured")
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=str(exc))


async def check_embedding() -> ComponentHealth:
    start = time.time()
    try:
        from app.api.dependencies import get_retrieval_pipeline
        pipeline = get_retrieval_pipeline()
        encoder = pipeline._retriever._vector._encoder
        # Quick encode test — the model is already loaded in memory
        await asyncio.to_thread(encoder.encode, "test", show_progress_bar=False)
        latency = (time.time() - start) * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2), message="Embedding Model Operational")
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=f"Embedding check failed: {exc}")


async def check_reranker() -> ComponentHealth:
    start = time.time()
    try:
        from app.api.dependencies import get_retrieval_pipeline
        pipeline = get_retrieval_pipeline()
        reranker = pipeline._reranker._model
        await asyncio.to_thread(reranker.predict, [("test", "test")])
        latency = (time.time() - start) * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2), message="Reranker Model Operational")
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=f"Reranker check failed: {exc}")


# ── Helper: wrap any check with a per-component timeout ──────────────


async def _safe_check(coro, timeout: float = 3.0) -> ComponentHealth:
    """Run a health check with a hard timeout so no single check blocks the response."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=f"Timed out after {timeout}s")
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=str(exc))


# ── Main health endpoint ─────────────────────────────────────────────


@router.get("", response_model=HealthResponse)
async def health_check():
    from app.config import settings
    
    is_local = settings.ENVIRONMENT in ("local", "development", "dev")
    
    # In local/dev mode, skip infrastructure checks (Redis, Celery)
    # that require services not available on Windows
    if is_local:
        tasks = await asyncio.gather(
            _safe_check(check_chroma(), timeout=3.0),
            _safe_check(check_groq(), timeout=1.0),
            _safe_check(check_embedding(), timeout=3.0),
            _safe_check(check_reranker(), timeout=3.0),
        )
        checks = {
            "chroma": tasks[0],
            "groq": tasks[1],
            "embedding": tasks[2],
            "reranker": tasks[3],
            "redis": ComponentHealth(status="healthy", latency_ms=0, message="Skipped (local mode)"),
            "celery": ComponentHealth(status="healthy", latency_ms=0, message="Skipped (local mode)"),
        }
    else:
        # Production: check everything
        tasks = await asyncio.gather(
            _safe_check(check_redis(), timeout=2.0),
            _safe_check(check_celery(), timeout=2.0),
            _safe_check(check_chroma(), timeout=3.0),
            _safe_check(check_groq(), timeout=1.0),
            _safe_check(check_embedding(), timeout=3.0),
            _safe_check(check_reranker(), timeout=3.0),
        )
        checks = {
            "redis": tasks[0],
            "celery": tasks[1],
            "chroma": tasks[2],
            "groq": tasks[3],
            "embedding": tasks[4],
            "reranker": tasks[5],
        }

    # Critical = must be healthy for system to work
    # Auxiliary = nice-to-have, system still usable without them
    critical_checks = ["chroma", "embedding"]
    aux_checks = ["redis", "celery", "groq", "reranker"]

    any_critical_unhealthy = any(checks[c].status == "unhealthy" for c in critical_checks)
    any_aux_unhealthy = any(checks[a].status == "unhealthy" for a in aux_checks)

    if any_critical_unhealthy:
        status = "unhealthy"
    elif any_aux_unhealthy:
        status = "degraded"
    else:
        status = "healthy"

    response = HealthResponse(
        status=status,
        timestamp=datetime.utcnow(),
        checks=checks,
    )

    if status == "unhealthy":
        response_dict = response.model_dump()
        response_dict["timestamp"] = response.timestamp.isoformat()
        raise HTTPException(status_code=503, detail=response_dict)

    return response


# ── Kubernetes-style probes ──────────────────────────────────────────


@router.get("/liveness")
async def liveness_check():
    return JSONResponse(
        {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@router.get("/readiness")
async def readiness_check():
    chroma_health = await check_chroma()

    if chroma_health.status == "unhealthy":
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "chroma": chroma_health.dict(),
            },
        )

    return JSONResponse(
        {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
