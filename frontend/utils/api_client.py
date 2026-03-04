"""
Client for communicating with the FastAPI backend.
"""
import requests
from typing import Optional
from dataclasses import dataclass
from frontend.config import config


@dataclass
class QueryResult:
    """Structured result from a query."""
    success: bool
    question: str
    domain: str
    answer: Optional[str] = None
    sources: list = None
    validation: dict = None
    metadata: dict = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.validation is None:
            self.validation = {}
        if self.metadata is None:
            self.metadata = {}


class APIClient:
    """Client for the LegalFinance RAG API."""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or config.API_BASE_URL
        self.timeout = config.API_TIMEOUT
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", self.timeout)
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timed out. Please try again."}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Cannot connect to API server. Is it running?"}
        except requests.exceptions.HTTPError as e:
            return {"success": False, "error": f"HTTP Error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def health_check(self) -> dict:
        """Check API health status."""
        return self._make_request("GET", "/health")
    
    def get_stats(self) -> dict:
        """Get document statistics."""
        return self._make_request("GET", "/api/v1/documents/stats")
    
    def get_domains(self) -> dict:
        """Get available domains."""
        return self._make_request("GET", "/api/v1/documents/domains")
    
    def query(self, question: str, domain: str = "all", include_sources: bool = True, session_id: str = None) -> QueryResult:
        """
        Send a query to the RAG system.
        
        Args:
            question: The question to ask
            domain: Domain filter (tax, finance, legal, all)
            include_sources: Whether to include source documents
            session_id: Optional session ID for user-document isolation
        
        Returns:
            QueryResult with answer and metadata
        """
        payload = {
            "question": question,
            "domain": domain,
            "include_sources": include_sources,
            "session_id": session_id
        }
        
        result = self._make_request("POST", "/api/v1/query", json=payload)
        
        return QueryResult(
            success=result.get("success", False),
            question=result.get("question", question),
            domain=result.get("domain", domain),
            answer=result.get("answer"),
            sources=result.get("sources", []),
            validation=result.get("validation", {}),
            metadata=result.get("metadata", {}),
            error=result.get("error")
        )
    
    def retrieve_only(self, question: str, domain: str = "all", top_k: int = 5) -> dict:
        """Retrieve relevant chunks without LLM generation."""
        payload = {
            "question": question,
            "domain": domain,
            "top_k": top_k
        }
        return self._make_request("POST", "/api/v1/query/retrieve", json=payload)
    
    def trigger_ingestion(self, clear_existing: bool = False) -> dict:
        """Trigger document ingestion."""
        payload = {"clear_existing": clear_existing}
        return self._make_request("POST", "/api/v1/documents/ingest", json=payload)
    
    def is_healthy(self) -> bool:
        """Quick check if API is reachable and healthy."""
        try:
            result = self.health_check()
            return result.get("status") == "healthy"
        except:
            return False


# Global client instance
api_client = APIClient()
