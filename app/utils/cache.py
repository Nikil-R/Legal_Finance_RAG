"""
Simple in-memory TTL cache for query responses.
"""

from __future__ import annotations

import time
from threading import Lock

from app.infra import redis_store


class TTLCache:
    def __init__(self, ttl_seconds: int = 300, max_entries: int = 2048) -> None:
        self.ttl_seconds = max(1, int(ttl_seconds))
        self.max_entries = max(1, int(max_entries))
        self._store: dict[str, tuple[float, dict]] = {}
        self._lock = Lock()

    def get(self, key: str) -> dict | None:
        redis_value = redis_store.cache_get(key)
        if redis_value is not None:
            return redis_value

        now = time.time()
        with self._lock:
            item = self._store.get(key)
            if item is None:
                return None
            exp_ts, value = item
            if exp_ts < now:
                self._store.pop(key, None)
                return None
            return value

    def set(self, key: str, value: dict) -> None:
        if redis_store.cache_set(key, value, self.ttl_seconds):
            return

        now = time.time()
        with self._lock:
            if len(self._store) >= self.max_entries:
                oldest_key = min(self._store, key=lambda k: self._store[k][0])
                self._store.pop(oldest_key, None)
            self._store[key] = (now + self.ttl_seconds, value)

    def clear(self) -> None:
        with self._lock:
            self._store.clear()
