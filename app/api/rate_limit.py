from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings


def get_api_key_identifier(request: Request) -> str:
    api_key = request.headers.get("X-API-Key", "")
    if api_key:
        return f"apikey:{api_key[:16]}"
    return f"ip:{get_remote_address(request)}"


try:
    storage_uri = settings.REDIS_URL
except RuntimeError:
    storage_uri = "redis://localhost:6379/1"

limiter = Limiter(
    key_func=get_api_key_identifier,
    default_limits=["1000/day", "100/hour"],
    storage_uri=storage_uri,
    strategy="fixed-window",
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": str(exc.detail),
            "retry_after": exc.detail or "Please retry later",
        },
        headers={"Retry-After": "60"},
    )
