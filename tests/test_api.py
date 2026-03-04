"""
API endpoint tests — use FastAPI's TestClient (synchronous, no live server needed).
"""

from __future__ import annotations

import os

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
