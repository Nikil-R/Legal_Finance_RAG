"""
API endpoint tests — use FastAPI's TestClient (synchronous, no live server needed).
"""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Shared TestClient for the whole module — avoids repeated startup overhead."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ── Health / Root / Config ────────────────────────────────────────────────────


class TestHealthEndpoints:
    def test_root_returns_api_info(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "LegalFinance RAG API"
        assert "version" in data
        assert "docs_url" in data

    def test_health_schema(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "components" in data
        assert "timestamp" in data

    def test_health_components_present(self, client):
        """All expected component keys must be present."""
        data = client.get("/health").json()
        for key in ("api", "groq_api_key_set", "chroma_db", "embeddings_model"):
            assert key in data["components"], f"Missing component: {key}"

    def test_metrics_endpoint_schema(self, client):
        data = client.get("/metrics").json()
        assert "counters" in data
        assert "timings" in data

    def test_config_returns_non_sensitive(self, client):
        """Config endpoint must expose public settings but never the API key."""
        data = client.get("/config").json()
        for key in ("groq_model", "embedding_model", "chunk_size", "top_k_retrieval"):
            assert key in data, f"Missing config key: {key}"
        # Sensitive value must NOT appear in the JSON
        assert "GROQ_API_KEY" not in str(data)

    def test_request_id_header_present(self, client):
        """Middleware adds X-Request-ID to every response."""
        response = client.get("/health")
        assert "x-request-id" in response.headers

    def test_process_time_header_present(self, client):
        """Middleware adds X-Process-Time-Ms to every response."""
        response = client.get("/health")
        assert "x-process-time-ms" in response.headers


# ── Document Endpoints ────────────────────────────────────────────────────────


class TestDocumentEndpoints:
    def test_domains_lists_four_entries(self, client):
        response = client.get("/api/v1/documents/domains")
        assert response.status_code == 200
        data = response.json()
        assert "domains" in data
        ids = {d["id"] for d in data["domains"]}
        assert ids == {"tax", "finance", "legal", "all"}

    def test_stats_schema(self, client):
        response = client.get("/api/v1/documents/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_chunks" in data
        assert "domains" in data
        assert "index_status" in data

    def test_stats_index_status_is_string(self, client):
        data = client.get("/api/v1/documents/stats").json()
        assert isinstance(data["index_status"], str)

    def test_ingest_enqueues_async_job(self, client):
        with patch(
            "app.api.routes.documents.enqueue_system_ingestion_job",
            return_value={
                "job_id": "sys-job-1",
                "status": "queued",
                "backend": "local",
                "clear_existing": True,
            },
        ) as enqueue_job:
            response = client.post(
                "/api/v1/documents/ingest", json={"clear_existing": True}
            )

        assert response.status_code == 202
        data = response.json()
        assert data["job_id"] == "sys-job-1"
        assert data["status"] == "queued"
        assert data["backend"] == "local"
        assert data["clear_existing"] is True
        enqueue_job.assert_called_once_with(clear_existing=True)

    def test_ingest_job_status_not_found(self, client):
        with patch(
            "app.api.routes.documents.system_ingestion_job_store.get_job",
            return_value=None,
        ):
            response = client.get("/api/v1/documents/ingest/jobs/missing-job")

        assert response.status_code == 404

    def test_ingest_job_status_triggers_cache_clear_on_completed_job(self, client):
        queued_record = {
            "job_id": "sys-job-2",
            "status": "completed",
            "clear_existing": False,
            "backend": "celery",
            "documents_loaded": 3,
            "chunks_created": 8,
            "chunks_stored": 8,
            "domains": {"tax": 4, "finance": 2, "legal": 2},
            "time_taken_seconds": 1.25,
            "cache_invalidated": False,
            "error": None,
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:00:01+00:00",
        }
        completed_record = {**queued_record, "cache_invalidated": True}
        with patch(
            "app.api.routes.documents.system_ingestion_job_store.get_job",
            return_value=queued_record,
        ), patch(
            "app.api.routes.documents.system_ingestion_job_store.update_job",
            return_value=completed_record,
        ) as update_job, patch(
            "app.api.routes.documents.clear_pipeline_cache"
        ) as clear_cache:
            response = client.get("/api/v1/documents/ingest/jobs/sys-job-2")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["cache_invalidated"] is True
        clear_cache.assert_called_once()
        update_job.assert_called_once_with("sys-job-2", cache_invalidated=True)


# ── Query Validation ──────────────────────────────────────────────────────────


class TestQueryValidation:
    def test_empty_question_rejected(self, client):
        """Pydantic min_length=3 must reject empty string."""
        response = client.post("/api/v1/query", json={"question": ""})
        assert response.status_code == 422

    def test_too_short_question_rejected(self, client):
        """Two-char question is below min_length=3."""
        response = client.post("/api/v1/query", json={"question": "ab"})
        assert response.status_code == 422

    def test_invalid_domain_rejected(self, client):
        response = client.post(
            "/api/v1/query",
            json={"question": "What is Section 80C?", "domain": "invalid"},
        )
        assert response.status_code == 422

    def test_valid_domain_enum_values(self, client):
        """All four domain values must be accepted (validation only, no success check)."""
        for domain in ("tax", "finance", "legal", "all"):
            r = client.post(
                "/api/v1/query",
                json={"question": "What is Section 80C?", "domain": domain},
            )
            # 200 or 500 (Groq key missing) — but never 422
            assert r.status_code != 422, f"Domain '{domain}' was incorrectly rejected"

    def test_default_domain_is_all(self, client):
        """Omitting domain field should default to 'all'."""
        r = client.post("/api/v1/query", json={"question": "What is Section 80C?"})
        # 422 would mean the default failed
        assert r.status_code != 422

    def test_v2_query_route_available(self, client):
        r = client.post("/api/v2/query", json={"question": "What is Section 80C?"})
        assert r.status_code != 404


# ── Retrieval-Only Endpoint ───────────────────────────────────────────────────


class TestRetrievalEndpoint:
    def test_retrieve_schema(self, client):
        r = client.post(
            "/api/v1/query/retrieve",
            json={"question": "What is Section 80C?", "domain": "tax", "top_k": 3},
        )
        assert r.status_code == 200
        data = r.json()
        assert "success" in data
        assert "chunks" in data
        assert "retrieval_time_ms" in data

    def test_retrieve_top_k_out_of_range_rejected(self, client):
        """top_k=0 is below ge=1, must be rejected."""
        r = client.post(
            "/api/v1/query/retrieve",
            json={"question": "Section 80C?", "top_k": 0},
        )
        assert r.status_code == 422

    def test_retrieve_top_k_above_max_rejected(self, client):
        """top_k=25 is above le=20, must be rejected."""
        r = client.post(
            "/api/v1/query/retrieve",
            json={"question": "Section 80C?", "top_k": 25},
        )
        assert r.status_code == 422


# ── Error Handling ────────────────────────────────────────────────────────────


class TestErrorHandling:
    def test_404_for_nonexistent_path(self, client):
        assert client.get("/does-not-exist-xyz").status_code == 404

    def test_method_not_allowed(self, client):
        """GET on a POST-only endpoint must return 405."""
        assert client.get("/api/v1/query").status_code == 405


# ── Full pipeline (requires live API key) ─────────────────────────────────────


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
class TestQueryWithApiKey:
    def test_full_query_success(self, client):
        r = client.post(
            "/api/v1/query",
            json={
                "question": "What are the deductions under Section 80C?",
                "domain": "tax",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert "success" in data
        assert "question" in data
        assert "timestamp" in data

class TestSessionOwnership:
    def test_user_documents_forbidden_on_owner_mismatch(self, client):
        with patch(
            "app.api.routes.user_documents.verify_session_ownership",
            return_value=False,
        ):
            response = client.get("/api/v1/user/documents", params={"session_id": "abc"})
        assert response.status_code == 403

    def test_user_delete_forbidden_on_owner_mismatch(self, client):
        with patch(
            "app.api.routes.user_documents.verify_session_ownership",
            return_value=False,
        ):
            response = client.delete("/api/v1/user/documents/abc")
        assert response.status_code == 403

    def test_query_forbidden_on_owner_mismatch(self, client):
        with patch(
            "app.api.routes.query.verify_session_ownership",
            return_value=False,
        ):
            response = client.post(
                "/api/v1/query",
                json={
                    "question": "What are Section 80C deductions?",
                    "domain": "tax",
                    "session_id": "abc",
                },
            )
        assert response.status_code == 403


class TestUserUploadLimits:
    def test_user_upload_accepts_file_within_limit(self, client):
        fake_settings = type(
            "FakeSettings",
            (),
            {"USER_UPLOAD_MAX_BYTES": 1024 * 1024, "CHROMA_PERSIST_DIR": "./test_chroma_db"},
        )()
        with patch(
            "app.api.routes.user_documents.get_settings", return_value=fake_settings
        ), patch(
            "app.api.routes.user_documents.enqueue_ingestion_job"
        ) as enqueue_job:
            enqueue_job.return_value = {
                "job_id": "job-123",
                "status": "queued",
                "backend": "local",
                "chunks_created": 0,
            }
            response = client.post(
                "/api/v1/user/upload",
                files={"file": ("small.txt", b"small content", "text/plain")},
            )

        assert response.status_code == 202
        assert response.json()["job_id"] == "job-123"
        enqueue_job.assert_called_once()

    def test_user_upload_rejects_file_over_limit(self, client):
        fake_settings = type(
            "FakeSettings",
            (),
            {"USER_UPLOAD_MAX_BYTES": 64, "CHROMA_PERSIST_DIR": "./test_chroma_db"},
        )()
        with patch(
            "app.api.routes.user_documents.get_settings", return_value=fake_settings
        ), patch(
            "app.api.routes.user_documents.enqueue_ingestion_job"
        ) as enqueue_job:
            response = client.post(
                "/api/v1/user/upload",
                files={"file": ("large.txt", b"x" * 65, "text/plain")},
            )

        assert response.status_code == 413
        assert response.json()["error"] == "File too large"
        enqueue_job.assert_not_called()

    def test_upload_job_status_forbidden_on_owner_mismatch(self, client):
        with patch(
            "app.api.routes.user_documents.ingestion_job_store.get_job",
            return_value={
                "job_id": "job-1",
                "session_id": "session-1",
                "filename": "small.txt",
                "status": "queued",
                "owner_id": "other-user",
            },
        ):
            response = client.get("/api/v1/user/upload/jobs/job-1")
        assert response.status_code == 403

    def test_upload_job_status_returns_record(self, client):
        with patch(
            "app.api.routes.user_documents.ingestion_job_store.get_job",
            return_value={
                "job_id": "job-1",
                "session_id": "session-1",
                "filename": "small.txt",
                "status": "completed",
                "chunks_created": 4,
                "backend": "local",
                "owner_id": "test-user",
                "created_at": "2026-01-01T00:00:00+00:00",
                "updated_at": "2026-01-01T00:00:01+00:00",
            },
        ):
            response = client.get("/api/v1/user/upload/jobs/job-1")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "job-1"
        assert data["status"] == "completed"
        assert data["chunks_created"] == 4
