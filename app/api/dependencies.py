"""
FastAPI dependencies for injecting services into routes.
Uses caching to avoid reinitializing heavy models on each request.
"""
from functools import lru_cache
from app.generation import RAGPipeline
from app.reranking import RetrievalPipeline
from app.retrieval import HybridRetriever
from app.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache()
def get_rag_pipeline() -> RAGPipeline:
    """
    Returns a cached RAGPipeline instance.
    The pipeline is initialized once and reused for all requests.
    """
    logger.info("Initializing RAGPipeline (this may take a moment on first call)...")
    pipeline = RAGPipeline()
    logger.info("RAGPipeline initialized successfully")
    return pipeline


@lru_cache()
def get_retrieval_pipeline() -> RetrievalPipeline:
    """
    Returns a cached RetrievalPipeline instance.
    Used for retrieval-only endpoints.
    """
    logger.info("Initializing RetrievalPipeline...")
    pipeline = RetrievalPipeline()
    logger.info("RetrievalPipeline initialized successfully")
    return pipeline


@lru_cache()
def get_retriever() -> HybridRetriever:
    """
    Returns a cached HybridRetriever instance.
    Used for stats and health checks.
    """
    return HybridRetriever()


def clear_pipeline_cache():
    """
    Clears the cached pipeline instances.
    Call this after re-ingestion to pick up new documents.
    """
    get_rag_pipeline.cache_clear()
    get_retrieval_pipeline.cache_clear()
    get_retriever.cache_clear()
    logger.info("Pipeline caches cleared")
