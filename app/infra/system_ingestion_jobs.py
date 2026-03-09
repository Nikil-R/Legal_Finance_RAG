"""
Job state storage for asynchronous system-document ingestion.
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone

from app.config import get_settings
from app.infra.redis_store import redis_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SystemIngestionJobStore:
    """Persist system-ingestion job states in Redis, with in-memory fallback."""

    LAST_COMPLETED_KEY = "system_ingestion:last_completed_at"

    def __init__(self) -> None:
        self._settings = get_settings()
        self._lock = threading.Lock()
        self._local_jobs: dict[str, tuple[dict, float]] = {}
        self._local_last_completed_at: str | None = None

    @property
    def ttl_seconds(self) -> int:
        return int(max(60, self._settings.INGESTION_JOB_TTL_SECONDS))

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _redis_key(job_id: str) -> str:
        return f"system_ingestion_job:{job_id}"

    def _local_put(self, job_id: str, record: dict) -> None:
        expiry_ts = time.time() + self.ttl_seconds
        with self._lock:
            self._local_jobs[job_id] = (dict(record), expiry_ts)

    def _local_get(self, job_id: str) -> dict | None:
        now = time.time()
        with self._lock:
            item = self._local_jobs.get(job_id)
            if not item:
                return None
            record, expiry_ts = item
            if expiry_ts <= now:
                self._local_jobs.pop(job_id, None)
                return None
            return dict(record)

    def _local_set_last_completed_at(self, when_iso: str) -> None:
        with self._lock:
            self._local_last_completed_at = when_iso

    def _local_get_last_completed_at(self) -> str | None:
        with self._lock:
            return self._local_last_completed_at

    def create_job(
        self,
        *,
        job_id: str,
        clear_existing: bool,
        backend: str,
    ) -> dict:
        now = self._now_iso()
        record = {
            "job_id": job_id,
            "status": "queued",
            "clear_existing": bool(clear_existing),
            "backend": backend,
            "documents_loaded": 0,
            "chunks_created": 0,
            "chunks_stored": 0,
            "domains": {},
            "time_taken_seconds": 0.0,
            "cache_invalidated": False,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }
        if redis_store.enabled:
            ok = redis_store.json_set(
                self._redis_key(job_id),
                record,
                ttl_seconds=self.ttl_seconds,
            )
            if not ok:
                logger.warning(
                    "Redis system job-store write failed for job '%s'; using local fallback.",
                    job_id,
                )
                self._local_put(job_id, record)
        else:
            self._local_put(job_id, record)
        return dict(record)

    def get_job(self, job_id: str) -> dict | None:
        if redis_store.enabled:
            record = redis_store.json_get(self._redis_key(job_id))
            if record is not None:
                return record
        return self._local_get(job_id)

    def update_job(self, job_id: str, **updates) -> dict | None:
        current = self.get_job(job_id)
        if current is None:
            return None

        current.update(updates)
        current["updated_at"] = self._now_iso()

        if redis_store.enabled:
            ok = redis_store.json_set(
                self._redis_key(job_id),
                current,
                ttl_seconds=self.ttl_seconds,
            )
            if not ok:
                logger.warning(
                    "Redis system job-store update failed for job '%s'; using local fallback.",
                    job_id,
                )
                self._local_put(job_id, current)
        else:
            self._local_put(job_id, current)

        return dict(current)

    def set_last_completed_at(self, when_iso: str) -> None:
        if redis_store.enabled:
            ok = redis_store.json_set(
                self.LAST_COMPLETED_KEY,
                {"last_completed_at": when_iso},
            )
            if not ok:
                logger.warning(
                    "Redis last-completed write failed; using local fallback."
                )
                self._local_set_last_completed_at(when_iso)
        else:
            self._local_set_last_completed_at(when_iso)

    def get_last_completed_at(self) -> str | None:
        if redis_store.enabled:
            record = redis_store.json_get(self.LAST_COMPLETED_KEY)
            if record is not None:
                return record.get("last_completed_at")
        return self._local_get_last_completed_at()

    def mark_processing(self, job_id: str) -> dict | None:
        return self.update_job(job_id, status="processing")

    def mark_completed(
        self,
        *,
        job_id: str,
        documents_loaded: int,
        chunks_created: int,
        chunks_stored: int,
        domains: dict[str, int],
        time_taken_seconds: float,
        cache_invalidated: bool,
    ) -> dict | None:
        record = self.update_job(
            job_id=job_id,
            status="completed",
            documents_loaded=int(max(0, documents_loaded)),
            chunks_created=int(max(0, chunks_created)),
            chunks_stored=int(max(0, chunks_stored)),
            domains=dict(domains),
            time_taken_seconds=float(max(0.0, time_taken_seconds)),
            cache_invalidated=bool(cache_invalidated),
            error=None,
        )
        if record is not None:
            self.set_last_completed_at(record["updated_at"])
        return record

    def mark_failed(
        self, *, job_id: str, error: str, time_taken_seconds: float
    ) -> dict | None:
        return self.update_job(
            job_id,
            status="failed",
            error=error,
            time_taken_seconds=float(max(0.0, time_taken_seconds)),
        )


system_ingestion_job_store = SystemIngestionJobStore()
