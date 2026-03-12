"""
FastAPI dependencies with resilient fallback instances.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import TYPE_CHECKING

import chromadb

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from app.generation import RAGPipeline, ToolOrchestrator
    from app.reranking import RetrievalPipeline
    from app.tools.executor import ToolExecutor
    from app.tools.registry import ToolRegistry


class _FallbackRAGPipeline:
    def run(
        self,
        question: str,
        domain: str = "all",
        session_id: str | None = None,
        owner_id: str | None = None,
    ) -> dict:
        return {
            "success": False,
            "error": "RAG pipeline unavailable (startup/dependency error).",
            "question": question,
            "domain": domain,
            "sources": [],
            "metadata": {"total_time_ms": 0.0, "degraded_mode": True},
        }


class _FallbackRetrievalPipeline:
    def run(
        self,
        query: str,
        domain: str = "all",
        retrieval_top_k: int = 20,
        rerank_top_k: int = 5,
        min_relevance_score: float = -5.0,
        session_id: str | None = None,
        owner_id: str | None = None,
    ) -> dict:
        return {
            "success": False,
            "error": "Retrieval pipeline unavailable (startup/dependency error).",
            "query": query,
            "domain": domain,
            "sources": [],
            "candidates_found": 0,
            "total_time_ms": 0.0,
            "degraded_mode": True,
        }


class _FallbackRetriever:
    def get_stats(self) -> dict:
        return {"total_documents": 0, "total_chunks": 0, "domains": {}}


class _StatsRetriever:
    def get_stats(self) -> dict:
        if os.getenv("TESTING", "").lower() == "true":
            return {"total_documents": 0, "total_chunks": 0, "domains": {}}
        try:
            client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
            col = client.get_collection("legal_finance_docs")
        except Exception:
            return {"total_documents": 0, "total_chunks": 0, "domains": {}}

        total = col.count()
        domains: dict[str, int] = {}
        for domain in ("tax", "finance", "legal"):
            try:
                res = col.get(where={"domain": {"$eq": domain}}, include=[])
                domains[domain] = len(res["ids"])
            except Exception:
                domains[domain] = 0
        return {"total_documents": total, "total_chunks": total, "domains": domains}


@lru_cache()
def get_rag_pipeline() -> RAGPipeline | _FallbackRAGPipeline:
    logger.info("Initializing RAGPipeline...")
    try:
        from app.generation import RAGPipeline

        return RAGPipeline()
    except Exception as exc:
        logger.error("RAGPipeline initialization failed: %s", exc)
        return _FallbackRAGPipeline()


@lru_cache()
def get_retrieval_pipeline() -> RetrievalPipeline | _FallbackRetrievalPipeline:
    logger.info("Initializing RetrievalPipeline...")
    try:
        from app.reranking import RetrievalPipeline

        return RetrievalPipeline()
    except Exception as exc:
        logger.error("RetrievalPipeline initialization failed: %s", exc)
        return _FallbackRetrievalPipeline()


@lru_cache()
def get_retriever() -> _StatsRetriever | _FallbackRetriever:
    try:
        return _StatsRetriever()
    except Exception as exc:
        logger.error("Stats retriever initialization failed: %s", exc)
        return _FallbackRetriever()


@lru_cache()
def get_tool_registry() -> ToolRegistry:
    from app.tools.registry import ToolRegistry

    return ToolRegistry()

@lru_cache()
def get_tool_executor() -> ToolExecutor:
    from app.tools.executor import ToolExecutor

    registry = get_tool_registry()
    return ToolExecutor(registry)

@lru_cache()
def get_tool_orchestrator() -> ToolOrchestrator:
    from app.generation import GroqClient, ToolOrchestrator

    client = GroqClient()
    registry = get_tool_registry()
    executor = get_tool_executor()
    return ToolOrchestrator(client, registry, executor)

def clear_pipeline_cache():
    get_rag_pipeline.cache_clear()
    get_retrieval_pipeline.cache_clear()
    get_retriever.cache_clear()
    get_tool_registry.cache_clear()
    get_tool_executor.cache_clear()
    get_tool_orchestrator.cache_clear()
    logger.info("Pipeline caches cleared")
