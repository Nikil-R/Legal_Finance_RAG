"""
Health check and system status endpoints.
"""
from fastapi import APIRouter
from datetime import datetime, timezone
import chromadb
from app.api.models import HealthResponse
from app.config import settings
from app.utils.logger import get_logger

router = APIRouter(tags=["Health"])
logger = get_logger(__name__)


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Returns the health status of the API and its components."
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    """
    # Check components
    components = {
        "api": True,
        "groq_api_key_set": bool(settings.GROQ_API_KEY),
        "chroma_db": False,
        "embeddings_model": False
    }
    
    # Check ChromaDB
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        client.heartbeat()
        components["chroma_db"] = True
    except Exception as e:
        logger.warning("ChromaDB health check failed: %s", e)
    
    # Check embeddings model (just verify it's configured)
    components["embeddings_model"] = bool(settings.EMBEDDING_MODEL)
    
    # Overall status
    critical_components = ["api", "groq_api_key_set", "chroma_db"]
    all_critical_healthy = all(components.get(c, False) for c in critical_components)
    status = "healthy" if all_critical_healthy else "degraded"
    
    return HealthResponse(
        status=status,
        version="0.1.0",
        components=components,
        timestamp=datetime.now(timezone.utc)
    )


@router.get(
    "/",
    summary="Root endpoint",
    description="Returns basic API information."
)
async def root() -> dict:
    """
    Root endpoint with API info.
    """
    return {
        "name": "LegalFinance RAG API",
        "version": "0.1.0",
        "description": "RAG system for Indian tax, finance, and legal documents",
        "docs_url": "/docs",
        "health_url": "/health"
    }


@router.get(
    "/config",
    summary="Get non-sensitive configuration",
    description="Returns non-sensitive configuration values for debugging."
)
async def get_config() -> dict:
    """
    Returns non-sensitive config values.
    """
    return {
        "groq_model": settings.GROQ_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "cross_encoder_model": settings.CROSS_ENCODER_MODEL,
        "chunk_size": settings.CHUNK_SIZE,
        "chunk_overlap": settings.CHUNK_OVERLAP,
        "top_k_retrieval": settings.TOP_K_RETRIEVAL,
        "top_k_rerank": settings.TOP_K_RERANK,
        "temperature": settings.TEMPERATURE,
        "chroma_persist_dir": settings.CHROMA_PERSIST_DIR
    }
