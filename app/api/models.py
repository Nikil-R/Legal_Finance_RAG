from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DomainEnum(str, Enum):
    tax = "tax"
    finance = "finance"
    legal = "legal"
    all = "all"


# ============ REQUEST MODELS ============


class QueryRequest(BaseModel):
    """Request model for RAG query endpoint"""

    question: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="The question to ask the RAG system",
        examples=["What are the deductions available under Section 80C?"],
    )
    domain: DomainEnum = Field(
        default=DomainEnum.all,
        description="Filter by domain: tax, finance, legal, or all",
    )
    include_sources: bool = Field(
        default=True, description="Whether to include source documents in response"
    )
    session_id: Optional[str] = Field(
        default=None, description="Optional session ID for conversation memory"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the deductions available under Section 80C?",
                "domain": "tax",
                "include_sources": True,
                "session_id": None,
            }
        }


class RetrievalOnlyRequest(BaseModel):
    """Request model for retrieval-only endpoint (no LLM generation)"""

    question: str = Field(..., min_length=3, max_length=1000)
    domain: DomainEnum = Field(default=DomainEnum.all)
    top_k: int = Field(default=5, ge=1, le=20)


class IngestRequest(BaseModel):
    """Request model for triggering document ingestion"""

    clear_existing: bool = Field(
        default=False,
        description="Whether to clear existing documents before ingesting",
    )


# ============ RESPONSE MODELS ============


class SourceDocument(BaseModel):
    """A source document used in the response"""

    reference_id: int
    source: str
    domain: str
    origin: str = "system"  # "system" or "user"
    relevance_score: float
    excerpt: Optional[str] = None
    citation_spans: list[dict] = Field(default_factory=list)


class UserUploadResponse(BaseModel):
    """Response for user document upload"""

    success: bool
    session_id: str
    filename: str
    status: str = "processing"
    job_id: Optional[str] = None
    chunks_created: Optional[int] = None
    backend: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class UserUploadJobStatusResponse(BaseModel):
    """Status for an asynchronous user-document ingestion job."""

    success: bool
    job_id: str
    session_id: str
    filename: str
    status: str
    chunks_created: int = 0
    backend: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserDocumentInfo(BaseModel):
    """Information about an uploaded user document"""

    filename: str
    uploaded_at: datetime
    chunks: int


class UserDocumentsResponse(BaseModel):
    """Response listing user documents"""

    success: bool
    session_id: str
    documents: list[UserDocumentInfo]
    error: Optional[str] = None


class ValidationResult(BaseModel):
    """Validation results for the generated response"""

    overall_valid: bool
    has_citations: bool
    has_disclaimer: bool
    issues: list[str] = Field(default_factory=list)


class TokenUsage(BaseModel):
    """Token usage statistics"""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class QueryMetadata(BaseModel):
    """Metadata about the query processing"""

    retrieval_candidates: int
    reranked_chunks: int
    top_relevance_score: float
    model: str
    prompt_version: str
    token_usage: TokenUsage
    retrieval_time_ms: float
    generation_time_ms: float
    total_time_ms: float
    guardrails: dict = Field(default_factory=dict)
    query_rewrite: dict = Field(default_factory=dict)
    cache_hit: bool = False


class QueryResponse(BaseModel):
    """Response model for RAG query endpoint"""

    success: bool
    question: str
    domain: str
    answer: Optional[str] = None
    sources: list[SourceDocument] = Field(default_factory=list)
    validation: Optional[ValidationResult] = None
    metadata: Optional[QueryMetadata] = None
    error: Optional[str] = None
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "question": "What are the deductions under Section 80C?",
                "domain": "tax",
                "answer": "Under Section 80C of the Income Tax Act...",
                "sources": [
                    {
                        "reference_id": 1,
                        "source": "income_tax_act.pdf",
                        "domain": "tax",
                        "relevance_score": 0.92,
                        "excerpt": "Section 80C allows...",
                    }
                ],
                "validation": {
                    "overall_valid": True,
                    "has_citations": True,
                    "has_disclaimer": True,
                    "issues": [],
                },
                "metadata": {
                    "retrieval_candidates": 20,
                    "reranked_chunks": 5,
                    "top_relevance_score": 0.92,
                    "model": "llama-3.1-8b-instant",
                    "prompt_version": "v1",
                    "token_usage": {
                        "prompt_tokens": 500,
                        "completion_tokens": 200,
                        "total_tokens": 700,
                    },
                    "retrieval_time_ms": 150,
                    "generation_time_ms": 800,
                    "total_time_ms": 950,
                },
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


class RetrievalResponse(BaseModel):
    """Response for retrieval-only endpoint"""

    success: bool
    question: str
    domain: str
    chunks: list[dict]
    total_found: int
    retrieval_time_ms: float
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    components: dict[str, bool]
    timestamp: datetime


class StatsResponse(BaseModel):
    """System statistics response"""

    total_documents: int
    total_chunks: int
    domains: dict[str, int]
    index_status: str
    last_ingestion: Optional[datetime] = None


class IngestJobResponse(BaseModel):
    """Response for asynchronous ingestion trigger."""

    success: bool
    job_id: str
    status: str
    clear_existing: bool
    backend: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class IngestJobStatusResponse(BaseModel):
    """Status for an asynchronous system-ingestion job."""

    success: bool
    job_id: str
    status: str
    clear_existing: bool
    backend: Optional[str] = None
    documents_loaded: int = 0
    chunks_created: int = 0
    chunks_stored: int = 0
    domains: dict[str, int] = Field(default_factory=dict)
    time_taken_seconds: float = 0
    cache_invalidated: bool = False
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IngestResponse(BaseModel):
    """Response for ingestion endpoint"""

    success: bool
    documents_loaded: int
    chunks_created: int
    chunks_stored: int
    domains: dict[str, int]
    time_taken_seconds: float
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = False
    error: str
    error_type: str
    timestamp: datetime
