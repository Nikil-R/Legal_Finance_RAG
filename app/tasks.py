"""
Celery tasks for asynchronous ingestion workloads.
"""

from __future__ import annotations

from celery import Celery

from app.config import get_settings
from app.ingestion.async_jobs import process_ingestion_job
from app.ingestion.system_async_jobs import process_system_ingestion_job

settings = get_settings()

_default_broker = "redis://localhost:6379/0"
broker_url = settings.CELERY_BROKER_URL or settings.REDIS_URL or _default_broker
result_backend = settings.CELERY_RESULT_BACKEND or broker_url

celery_app = Celery(
    "legal_finance_rag_tasks",
    broker=broker_url,
    backend=result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="ingest_document_async")
def ingest_document_async(
    *,
    job_id: str,
    staged_file_path: str,
    filename: str,
    session_id: str,
    owner_id: str,
) -> dict:
    return process_ingestion_job(
        job_id=job_id,
        staged_file_path=staged_file_path,
        filename=filename,
        session_id=session_id,
        owner_id=owner_id,
    )


@celery_app.task(name="ingest_system_documents_async")
def ingest_system_documents_async(
    *,
    job_id: str,
    clear_existing: bool,
    backend: str = "celery",
) -> dict:
    return process_system_ingestion_job(
        job_id=job_id,
        clear_existing=clear_existing,
        backend=backend,
    )
