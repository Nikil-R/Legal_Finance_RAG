import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("GROQ_API_KEY", "test-groq")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_root():
    response = client.get("/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "checks" in data


def test_liveness():
    response = client.get("/health/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness():
    response = client.get("/health/readiness")
    assert response.status_code in (200, 503)


def test_metrics_exposed():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "query_requests_total" in response.text


def test_query_hits_metrics():
    response = client.post(
        "/api/v1/query",
        headers={"X-API-Key": "query_key_67890"},
        json={"question": "test query"},
    )
    assert response.status_code == 200
    metrics_snapshot = client.get("/metrics").text
    assert "query_requests_total" in metrics_snapshot
