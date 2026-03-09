import os

import pytest
from fastapi.testclient import TestClient

# Ensure local env before app import (SecretsManager requires GROQ_API_KEY/REDIS_URL)
os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("GROQ_API_KEY", "local-test-key")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.main import app  # noqa: E402

client = TestClient(app)


def _reset_rate_limits():
    try:
        import redis

        limiter_client = redis.Redis.from_url("redis://localhost:6379/1")
        limiter_client.flushdb()
    except Exception:
        pass


def test_no_api_key_returns_401():
    response = client.post("/api/v1/query", json={"question": "test"})
    assert response.status_code == 401
    assert "Missing X-API-Key" in response.json()["detail"]


def test_invalid_api_key_returns_401():
    response = client.post(
        "/api/v1/query",
        json={"question": "test"},
        headers={"X-API-Key": "invalid_key"},
    )
    assert response.status_code == 401


def test_query_role_can_query():
    response = client.post(
        "/api/v1/query",
        json={"question": "test"},
        headers={"X-API-Key": "query_key_67890"},
    )
    assert response.status_code == 200


def test_query_role_cannot_upload():
    response = client.post(
        "/api/v1/documents/ingest",
        files={"file": ("test.pdf", b"content", "application/pdf")},
        headers={"X-API-Key": "query_key_67890"},
    )
    assert response.status_code == 403
    assert "Forbidden" in response.json()["detail"]


def test_admin_can_delete():
    response = client.delete(
        "/api/v1/documents/test123",
        headers={"X-API-Key": "admin_key_12345"},
    )
    assert response.status_code == 200


@pytest.mark.usefixtures("_reset_limit_on_failure")
def test_rate_limiting_blocks_excessive_requests():
    _reset_rate_limits()
    response = None
    for i in range(61):
        response = client.post(
            "/api/v1/query",
            json={"question": f"test {i}"},
            headers={"X-API-Key": "query_key_67890"},
        )

    assert response is not None
    assert response.status_code == 429
    assert response.json()["error"] == "Rate limit exceeded"


@pytest.fixture(autouse=True)
def _reset_limit_on_failure():
    yield
    _reset_rate_limits()
