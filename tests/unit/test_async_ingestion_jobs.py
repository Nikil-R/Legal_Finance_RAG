from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

import app.ingestion.async_jobs as async_jobs


def test_process_ingestion_job_marks_completed_and_cleans_file(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    work_dir = Path(".tmp") / "test_async_ingestion_jobs"
    work_dir.mkdir(parents=True, exist_ok=True)
    staged = work_dir / f"{uuid4().hex}.txt"
    staged.write_bytes(b"hello")

    mark_processing = MagicMock()
    mark_completed = MagicMock()
    mark_failed = MagicMock()
    monkeypatch.setattr(async_jobs.ingestion_job_store, "mark_processing", mark_processing)
    monkeypatch.setattr(async_jobs.ingestion_job_store, "mark_completed", mark_completed)
    monkeypatch.setattr(async_jobs.ingestion_job_store, "mark_failed", mark_failed)

    class DummyIngestor:
        def ingest_file(self, **kwargs):
            return {"success": True, "chunks_created": 3}

    monkeypatch.setattr(async_jobs, "UserDocumentIngestor", DummyIngestor)

    result = async_jobs.process_ingestion_job(
        job_id="job-1",
        staged_file_path=str(staged),
        filename="upload.txt",
        session_id="session-1",
        owner_id="owner-1",
    )

    assert result["success"] is True
    mark_processing.assert_called_once_with("job-1")
    mark_completed.assert_called_once_with(job_id="job-1", chunks_created=3)
    mark_failed.assert_not_called()
    assert not staged.exists()


def test_enqueue_ingestion_job_submits_local_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(async_jobs, "_use_celery", lambda: False)

    record = {
        "job_id": "job-1",
        "status": "queued",
        "session_id": "session-1",
        "filename": "upload.txt",
        "owner_id": "owner-1",
        "backend": "local",
        "chunks_created": 0,
        "error": None,
    }
    create_job = MagicMock(return_value=record)
    get_job = MagicMock(return_value=record)
    submit = MagicMock()

    monkeypatch.setattr(async_jobs.ingestion_job_store, "create_job", create_job)
    monkeypatch.setattr(async_jobs.ingestion_job_store, "get_job", get_job)
    monkeypatch.setattr(async_jobs._local_executor, "submit", submit)

    out = async_jobs.enqueue_ingestion_job(
        staged_file_path="C:/tmp/upload.txt",
        filename="upload.txt",
        session_id="session-1",
        owner_id="owner-1",
    )

    assert out["job_id"] == "job-1"
    create_job.assert_called_once()
    submit.assert_called_once()
