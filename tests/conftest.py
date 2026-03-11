"""
Pytest configuration and shared fixtures.
"""

import os
import shutil
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ============ Environment Setup ============

_LOCAL_TMP_ROOT = Path.home() / ".codex" / "memories" / "pytest_tmp_root"


def _make_local_tmp_dir(prefix: str) -> Path:
    _LOCAL_TMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = _LOCAL_TMP_ROOT / f"{prefix}{uuid.uuid4().hex[:10]}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def pytest_configure(config):
    """Configure pytest environment."""
    # Set test environment
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "WARNING"
    os.environ["API_AUTH_ENABLED"] = "true"
    os.environ["API_KEYS"] = "admin:admin_key_12345,query:query_key_67890"
    os.environ["API_KEY_ROLES"] = "admin:admin,query:query"
    os.environ["API_KEY_MIN_LENGTH"] = "1"
    os.environ["API_REQUIRE_KEY_ID"] = "false"
    os.environ["REJECT_DEFAULT_API_KEYS"] = "false"

    # Use test ChromaDB directory
    os.environ["CHROMA_PERSIST_DIR"] = "./test_chroma_db"


def pytest_unconfigure(config):
    """Cleanup after tests."""
    # Clean up test directories
    test_chroma = Path("./test_chroma_db")
    if test_chroma.exists():
        shutil.rmtree(test_chroma, ignore_errors=True)
    if _LOCAL_TMP_ROOT.exists():
        shutil.rmtree(_LOCAL_TMP_ROOT, ignore_errors=True)


# ============ Fixtures ============


@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary test data directory with sample documents."""
    data_dir = _make_local_tmp_dir("data_")

    # Create domain subdirectories
    (data_dir / "raw" / "tax").mkdir(parents=True)
    (data_dir / "raw" / "finance").mkdir(parents=True)
    (data_dir / "raw" / "legal").mkdir(parents=True)

    # Create sample documents
    tax_content = """
    Income Tax Act, 1961 - Section 80C
    
    Section 80C of the Income Tax Act allows deductions up to Rs 1,50,000 
    from gross total income for specified investments and expenses.
    
    Eligible investments include:
    1. Public Provident Fund (PPF)
    2. Employee Provident Fund (EPF)
    3. National Savings Certificate (NSC)
    4. Equity Linked Savings Scheme (ELSS) with 3-year lock-in
    5. Life Insurance Premium payments
    6. Fixed Deposits with 5-year lock-in period
    """

    finance_content = """
    Reserve Bank of India - KYC Guidelines 2023
    
    The Reserve Bank of India mandates Know Your Customer (KYC) norms 
    for all regulated entities including banks, NBFCs, and payment system operators.
    
    Key Requirements:
    1. Customer Identification using Aadhaar, PAN, Passport, or Voter ID
    2. Customer Due Diligence (CDD) with risk-based approach
    3. Periodic KYC updation every 2 years for high-risk customers
    """

    legal_content = """
    Indian Contract Act, 1872 - Key Provisions
    
    Section 2(h): An agreement enforceable by law is a contract.
    
    Section 10: All agreements are contracts if made by free consent 
    of parties competent to contract, for lawful consideration.
    
    Section 14: Free Consent - Consent is free when not caused by 
    coercion, undue influence, fraud, or misrepresentation.
    """

    (data_dir / "raw" / "tax" / "income_tax.txt").write_text(tax_content)
    (data_dir / "raw" / "finance" / "rbi_kyc.txt").write_text(finance_content)
    (data_dir / "raw" / "legal" / "contract_act.txt").write_text(legal_content)

    return data_dir


@pytest.fixture(scope="session")
def chroma_test_dir():
    """Create temporary ChromaDB directory."""
    return _make_local_tmp_dir("chroma_")


@pytest.fixture
def tmp_path():
    """Workspace-local replacement for pytest tmp_path fixture on Windows sandbox."""
    path = _make_local_tmp_dir("case_")
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def mock_groq_client():
    """Mock Groq client for tests without API calls."""
    # Note: Using the actual path in app.generation.llm_client
    with patch("app.generation.llm_client.Groq") as mock:
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="Test response with citation [1].\n\n---\n**Disclaimer:** For educational purposes only."
                ),
                finish_reason="stop",
            )
        ]
        mock_response.usage = MagicMock(
            prompt_tokens=100, completion_tokens=50, total_tokens=150
        )
        mock_instance.chat.completions.create.return_value = mock_response
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("app.config.get_settings") as mock:
        settings = MagicMock()
        settings.GROQ_API_KEY = "test-api-key"
        settings.GROQ_MODEL = "llama-3.1-8b-instant"
        settings.CHROMA_PERSIST_DIR = "./test_chroma_db"
        settings.EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
        settings.CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        settings.CHUNK_SIZE = 512
        settings.CHUNK_OVERLAP = 50
        settings.TOP_K_RETRIEVAL = 20
        settings.TOP_K_RERANK = 5
        settings.TEMPERATURE = 0.0
        mock.return_value = settings
        yield settings


@pytest.fixture
def sample_chunks():
    """Sample chunks for testing."""
    return [
        {
            "content": "Section 80C allows deductions up to Rs 1,50,000 for PPF and ELSS investments.",
            "metadata": {
                "chunk_id": "tax_001_chunk_0",
                "source": "income_tax.txt",
                "domain": "tax",
                "chunk_index": 0,
            },
        },
        {
            "content": "RBI mandates KYC norms for all banks including Aadhaar verification.",
            "metadata": {
                "chunk_id": "finance_001_chunk_0",
                "source": "rbi_kyc.txt",
                "domain": "finance",
                "chunk_index": 0,
            },
        },
        {
            "content": "Section 2(h) defines a contract as an agreement enforceable by law.",
            "metadata": {
                "chunk_id": "legal_001_chunk_0",
                "source": "contract_act.txt",
                "domain": "legal",
                "chunk_index": 0,
            },
        },
    ]


@pytest.fixture
def sample_query_response():
    """Sample RAG pipeline response."""
    return {
        "success": True,
        "question": "What are Section 80C deductions?",
        "domain": "tax",
        "answer": "Under Section 80C, taxpayers can claim deductions up to Rs 1,50,000 [1].\n\n---\n**Disclaimer:** For educational purposes only.",
        "sources": [
            {
                "reference_id": 1,
                "source": "income_tax.txt",
                "domain": "tax",
                "relevance_score": 0.92,
                "excerpt": "Section 80C allows deductions...",
            }
        ],
        "validation": {
            "overall_valid": True,
            "citations": {"has_citations": True, "citations_found": [1]},
            "disclaimer": {"has_disclaimer": True},
        },
        "metadata": {
            "retrieval_candidates": 20,
            "reranked_chunks": 5,
            "top_relevance_score": 0.92,
            "model": "llama-3.1-8b-instant",
            "prompt_version": "v1",
            "token_usage": {
                "prompt_tokens": 500,
                "completion_tokens": 100,
                "total_tokens": 600,
            },
            "total_time_ms": 1500,
        },
    }


# ============ Markers ============


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location."""
    for item in items:
        # Add markers based on test path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

        # Mark tests that require API key
        if "groq" in item.name.lower() or "api_key" in item.name.lower():
            item.add_marker(pytest.mark.requires_api_key)


# ============ Skip Conditions ============


@pytest.fixture
def skip_without_api_key():
    """Skip test if GROQ_API_KEY not set."""
    if not os.getenv("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set")


@pytest.fixture
def skip_in_ci():
    """Skip test in CI environment."""
    if os.getenv("CI"):
        pytest.skip("Skipping in CI environment")
