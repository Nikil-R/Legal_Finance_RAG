"""
Top-level RAG pipeline orchestrator.
"""

from __future__ import annotations

import copy
import hashlib
import time

from app.config import settings
from app.generation.citation_mapper import CitationMapper
from app.generation.guardrails import GuardrailEngine
from app.generation.generator import RAGGenerator
from app.observability import metrics, prom_bridge
from app.reranking.pipeline import RetrievalPipeline
from app.utils.cache import TTLCache
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    def __init__(self, prompt_version: str = "v1") -> None:
        logger.info("Initializing RAGPipeline with prompt version: %s", prompt_version)
        self.retrieval_pipeline = RetrievalPipeline()
        self.generator = RAGGenerator(prompt_version=prompt_version)
        self.guardrails = GuardrailEngine()
        self.citation_mapper = CitationMapper()
        self._cache = TTLCache(ttl_seconds=settings.QUERY_CACHE_TTL_SECONDS)
        logger.info("RAGPipeline initialized.")

    def _cache_key(self, question: str, domain: str, session_id: str | None) -> str:
        raw = f"{domain}|{session_id or ''}|{question.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def run(
        self,
        question: str,
        domain: str = "all",
        session_id: str | None = None,
    ) -> dict:
        start_time = time.perf_counter()
        question = question.strip()
        metrics.inc("query_requests_total")
        guardrail_state = {
            "enabled": settings.ENABLE_GUARDRAILS,
            "input": {"allowed": True, "category": "ok", "reason": "", "flags": []},
            "retrieval": {"allowed": True, "category": "ok", "reason": "", "flags": []},
            "output": {"allowed": True, "category": "ok", "reason": "", "flags": []},
        }

        if settings.ENABLE_GUARDRAILS:
            input_guard = self.guardrails.validate_input(question)
            guardrail_state["input"] = input_guard
            if not input_guard["allowed"]:
                metrics.inc("guardrail_input_block_total")
                prom_bridge.inc_query("blocked_input")
                return {
                    "success": False,
                    "error": input_guard["reason"],
                    "question": question,
                    "domain": domain,
                    "answer": "I cannot help with that request.",
                    "sources": [],
                    "metadata": {
                        "total_time_ms": (time.perf_counter() - start_time) * 1000,
                        "guardrails": guardrail_state,
                    },
                }

        cache_key = self._cache_key(question, domain, session_id)
        if settings.ENABLE_QUERY_CACHE:
            cached = self._cache.get(cache_key)
            if cached is not None:
                metrics.inc("query_cache_hit_total")
                result = copy.deepcopy(cached)
                result["metadata"]["cache_hit"] = True
                return result
            metrics.inc("query_cache_miss_total")

        retrieval_result = self.retrieval_pipeline.run(
            question, domain=domain, session_id=session_id
        )
        if not retrieval_result["success"]:
            metrics.inc("query_retrieval_failed_total")
            prom_bridge.inc_query("failed_retrieval")
            return {
                "success": False,
                "error": retrieval_result["error"],
                "question": question,
                "domain": domain,
                "answer": "I don't have enough information to answer that question.",
                "sources": [],
                "metadata": {
                    "total_time_ms": (time.perf_counter() - start_time) * 1000,
                    "guardrails": guardrail_state,
                },
            }

        if settings.ENABLE_GUARDRAILS:
            retrieval_guard = self.guardrails.validate_retrieval(retrieval_result)
            guardrail_state["retrieval"] = retrieval_guard
            if not retrieval_guard["allowed"]:
                metrics.inc("guardrail_retrieval_block_total")
                prom_bridge.inc_query("blocked_retrieval")
                return {
                    "success": False,
                    "error": retrieval_guard["reason"],
                    "question": question,
                    "domain": domain,
                    "answer": "I don't have enough grounded evidence to answer this safely.",
                    "sources": [],
                    "metadata": {
                        "total_time_ms": (time.perf_counter() - start_time) * 1000,
                        "guardrails": guardrail_state,
                    },
                }

        gen_result = self.generator.generate(
            question=question,
            context=retrieval_result["context"],
            sources=retrieval_result["sources"],
        )
        if not gen_result["success"]:
            metrics.inc("query_generation_failed_total")
            prom_bridge.inc_query("failed_generation")
            return {
                "success": False,
                "error": gen_result.get("error", "Unknown generation error"),
                "question": question,
                "metadata": {
                    "total_time_ms": (time.perf_counter() - start_time) * 1000,
                    "guardrails": guardrail_state,
                },
            }

        if settings.ENABLE_GUARDRAILS:
            output_guard = self.guardrails.validate_output(
                gen_result["answer"], gen_result["validation"]
            )
            guardrail_state["output"] = output_guard
            if not output_guard["allowed"]:
                metrics.inc("guardrail_output_block_total")
                prom_bridge.inc_query("blocked_output")
                return {
                    "success": False,
                    "error": output_guard["reason"],
                    "question": question,
                    "domain": domain,
                    "answer": "I cannot provide a safe answer for this request.",
                    "sources": [],
                    "metadata": {
                        "total_time_ms": (time.perf_counter() - start_time) * 1000,
                        "guardrails": guardrail_state,
                    },
                }

        citation_spans = self.citation_mapper.build_source_highlights(
            gen_result["answer"], retrieval_result["sources"]
        )
        metadata_sources = []
        for src in gen_result["sources"]:
            ref_id = int(src["reference_id"])
            metadata_sources.append(
                {
                    "reference_id": ref_id,
                    "source": src["source"],
                    "domain": src["domain"],
                    "origin": src.get("origin", "system"),
                    "relevance_score": src.get("rerank_score", 0.0),
                    "excerpt": src.get("excerpt", ""),
                    "content": src.get("content", ""),
                    "citation_spans": citation_spans.get(ref_id, []),
                }
            )

        total_time_ms = (time.perf_counter() - start_time) * 1000
        metrics.observe_ms("query_total_latency_ms", total_time_ms)
        metrics.observe_ms("retrieval_latency_ms", retrieval_result.get("total_time_ms", 0.0))
        metrics.observe_ms("generation_latency_ms", gen_result.get("duration_ms", 0.0))
        metrics.inc("query_success_total")
        prom_bridge.inc_query("success")

        result = {
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
                "generation_time_ms": gen_result.get("duration_ms", 0.0),
                "total_time_ms": total_time_ms,
                "guardrails": guardrail_state,
                "query_rewrite": retrieval_result.get("query_rewrite", {}),
                "cache_hit": False,
            },
            "timestamp": gen_result["timestamp"],
        }
        if settings.ENABLE_QUERY_CACHE:
            self._cache.set(cache_key, copy.deepcopy(result))
        return result

    def run_simple(self, question: str, domain: str = "all") -> str:
        result = self.run(question, domain=domain)
        if result["success"]:
            return result["answer"]
        return f"Error: {result.get('error', 'Could not generate answer')}"
