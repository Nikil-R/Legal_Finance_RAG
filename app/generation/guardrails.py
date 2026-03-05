"""
Safety and policy guardrails for the RAG pipeline.
"""

from __future__ import annotations

import re

from app.config import settings


class GuardrailEngine:
    """Applies input, retrieval, and output safety checks."""

    def __init__(self) -> None:
        self._injection_patterns = [
            re.compile(
                r"(ignore|bypass|override).{0,40}(instruction|system prompt|guardrail)",
                re.IGNORECASE,
            ),
            re.compile(r"\b(jailbreak|dan mode|developer mode)\b", re.IGNORECASE),
        ]
        self._illegal_intent_patterns = [
            re.compile(
                r"(how to|ways to|help me).{0,50}(evade tax|hide income|launder|forge|fake documents)",
                re.IGNORECASE,
            ),
            re.compile(r"\b(tax evasion|money laundering)\b", re.IGNORECASE),
        ]
        self._sensitive_patterns = [
            re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),  # PAN
            re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b"),  # Aadhaar-like
        ]

    def validate_input(self, query: str) -> dict:
        """Blocks malicious or clearly unsafe requests before retrieval."""
        clean_query = (query or "").strip()
        if not clean_query:
            return {
                "allowed": False,
                "category": "empty_query",
                "reason": "Query must not be empty.",
                "flags": [],
            }

        for pattern in self._injection_patterns:
            if pattern.search(clean_query):
                return {
                    "allowed": False,
                    "category": "prompt_injection",
                    "reason": "Query blocked by safety policy (prompt-injection pattern detected).",
                    "flags": ["prompt_injection"],
                }

        for pattern in self._illegal_intent_patterns:
            if pattern.search(clean_query):
                return {
                    "allowed": False,
                    "category": "illegal_request",
                    "reason": "Query blocked by safety policy (illegal or evasive intent detected).",
                    "flags": ["illegal_intent"],
                }

        sensitive_hits = sum(
            1 for pattern in self._sensitive_patterns if pattern.search(clean_query)
        )
        flags = ["sensitive_data_detected"] if sensitive_hits else []

        return {
            "allowed": True,
            "category": "ok",
            "reason": "",
            "flags": flags,
        }

    def validate_retrieval(self, retrieval_result: dict) -> dict:
        """
        Ensures generated answers are grounded in sufficiently strong retrieval evidence.
        """
        reranked_chunks = retrieval_result.get("candidates_reranked", 0)
        top_score = float(retrieval_result.get("top_score") or 0.0)

        if reranked_chunks < settings.GUARDRAIL_MIN_RERANKED_CHUNKS:
            return {
                "allowed": False,
                "category": "insufficient_evidence",
                "reason": "Insufficient grounded evidence to answer safely.",
                "flags": ["too_few_chunks"],
            }

        if top_score < settings.GUARDRAIL_MIN_TOP_SCORE:
            return {
                "allowed": False,
                "category": "low_relevance",
                "reason": "Retrieved evidence is too weak to generate a reliable answer.",
                "flags": ["low_top_score"],
            }

        return {"allowed": True, "category": "ok", "reason": "", "flags": []}

    def validate_output(self, answer: str, validation: dict) -> dict:
        """
        Blocks outputs that fail mandatory policy checks after generation.
        """
        issues = list(validation.get("issues", []))
        has_refusal = validation.get("refusal", {}).get("is_refusal", False)

        if not validation.get("overall_valid", False):
            return {
                "allowed": False,
                "category": "validation_failed",
                "reason": "Generated response failed mandatory validation checks.",
                "flags": issues,
            }

        lower_answer = (answer or "").lower()
        if not has_refusal and "guaranteed" in lower_answer and "return" in lower_answer:
            return {
                "allowed": False,
                "category": "unsafe_financial_claim",
                "reason": "Generated response contains unsafe guaranteed financial claims.",
                "flags": ["unsafe_financial_claim"],
            }

        return {"allowed": True, "category": "ok", "reason": "", "flags": []}
