from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import app.ingestion.system_async_jobs as system_async_jobs


def test_process_system_ingestion_job_marks_completed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mark_processing = MagicMock()
    mark_completed = MagicMock()
    mark_failed = MagicMock()
    monkeypatch.setattr(
        system_async_jobs.system_ingestion_job_store, "mark_processing", mark_processing
    )
    monkeypatch.setattr(
        system_async_jobs.system_ingestion_job_store, "mark_completed", mark_completed
    )
    monkeypatch.setattr(
        system_async_jobs.system_ingestion_job_store, "mark_failed", mark_failed
    )

    monkeypatch.setattr(
        system_async_jobs,
        "run_ingestion_pipeline",
        lambda clear_existing: {
            "documents_loaded": 2,
            "chunks_created": 6,
            "chunks_stored": 6,
            "domain_breakdown": {"tax": 4, "legal": 2},
        },
    )
    clear_cache = MagicMock()
    monkeypatch.setattr(system_async_jobs, "clear_pipeline_cache", clear_cache)

    result = system_async_jobs.process_system_ingestion_job(
        job_id="job-1",
        clear_existing=True,
        backend="local",
    )

    assert result["success"] is True
    mark_processing.assert_called_once_with("job-1")
    mark_completed.assert_called_once()
    mark_failed.assert_not_called()
    clear_cache.assert_called_once()

    kwargs = mark_completed.call_args.kwargs
    assert kwargs["job_id"] == "job-1"
    assert kwargs["documents_loaded"] == 2
    assert kwargs["chunks_created"] == 6
    assert kwargs["chunks_stored"] == 6
    assert kwargs["domains"] == {"tax": 4, "legal": 2}
    assert kwargs["cache_invalidated"] is True


def test_enqueue_system_ingestion_job_submits_local_worker(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(system_async_jobs, "_use_celery", lambda: False)

    record = {
        "job_id": "job-1",
        "status": "queued",
        "clear_existing": False,
        "backend": "local",
        "documents_loaded": 0,
        "chunks_created": 0,
        "chunks_stored": 0,
        "domains": {},
        "time_taken_seconds": 0.0,
        "cache_invalidated": False,
        "error": None,
    }
    create_job = MagicMock(return_value=record)
    get_job = MagicMock(return_value=record)
    submit = MagicMock()

    monkeypatch.setattr(
        system_async_jobs.system_ingestion_job_store, "create_job", create_job
    )
    monkeypatch.setattr(system_async_jobs.system_ingestion_job_store, "get_job", get_job)
    monkeypatch.setattr(system_async_jobs._local_executor, "submit", submit)

    out = system_async_jobs.enqueue_system_ingestion_job(clear_existing=False)

    assert out["job_id"] == "job-1"
    create_job.assert_called_once()
    submit.assert_called_once()
    kwargs = submit.call_args.kwargs
    assert kwargs["backend"] == "local"
