"""
Optional Redis-backed primitives for production cache and rate-limiting.
Falls back gracefully when Redis is unavailable.
"""

from __future__ import annotations

import json
import time

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from redis import Redis
except Exception:  # pragma: no cover - optional dependency
    Redis = None  # type: ignore


class RedisStore:
    def __init__(self) -> None:
        self._client = None
        if not settings.REDIS_URL or Redis is None:
            return
        try:
            self._client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            self._client.ping()
            logger.info("Redis store connected")
        except Exception as exc:
            logger.warning("Redis unavailable, using local fallback: %s", exc)
            self._client = None

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def _key(self, raw: str) -> str:
        return f"{settings.REDIS_KEY_PREFIX}:{raw}"

    def json_get(self, key: str) -> dict | None:
        if not self._client:
            return None
        try:
            raw = self._client.get(self._key(key))
            return json.loads(raw) if raw else None
        except Exception:
            return None

    def json_set(self, key: str, value: dict, ttl_seconds: int | None = None) -> bool:
        if not self._client:
            return False
        try:
            payload = json.dumps(value)
            if ttl_seconds is None:
                self._client.set(self._key(key), payload)
            else:
                self._client.setex(
                    self._key(key),
                    int(max(1, ttl_seconds)),
                    payload,
                )
            return True
        except Exception:
            return False

    def cache_get(self, key: str) -> dict | None:
        return self.json_get(f"cache:{key}")

    def cache_set(self, key: str, value: dict, ttl_seconds: int) -> bool:
        return self.json_set(f"cache:{key}", value, ttl_seconds=ttl_seconds)

    def rate_limit_allow(self, key: str, limit_per_minute: int) -> tuple[bool, int]:
        """
        Fixed-window limiter in Redis: key expires in 60s.
        Returns (allowed, retry_after_seconds).
        """
        if not self._client:
            return True, 0
        rkey = self._key(f"rate:{key}:{int(time.time() // 60)}")
        try:
            count = self._client.incr(rkey)
            if count == 1:
                self._client.expire(rkey, 61)
            if count > limit_per_minute:
                ttl = int(self._client.ttl(rkey))
                return False, max(ttl, 1)
            return True, 0
        except Exception:
            return True, 0


redis_store = RedisStore()
