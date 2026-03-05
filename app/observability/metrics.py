"""
In-memory metrics registry for lightweight production observability.
"""

from __future__ import annotations

from collections import defaultdict
from statistics import mean
from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[str, int] = defaultdict(int)
        self._timings: dict[str, list[float]] = defaultdict(list)

    def inc(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def observe_ms(self, name: str, value_ms: float) -> None:
        with self._lock:
            self._timings[name].append(float(value_ms))

    def snapshot(self) -> dict:
        with self._lock:
            timings = {}
            for name, values in self._timings.items():
                if not values:
                    continue
                sorted_values = sorted(values)
                idx_95 = max(int(0.95 * (len(sorted_values) - 1)), 0)
                idx_99 = max(int(0.99 * (len(sorted_values) - 1)), 0)
                timings[name] = {
                    "count": len(values),
                    "avg_ms": round(mean(values), 3),
                    "p95_ms": round(sorted_values[idx_95], 3),
                    "p99_ms": round(sorted_values[idx_99], 3),
                }

            return {
                "counters": dict(self._counters),
                "timings": timings,
            }


metrics = MetricsRegistry()
