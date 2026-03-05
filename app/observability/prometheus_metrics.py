"""
Prometheus metrics bridge (optional).
"""

from __future__ import annotations

from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
except Exception:  # pragma: no cover
    CONTENT_TYPE_LATEST = "text/plain"
    Counter = None  # type: ignore
    Histogram = None  # type: ignore
    generate_latest = None  # type: ignore


class PrometheusBridge:
    def __init__(self) -> None:
        self.enabled = Counter is not None and Histogram is not None
        if not self.enabled:
            return
        self.http_requests = Counter(
            "rag_http_requests_total", "Total HTTP requests", ["method", "path", "status"]
        )
        self.http_latency = Histogram(
            "rag_http_request_latency_ms", "HTTP request latency in ms", ["path"]
        )
        self.query_total = Counter("rag_query_total", "Total query requests", ["status"])

    def observe_http(self, method: str, path: str, status: int, latency_ms: float) -> None:
        if not self.enabled:
            return
        self.http_requests.labels(method=method, path=path, status=str(status)).inc()
        self.http_latency.labels(path=path).observe(latency_ms)

    def inc_query(self, status: str) -> None:
        if self.enabled:
            self.query_total.labels(status=status).inc()

    def render(self) -> tuple[bytes, str]:
        if not self.enabled or generate_latest is None:
            return b"# Prometheus client not installed\n", "text/plain; charset=utf-8"
        return generate_latest(), CONTENT_TYPE_LATEST


prom_bridge = PrometheusBridge()
