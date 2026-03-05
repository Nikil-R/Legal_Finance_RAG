"""
Middleware for logging, rate limiting, and exception handling.
"""

from __future__ import annotations

import time
import traceback
from collections import defaultdict, deque
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.infra import redis_store
from app.observability import metrics, prom_bridge
from app.utils.logger import get_logger
from app.utils.request_context import reset_request_context, set_request_context

logger = get_logger(__name__)


class RateLimiter:
    def __init__(self, rpm: int) -> None:
        self.rpm = max(1, int(rpm))
        self._bucket: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> tuple[bool, int]:
        if redis_store.enabled:
            return redis_store.rate_limit_allow(key, self.rpm)

        now = time.time()
        window_start = now - 60.0
        q = self._bucket[key]
        while q and q[0] < window_start:
            q.popleft()
        if len(q) >= self.rpm:
            retry_after = int(max(1.0, 60.0 - (now - q[0])))
            return False, retry_after
        q.append(now)
        return True, 0


rate_limiter = RateLimiter(settings.RATE_LIMIT_RPM)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        request_id = request.headers.get("x-request-id", f"{int(start_time * 1000)}")
        trace_id = request.headers.get("x-trace-id", uuid4().hex)
        request.state.request_id = request_id
        request.state.trace_id = trace_id
        ctx_tokens = set_request_context(request_id=request_id, trace_id=trace_id)
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        rate_key = f"{client_ip}:{path}"

        allowed, retry_after = rate_limiter.allow(rate_key)
        if not allowed:
            metrics.inc("http_rate_limited_total")
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "error_type": "rate_limit",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                headers={
                    "X-Request-ID": request_id,
                    "Retry-After": str(retry_after),
                },
            )

        metrics.inc("http_requests_total")
        logger.info(
            "Request started | ID: %s | Method: %s | Path: %s | IP: %s",
            request_id,
            request.method,
            path,
            client_ip,
        )
        try:
            response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            metrics.observe_ms("http_request_latency_ms", process_time)
            metrics.inc(f"http_status_{response.status_code}_total")
            if process_time >= settings.SLOW_REQUEST_THRESHOLD_MS:
                metrics.inc("http_slow_requests_total")
                logger.warning(
                    "Slow request detected | ID: %s | Path: %s | Time: %.2fms",
                    request_id,
                    path,
                    process_time,
                )
            prom_bridge.observe_http(
                method=request.method,
                path=path,
                status=response.status_code,
                latency_ms=process_time,
            )
            logger.info(
                "Request completed | ID: %s | Status: %d | Time: %.2fms",
                request_id,
                response.status_code,
                process_time,
            )
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Process-Time-Ms"] = str(int(process_time))
            return response
        except Exception as exc:
            process_time = (time.time() - start_time) * 1000
            metrics.inc("http_exceptions_total")
            prom_bridge.observe_http(
                method=request.method,
                path=path,
                status=500,
                latency_ms=process_time,
            )
            logger.error(
                "Request failed | ID: %s | Error: %s | Time: %.2fms",
                request_id,
                str(exc),
                process_time,
            )
            raise
        finally:
            reset_request_context(ctx_tokens)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s\n%s", str(exc), traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An internal server error occurred",
            "error_type": "internal_error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "error_type": "http_error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
