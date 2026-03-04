"""
RAG Pipeline — Top-level orchestrator for the entire system.
"""

from __future__ import annotations

import time

from app.generation.generator import RAGGenerator
from app.reranking.pipeline import RetrievalPipeline
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    """Complete end-to-end RAG system."""

    def __init__(self, prompt_version: str = "v1") -> None:
        logger.info("Initializing RAGPipeline with prompt version: %s", prompt_version)
        self.retrieval_pipeline = RetrievalPipeline()
        self.generator = RAGGenerator(prompt_version=prompt_version)
        logger.info("RAGPipeline initialized.")

    def run(self, question: str, domain: str = "all") -> dict:
        """
        Runs the full pipeline.
        """
        start_time = time.perf_counter()
        question = question.strip()

        # 1. Retrieval Phase
        logger.info("Starting Retrieval Phase for: '%s'", question[:50])
        retrieval_result = self.retrieval_pipeline.run(question, domain=domain)

        if not retrieval_result["success"]:
            logger.warning("Retrieval failed: %s", retrieval_result["error"])
            # Return a "failure but successful API object" indicating no info found
            return {
                "success": False,
                "error": retrieval_result["error"],
                "question": question,
                "domain": domain,
                "answer": "I don't have enough information to answer that question.",
                "sources": [],
                "metadata": {
                    "total_time_ms": (time.perf_counter() - start_time) * 1000,
                },
            }

        # 2. Generation Phase
        logger.info("Starting Generation Phase...")
        gen_result = self.generator.generate(
            question=question,
            context=retrieval_result["context"],
            sources=retrieval_result["sources"],
        )

        if not gen_result["success"]:
            logger.error("Generation failed: %s", gen_result.get("error"))
            return {
                "success": False,
                "error": gen_result.get("error", "Unknown generation error"),
                "question": question,
                "metadata": {
                    "total_time_ms": (time.perf_counter() - start_time) * 1000,
                },
            }

        # 3. Final Compilation
        end_time = time.perf_counter()
        total_time_ms = (end_time - start_time) * 1000

        # Create a simplified source list for metadata
        metadata_sources = []
        for src in gen_result["sources"]:
            metadata_sources.append(
                {
                    "reference_id": src["reference_id"],
                    "source": src["source"],
                    "domain": src["domain"],
                    "relevance_score": src.get("rerank_score", 0.0),
                }
            )

        return {
            "success": True,
            "question": question,
            "domain": domain,
            "answer": gen_result["answer"],
            "sources": metadata_sources,
            "validation": gen_result["validation"],
            "metadata": {
                "retrieval_candidates": retrieval_result["candidates_found"],
                "reranked_chunks": retrieval_result["candidates_reranked"],
                "top_relevance_score": retrieval_result["top_score"],
                "model": gen_result["model"],
                "prompt_version": gen_result["prompt_version"],
                "token_usage": gen_result["usage"],
                "retrieval_time_ms": retrieval_result["total_time_ms"],
                "generation_time_ms": gen_result["usage"].get(
                    "duration_ms", 0.0
                ),  # Not always standard in older req
                "total_time_ms": total_time_ms,
            },
            "timestamp": gen_result["timestamp"],
        }

    def run_simple(self, question: str, domain: str = "all") -> str:
        """Just returns the answer string or an error message."""
        result = self.run(question, domain=domain)
        if result["success"]:
            return result["answer"]
        else:
            return f"Error: {result.get('error', 'Could not generate answer')}"
