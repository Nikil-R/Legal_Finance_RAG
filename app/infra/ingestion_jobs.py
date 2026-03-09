"""
Job state storage for asynchronous user-document ingestion.
"""

from __future__ import annotations

import threading
import time
from datetime import datetime, timezone

from app.config import get_settings
from app.infra.redis_store import redis_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


class IngestionJobStore:
    """Persist ingestion job states in Redis, with in-memory fallback."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._lock = threading.Lock()
        self._local_jobs: dict[str, tuple[dict, float]] = {}

    @property
    def ttl_seconds(self) -> int:
        return int(max(60, self._settings.INGESTION_JOB_TTL_SECONDS))

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _redis_key(job_id: str) -> str:
        return f"ingestion_job:{job_id}"

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

    def create_job(
        self,
        *,
        job_id: str,
        session_id: str,
        filename: str,
        owner_id: str,
        backend: str,
    ) -> dict:
        now = self._now_iso()
        record = {
            "job_id": job_id,
            "status": "queued",
            "session_id": session_id,
            "filename": filename,
            "owner_id": owner_id,
            "backend": backend,
            "chunks_created": 0,
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
                    "Redis job-store write failed for job '%s'; using local fallback.",
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
                    "Redis job-store update failed for job '%s'; using local fallback.",
                    job_id,
                )
                self._local_put(job_id, current)
        else:
            self._local_put(job_id, current)

        return dict(current)

    def mark_processing(self, job_id: str) -> dict | None:
        return self.update_job(job_id, status="processing")

    def mark_completed(self, job_id: str, chunks_created: int) -> dict | None:
        return self.update_job(
            job_id,
            status="completed",
            chunks_created=int(max(0, chunks_created)),
            error=None,
        )

    def mark_failed(self, job_id: str, error: str) -> dict | None:
        return self.update_job(job_id, status="failed", error=error)


ingestion_job_store = IngestionJobStore()
