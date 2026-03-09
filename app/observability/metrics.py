from __future__ import annotations

from typing import Dict

from prometheus_client import Counter, Gauge, Histogram, Info
from prometheus_fastapi_instrumentator import Instrumentator

from app.config import settings

class MetricsRegistry:
    """In-memory counters/timings for quick snapshots."""

    def __init__(self) -> None:
        self._counters: Dict[str, int] = {}
        self._timings: Dict[str, list[float]] = {}
        self._lock = None

    def inc(self, name: str, amount: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + amount

    def observe_ms(self, name: str, value_ms: float) -> None:
        self._timings.setdefault(name, []).append(float(value_ms))

    def snapshot(self) -> Dict[str, Dict]:
        return {
            "counters": dict(self._counters),
            "timings": {
                name: {
                    "count": len(values),
                    "avg_ms": sum(values) / len(values) if values else 0,
                    "p95_ms": sorted(values)[int(0.95 * (len(values) - 1))] if values else 0,
                }
                for name, values in self._timings.items()
                if values
            },
        }


metrics = MetricsRegistry()

# Prometheus instrumentation
query_counter = Counter(
    "query_requests_total",
    "Total number of query requests",
    ["role", "status"],
)

query_latency = Histogram(
    "query_duration_seconds",
    "Execution time of query endpoint",
    ["endpoint"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

ingestion_counter = Counter(
    "ingestion_requests_total",
    "Total number of ingestion requests",
    ["status"],
)

celery_queue_length = Gauge(
    "celery_queue_length",
    "Pending Celery jobs by queue",
    ["queue_name"],
)

system_info = Info("legal_rag_system", "System information")

_metrics_instrumentator: Instrumentator | None = None


def configure_metrics(app) -> None:
    global _metrics_instrumentator
    _metrics_instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics"],
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    _metrics_instrumentator.instrument(app).expose(app, endpoint="/metrics")
    system_info.info(
        {
            "service": "legal-rag-api",
            "environment": settings.ENVIRONMENT,
        }
    )
