"""
Frontend configuration settings.
"""

import os


class FrontendConfig:
    """Configuration for the Streamlit frontend."""

    # API Settings
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    API_TIMEOUT: int = 60  # seconds

    # UI Settings
    PAGE_TITLE: str = "LegalFinance RAG"
    PAGE_ICON: str = "⚖️"
    LAYOUT: str = "wide"

    # Domain Configuration
    DOMAINS = {
        "all": {
            "name": "All Domains",
            "icon": "🔍",
            "description": "Search across tax, finance, and legal documents",
        },
        "tax": {
            "name": "Tax Laws",
            "icon": "💰",
            "description": "Income Tax Act, GST, tax deductions and provisions",
        },
        "finance": {
            "name": "Finance",
            "icon": "🏦",
            "description": "RBI guidelines, banking regulations, KYC norms",
        },
        "legal": {
            "name": "Legal",
            "icon": "📜",
            "description": "Contract Act, legal provisions, compliance",
        },
    }

    # Chat Settings
    MAX_HISTORY: int = 50

    # Display Settings
    SHOW_METADATA: bool = True
    SHOW_SOURCES: bool = True
    DEFAULT_EXPANDED_SOURCES: bool = False


config = FrontendConfig()
