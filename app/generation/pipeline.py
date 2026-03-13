"""
Top-level RAG pipeline orchestrator.
"""

from __future__ import annotations

import copy
import hashlib
import time
from typing import Any, Dict, List, Optional, cast

from app.config import settings
from app.generation.citation_mapper import CitationMapper
from app.generation.generator import RAGGenerator
from app.generation.vision_handler import VisionHandler
from app.generation.guardrails import GuardrailEngine
from app.observability import metrics, prom_bridge
from app.reranking.pipeline import RetrievalPipeline
from app.utils.cache import TTLCache, ChatHistory
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGPipeline:
    def __init__(self, prompt_version: str = "v1") -> None:
        logger.info("Initializing RAGPipeline with prompt version: %s", prompt_version)
        self.retrieval_pipeline = RetrievalPipeline()
        self.generator = RAGGenerator(prompt_version=prompt_version)
        self.vision = VisionHandler()
        self.guardrails = GuardrailEngine()
        self.citation_mapper = CitationMapper()
        self._cache = TTLCache(ttl_seconds=settings.QUERY_CACHE_TTL_SECONDS)
        self.chat_history = ChatHistory()
        logger.info("RAGPipeline initialized.")

    def _cache_key(
        self,
        question: str,
        domain: str,
        session_id: str | None,
        owner_id: str | None,
    ) -> str:
        raw = (
            f"{domain}|{owner_id or ''}|{session_id or ''}|{question.strip().lower()}"
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def run(
        self,
        question: str,
        domain: str = "all",
        session_id: str | None = None,
        owner_id: str | None = None,
        image_url: str | None = None,
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

        cache_key = self._cache_key(question, domain, session_id, owner_id)
        if settings.ENABLE_QUERY_CACHE:
            cached = self._cache.get(cache_key)
            if cached is not None:
                metrics.inc("query_cache_hit_total")
                result = cast(Dict[str, Any], copy.deepcopy(cached))
                if "metadata" not in result:
                    result["metadata"] = {}
                result["metadata"]["cache_hit"] = True
                return result
            metrics.inc("query_cache_miss_total")

        # Retrieve chat history
        history = self.chat_history.get_history(session_id) if session_id else []

        # --- Phase 0: Vision Analysis (Multimodal) ---
        vision_context = ""
        if image_url:
            logger.info("Processing multimodal input (image)...")
            # We run OCR/Analysis via Gemini
            import asyncio
            vision_result = asyncio.run(self.vision.analyze_document_image(image_url))
            vision_context = f"\n### Scanned Document Content:\n{vision_result.get('analysis', '')}\n"

        # --- Phase 1: Retrieval ---
        retrieval_res = self.retrieval_pipeline.run(
            question, domain=domain, session_id=session_id, owner_id=owner_id
        )
        if not retrieval_res["success"]:
            metrics.inc("query_retrieval_failed_total")
            prom_bridge.inc_query("failed_retrieval")
            return {
                "success": False,
                "error": retrieval_res["error"],
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
            retrieval_guard = self.guardrails.validate_retrieval(retrieval_res)
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

        # --- Phase 2: Generation ---
        # Add vision data to context if available
        full_context = f"{vision_context}\n{retrieval_res['context']}"
        
        gen_result = self.generator.generate(
            question=question,
            context=full_context,
            domain=domain,
            sources=retrieval_res["sources"],
            history=history,
        )
        
        # Store in history if successful
        if gen_result["success"] and session_id:
            self.chat_history.add_turn(session_id, "user", question)
            self.chat_history.add_turn(session_id, "assistant", gen_result["answer"])
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
            gen_result["answer"], retrieval_res["sources"]
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
        metrics.observe_ms("retrieval_latency_ms", retrieval_res.get("total_time_ms", 0.0))
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
                "retrieval_candidates": retrieval_res["candidates_found"],
                "reranked_chunks": retrieval_res["candidates_reranked"],
                "top_relevance_score": retrieval_res["top_score"],
                "model": gen_result["model"],
                "prompt_version": gen_result["prompt_version"],
                "token_usage": gen_result["usage"],
                "retrieval_time_ms": retrieval_res["total_time_ms"],
                "generation_time_ms": gen_result.get("duration_ms", 0.0),
                "total_time_ms": total_time_ms,
                "guardrails": guardrail_state,
                "query_rewrite": retrieval_res.get("query_rewrite", {}),
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
