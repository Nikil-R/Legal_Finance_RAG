"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health endpoints."""
    
    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert "name" in response.json()
    
    def test_health(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data


class TestQueryEndpoints:
    """Tests for query endpoints."""
    
    def test_query_validation(self, client):
        """Test query validation."""
        # Empty question
        response = client.post("/api/v1/query", json={"question": ""})
        assert response.status_code == 422
        
        # Too short
        response = client.post("/api/v1/query", json={"question": "ab"})
        assert response.status_code == 422
    
    def test_query_invalid_domain(self, client):
        """Test query with invalid domain."""
        response = client.post(
            "/api/v1/query",
            json={"question": "What is tax?", "domain": "invalid"}
        )
        assert response.status_code == 422
    
    @pytest.mark.requires_api_key
    def test_query_success(self, client, skip_without_api_key):
        """Test successful query."""
        response = client.post(
            "/api/v1/query",
            json={
                "question": "What are Section 80C deductions?",
                "domain": "tax"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "success" in data


class TestDocumentEndpoints:
    """Tests for document endpoints."""
    
    def test_get_stats(self, client):
        """Test stats endpoint."""
        response = client.get("/api/v1/documents/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_chunks" in data
    
    def test_get_domains(self, client):
        """Test domains endpoint."""
        response = client.get("/api/v1/documents/domains")
        
        assert response.status_code == 200
        data = response.json()
        assert "domains" in data
