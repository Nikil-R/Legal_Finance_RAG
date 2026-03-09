"""
Async dispatch helpers for system-document ingestion jobs.
"""

from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor

from app.api.dependencies import clear_pipeline_cache
from app.config import get_settings
from app.infra.system_ingestion_jobs import system_ingestion_job_store
from app.ingestion.pipeline import run_ingestion_pipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
_local_executor = ThreadPoolExecutor(
    max_workers=max(1, settings.INGESTION_LOCAL_WORKERS),
    thread_name_prefix="system-ingestion-job",
)


def _broker_url() -> str:
    return (settings.CELERY_BROKER_URL or settings.REDIS_URL or "").strip()


def _use_celery() -> bool:
    backend = (settings.INGESTION_QUEUE_BACKEND or "auto").strip().lower()
    if backend == "celery":
        return True
    if backend == "local":
        return False
    return bool(_broker_url())


def process_system_ingestion_job(
    *,
    job_id: str,
    clear_existing: bool,
    backend: str,
) -> dict:
    """
    Execute system ingestion work and update job status.
    """
    system_ingestion_job_store.mark_processing(job_id)
    started = time.time()

    try:
        summary = run_ingestion_pipeline(clear_existing=clear_existing)
        elapsed = time.time() - started

        # Local workers run in the API process, so they can safely invalidate caches.
        cache_invalidated = backend == "local"
        if cache_invalidated:
            clear_pipeline_cache()

        system_ingestion_job_store.mark_completed(
            job_id=job_id,
            documents_loaded=summary.get("documents_loaded", 0),
            chunks_created=summary.get("chunks_created", 0),
            chunks_stored=summary.get("chunks_stored", 0),
            domains=summary.get("domain_breakdown", {}),
            time_taken_seconds=elapsed,
            cache_invalidated=cache_invalidated,
        )
        return {"success": True, **summary, "time_taken_seconds": elapsed}
    except Exception as exc:
        elapsed = time.time() - started
        logger.error(
            "Async system ingestion failed for job '%s': %s", job_id, exc, exc_info=True
        )
        system_ingestion_job_store.mark_failed(
            job_id=job_id,
            error="Ingestion failed.",
            time_taken_seconds=elapsed,
        )
        return {"success": False, "error": str(exc), "time_taken_seconds": elapsed}


def enqueue_system_ingestion_job(*, clear_existing: bool) -> dict:
    """
    Enqueue system ingestion through Celery or a local threadpool fallback.
    """
    backend = "celery" if _use_celery() else "local"
    job_id = uuid.uuid4().hex
    record = system_ingestion_job_store.create_job(
        job_id=job_id,
        clear_existing=clear_existing,
        backend=backend,
    )

    payload = {
        "job_id": job_id,
        "clear_existing": bool(clear_existing),
        "backend": backend,
    }

    if backend == "celery":
        try:
            from app.tasks import ingest_system_documents_async

            ingest_system_documents_async.apply_async(kwargs=payload, task_id=job_id)
            return record
        except Exception as exc:
            logger.warning(
                "Celery enqueue failed for system job '%s'; falling back to local worker: %s",
                job_id,
                exc,
            )
            backend = "local"
            payload["backend"] = backend
            system_ingestion_job_store.update_job(job_id, backend=backend)

    _local_executor.submit(process_system_ingestion_job, **payload)
    return system_ingestion_job_store.get_job(job_id) or record
