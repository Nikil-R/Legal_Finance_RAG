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


async def check_redis() -> ComponentHealth:
    from redis.asyncio import Redis
    from app.config import settings

    start = time.time()
    try:
        redis = Redis.from_url(
            settings.REDIS_URL,
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
        )
        await redis.ping()
        await redis.close()
        latency = (time.time() - start) * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2))
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=str(exc))


async def check_celery() -> ComponentHealth:
    from app.tasks import celery_app

    start = time.time()
    try:
        inspect = celery_app.control.inspect(timeout=2.0)
        active = inspect.active()

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


async def check_qdrant() -> ComponentHealth:
    from app.config import settings

    start = time.time()
    try:
        from qdrant_client import QdrantClient

        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        collections = client.get_collections()
        latency = (time.time() - start) * 1000
        return ComponentHealth(
            status="healthy",
            latency_ms=round(latency, 2),
            message=f"{len(collections.collections)} collections",
        )
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=str(exc))


async def check_groq() -> ComponentHealth:
    from app.config import settings
    from groq import AsyncGroq

    start = time.time()
    try:
        client = AsyncGroq(api_key=settings.GROQ_API_KEY, timeout=5.0)
        await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )
        latency = (time.time() - start) * 1000
        return ComponentHealth(status="healthy", latency_ms=round(latency, 2))
    except Exception as exc:
        return ComponentHealth(status="unhealthy", latency_ms=0, message=str(exc))


@router.get("", response_model=HealthResponse)
async def health_check():
    tasks = await asyncio.gather(
        check_redis(),
        check_celery(),
        check_qdrant(),
        check_groq(),
        return_exceptions=True,
    )

    def normalize(idx: int) -> ComponentHealth:
        result = tasks[idx]
        if isinstance(result, ComponentHealth):
            return result
        return ComponentHealth(status="unhealthy", latency_ms=0, message=str(result))

    checks = {
        "redis": normalize(0),
        "celery": normalize(1),
        "qdrant": normalize(2),
        "groq": normalize(3),
    }

    unhealthy = sum(1 for component in checks.values() if component.status == "unhealthy")
    status = "healthy" if unhealthy == 0 else "degraded" if unhealthy == 1 else "unhealthy"

    response = HealthResponse(
        status=status,
        timestamp=datetime.utcnow(),
        checks=checks,
    )

    if status == "unhealthy":
        raise HTTPException(status_code=503, detail=response.dict())

    return response


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
    redis_health, qdrant_health = await asyncio.gather(check_redis(), check_qdrant())

    if redis_health.status == "unhealthy" or qdrant_health.status == "unhealthy":
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "redis": redis_health.dict(),
                "qdrant": qdrant_health.dict(),
            },
        )

    return JSONResponse(
        {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
