from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- LLM ---
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"

    # --- Vector Store ---
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # --- Embedding & Reranking Models ---
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CROSS_ENCODER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    # --- Chunking ---
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50

    # --- Retrieval ---
    TOP_K_RETRIEVAL: int = 20
    TOP_K_RERANK: int = 5

    # --- Generation ---
    TEMPERATURE: float = 0.0

    # --- Guardrails ---
    ENABLE_GUARDRAILS: bool = True
    GUARDRAIL_MIN_TOP_SCORE: float = 0.15
    GUARDRAIL_MIN_RERANKED_CHUNKS: int = 1
    ENABLE_QUERY_REWRITE: bool = True

    # --- Logging ---
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    SLOW_REQUEST_THRESHOLD_MS: int = 2000

    # --- API ---
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = "*"
    API_AUTH_ENABLED: bool = True
    API_KEYS: str = ""
    API_KEYS_HASHED: str = ""
    API_KEY_MIN_LENGTH: int = 24
    API_REQUIRE_KEY_ID: bool = False
    API_KEY_HEADER_NAME: str = "x-api-key"
    API_KEY_ID_HEADER_NAME: str = "x-api-key-id"
    REJECT_DEFAULT_API_KEYS: bool = True
    RATE_LIMIT_RPM: int = 120
    REQUEST_TIMEOUT_SECONDS: int = 45
    REDIS_URL: str = ""
    REDIS_KEY_PREFIX: str = "legal_finance_rag"
    INGESTION_QUEUE_BACKEND: str = "auto"  # auto | celery | local
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    INGESTION_LOCAL_WORKERS: int = 2
    INGESTION_JOB_TTL_SECONDS: int = 24 * 60 * 60

    # --- Cache ---
    ENABLE_QUERY_CACHE: bool = True
    QUERY_CACHE_TTL_SECONDS: int = 300

    ENVIRONMENT: str = "development"
    TESTING: bool = False

    # --- LLM Reliability ---
    LLM_REQUEST_TIMEOUT_SECONDS: int = 40
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_BACKOFF_SECONDS: float = 1.0

    # --- Compliance ---
    PII_REDACTION_ENABLED: bool = True
    USER_DOC_RETENTION_DAYS: int = 30
    USER_UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024

    # --- Evaluation Gate ---
    EVAL_GATE_MIN_PASS_RATE: float = 0.8
    EVAL_GATE_MIN_FAITHFULNESS: float = 0.7
    EVAL_GATE_MIN_CORRECTNESS: float = 0.6
    EVAL_GATE_MIN_CITATION_QUALITY: float = 0.8
    EVAL_GATE_MIN_RETRIEVAL_RELEVANCE: float = 0.5


@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings instance."""
    return Settings()


settings = get_settings()
