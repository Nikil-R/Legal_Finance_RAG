"""
Frontend component tests.

Note: These are unit tests for frontend utilities.
Full E2E tests would require Selenium/Playwright.
"""

from unittest.mock import MagicMock, patch


class TestAPIClient:
    """Tests for the API client."""

    def test_api_client_initialization(self):
        """Test API client initializes with correct URL."""
        from frontend.utils.api_client import APIClient

        client = APIClient("http://test:8000")
        assert client.base_url == "http://test:8000"

    def test_api_client_default_url(self):
        """Test API client uses default URL."""
        from frontend.config import config
        from frontend.utils.api_client import APIClient

        client = APIClient()
        assert client.base_url == config.API_BASE_URL

    @patch("frontend.utils.api_client.requests")
    def test_health_check_success(self, mock_requests):
        """Test health check parses response correctly."""
        from frontend.utils.api_client import APIClient

        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "healthy", "components": {}}
        mock_response.raise_for_status = MagicMock()
        mock_requests.request.return_value = mock_response

        client = APIClient()
        result = client.health_check()

        assert result["status"] == "healthy"

    @patch("frontend.utils.api_client.requests")
    def test_health_check_connection_error(self, mock_requests):
        """Test health check handles connection errors."""
        import requests

        from frontend.utils.api_client import APIClient

        mock_requests.request.side_effect = requests.exceptions.ConnectionError()
        mock_requests.exceptions = requests.exceptions

        client = APIClient()
        result = client.health_check()

        assert not result["success"]
        assert "Cannot connect" in result["error"]

    @patch("frontend.utils.api_client.requests")
    def test_query_success(self, mock_requests):
        """Test query parses successful response."""
        from frontend.utils.api_client import APIClient

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "question": "Test question",
            "domain": "tax",
            "answer": "Test answer",
            "sources": [],
            "validation": {},
            "metadata": {},
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests.request.return_value = mock_response

        client = APIClient()
        result = client.query("Test question", "tax")

        assert result.success
        assert result.answer == "Test answer"
        assert result.domain == "tax"

    @patch("frontend.utils.api_client.requests")
    def test_query_failure(self, mock_requests):
        """Test query handles failure response."""
        from frontend.utils.api_client import APIClient

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": False,
            "question": "Test question",
            "domain": "tax",
            "error": "No results found",
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests.request.return_value = mock_response

        client = APIClient()
        result = client.query("Test question", "tax")

        assert not result.success
        assert result.error == "No results found"


class TestFrontendConfig:
    """Tests for frontend configuration."""

    def test_config_has_required_fields(self):
        """Test config has all required fields."""
        from frontend.config import config

        assert hasattr(config, "API_BASE_URL")
        assert hasattr(config, "DOMAINS")
        assert hasattr(config, "PAGE_TITLE")

    def test_domains_config(self):
        """Test domains configuration is complete."""
        from frontend.config import config

        required_domains = ["all", "tax", "finance", "legal"]

        for domain in required_domains:
            assert domain in config.DOMAINS
            assert "name" in config.DOMAINS[domain]
            assert "icon" in config.DOMAINS[domain]
            assert "description" in config.DOMAINS[domain]


class TestQueryResult:
    """Tests for QueryResult dataclass."""

    def test_query_result_defaults(self):
        """Test QueryResult has correct defaults."""
        from frontend.utils.api_client import QueryResult

        result = QueryResult(success=True, question="Test", domain="tax")

        assert result.sources == []
        assert result.validation == {}
        assert result.metadata == {}
        assert result.answer is None
        assert result.error is None

    def test_query_result_with_data(self):
        """Test QueryResult stores data correctly."""
        from frontend.utils.api_client import QueryResult

        result = QueryResult(
            success=True,
            question="Test question",
            domain="finance",
            answer="Test answer",
            sources=[{"id": 1}],
            validation={"valid": True},
            metadata={"time_ms": 100},
        )

        assert result.success
        assert result.question == "Test question"
        assert result.domain == "finance"
        assert result.answer == "Test answer"
        assert len(result.sources) == 1
        assert result.validation["valid"]
        assert result.metadata["time_ms"] == 100
