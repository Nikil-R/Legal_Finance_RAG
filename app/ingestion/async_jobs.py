"""
Async dispatch helpers for user-document ingestion jobs.
"""

from __future__ import annotations

import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.config import get_settings
from app.infra.ingestion_jobs import ingestion_job_store
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()
_local_executor = ThreadPoolExecutor(
    max_workers=max(1, settings.INGESTION_LOCAL_WORKERS),
    thread_name_prefix="ingestion-job",
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


def process_ingestion_job(
    *,
    job_id: str,
    staged_file_path: str,
    filename: str,
    session_id: str,
    owner_id: str,
) -> dict:
    """
    Execute ingestion work for an already-staged file and update job status.
    """
    from app.ingestion.user_ingestor import UserDocumentIngestor

    path = Path(staged_file_path)
    ingestion_job_store.mark_processing(job_id)

    try:
        if not path.exists():
            error = "Staged file not found."
            ingestion_job_store.mark_failed(job_id, error=error)
            return {"success": False, "error": error}

        content = path.read_bytes()
        ingestor = UserDocumentIngestor()
        result = ingestor.ingest_file(
            content=content,
            filename=filename,
            session_id=session_id,
            owner_id=owner_id,
        )
        if result.get("success"):
            ingestion_job_store.mark_completed(
                job_id=job_id, chunks_created=result.get("chunks_created", 0)
            )
        else:
            ingestion_job_store.mark_failed(
                job_id=job_id,
                error=result.get("error", "Ingestion failed."),
            )
        return result
    except Exception as exc:
        logger.error("Async ingestion failed for job '%s': %s", job_id, exc, exc_info=True)
        ingestion_job_store.mark_failed(job_id=job_id, error="Ingestion failed.")
        return {"success": False, "error": str(exc)}
    finally:
        path.unlink(missing_ok=True)
        try:
            path.parent.rmdir()
        except OSError:
            # Parent directory may still contain files from other jobs.
            pass


def enqueue_ingestion_job(
    *,
    staged_file_path: str,
    filename: str,
    session_id: str,
    owner_id: str,
) -> dict:
    """
    Enqueue a staged ingestion job through Celery or a local threadpool fallback.
    """
    backend = "celery" if _use_celery() else "local"
    job_id = uuid.uuid4().hex
    record = ingestion_job_store.create_job(
        job_id=job_id,
        session_id=session_id,
        filename=filename,
        owner_id=owner_id,
        backend=backend,
    )

    payload = {
        "job_id": job_id,
        "staged_file_path": staged_file_path,
        "filename": filename,
        "session_id": session_id,
        "owner_id": owner_id,
    }

    if backend == "celery":
        try:
            from app.tasks import ingest_document_async

            ingest_document_async.apply_async(kwargs=payload, task_id=job_id)
            return record
        except Exception as exc:
            logger.warning(
                "Celery enqueue failed for job '%s'; falling back to local worker: %s",
                job_id,
                exc,
            )
            ingestion_job_store.update_job(job_id, backend="local")

    _local_executor.submit(process_ingestion_job, **payload)
    return ingestion_job_store.get_job(job_id) or record
