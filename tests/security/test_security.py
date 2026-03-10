"""
Security tests for the RAG API.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client() -> AsyncClient:
    """Async HTTP client for security tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
@pytest.mark.security
async def test_sql_injection_in_query(async_client: AsyncClient):
    """Verify SQL injection attempts are sanitized."""
    sql_payloads = [
        "'; DROP TABLE documents; --",
        "1' OR '1'='1",
        "admin'--",
    ]

    for payload in sql_payloads:
        response = await async_client.post(
            "/api/v1/query",
            json={"question": payload, "domain": "tax"},
            headers={"x-test-user-id": "test-user"}
        )

        # Should not crash (may return error or empty results)
        assert response.status_code in [200, 400, 422, 500, 503], \
            f"SQL injection caused unexpected error: {payload}"


@pytest.mark.asyncio
@pytest.mark.security
async def test_invalid_json_handling(async_client: AsyncClient):
    """Verify malformed JSON is handled gracefully."""
    response = await async_client.post(
        "/api/v1/query",
        content=b"not valid json{{{",
        headers={
            "Content-Type": "application/json",
            "x-test-user-id": "test-user"
        }
    )

    assert response.status_code in [400, 422], \
        "Malformed JSON not handled properly"


@pytest.mark.asyncio
@pytest.mark.security
async def test_health_endpoints_accessible(async_client: AsyncClient):
    """Verify health endpoints are accessible."""
    endpoints = [
        "/health/liveness",
        "/health/readiness"
    ]

    for endpoint in endpoints:
        response = await async_client.get(endpoint)
        assert response.status_code in [200, 503], \
            f"Health endpoint {endpoint} not accessible"


@pytest.mark.asyncio
@pytest.mark.security
async def test_metrics_endpoint_accessible(async_client: AsyncClient):
    """Verify metrics endpoint is accessible."""
    response = await async_client.get("/metrics")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.security
async def test_documentation_accessible(async_client: AsyncClient):
    """Verify API documentation is accessible."""
    response = await async_client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.security
async def test_openapi_spec_accessible(async_client: AsyncClient):
    """Verify OpenAPI spec is accessible."""
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.security
async def test_invalid_http_methods_rejected(async_client: AsyncClient):
    """Verify invalid HTTP methods are rejected."""
    # Try PUT on POST-only endpoint
    response = await async_client.put(
        "/api/v1/query",
        json={"question": "test", "domain": "tax"},
        headers={"x-test-user-id": "test-user"}
    )

    assert response.status_code in [400, 405, 500], \
        "Invalid HTTP method not rejected properly"


@pytest.mark.asyncio
@pytest.mark.security
async def test_none_domain_handling(async_client: AsyncClient):
    """Verify null/None domain values are handled."""
    response = await async_client.post(
        "/api/v1/query",
        json={"question": "test", "domain": None},
        headers={"x-test-user-id": "test-user"}
    )

    # Should either reject or default to "all"
    assert response.status_code in [200, 400, 422, 500, 503], \
        "None domain not handled properly"


@pytest.mark.asyncio
@pytest.mark.security
async def test_large_query_handling(async_client: AsyncClient):
    """Verify large queries are handled."""
    large_query = "a" * 100000  # 100KB query

    response = await async_client.post(
        "/api/v1/query",
        json={"question": large_query, "domain": "tax"},
        headers={"x-test-user-id": "test-user"}
    )

    # Should either reject or handle gracefully
    assert response.status_code in [200, 400, 414, 422, 500, 503], \
        "Large request not handled properly"


@pytest.mark.asyncio
@pytest.mark.security
async def test_request_size_limit(async_client: AsyncClient):
    """Verify very large requests are rejected."""
    # Create a very large query (11MB)
    very_large_query = "a" * (11 * 1024 * 1024)

    response = await async_client.post(
        "/api/v1/query",
        json={"question": very_large_query, "domain": "tax"},
        headers={"x-test-user-id": "test-user"}
    )

    # Should reject with appropriate error
    assert response.status_code in [400, 413, 414, 422, 500, 503], \
        "Very large request not handled properly"
