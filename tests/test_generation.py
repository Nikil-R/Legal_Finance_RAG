"""
Tests for the generation subsystem (PromptManager, ResponseValidator, RAGPipeline).
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.generation.response_validator import ResponseValidator
from app.prompts.prompt_manager import PromptManager


# ── PromptManager Tests ───────────────────────────────────────────────────────


class TestPromptManager:
    def test_prompt_manager_load(self):
        """Should load v1 prompt YAML correctly."""
        pm = PromptManager()
        data = pm.load_prompt("v1")

        assert data["version"] == "v1"
        assert "system_prompt" in data
        assert "user_prompt_template" in data
        assert "parameters" in data
        assert "ONLY use information from the provided context" in data["system_prompt"]

    def test_prompt_manager_format(self):
        """Should format user prompt with context and question placeholders."""
        pm = PromptManager()
        context = "Source [1]: Content A"
        question = "What is A?"

        prompt = pm.format_user_prompt("v1", context, question)
        assert "## CONTEXT:" in prompt
        assert "## QUESTION:" in prompt
        assert context in prompt
        assert question in prompt

    def test_prompt_manager_invalid_version(self):
        """Should raise FileNotFoundError for non-existent versions."""
        pm = PromptManager()
        with pytest.raises(FileNotFoundError):
            pm.load_prompt("v999")


# ── ResponseValidator Tests ───────────────────────────────────────────────────


class TestResponseValidator:
    def test_citations_valid(self):
        validator = ResponseValidator()
        resp = "Tax is 10% [1]. Refund is 5% [2] according to [1][2]."
        res = validator.validate_citations(resp, num_sources=3)

        assert res["valid"] is True
        assert res["citations_found"] == [1, 2]
        assert res["invalid_citations"] == []
        assert res["has_citations"] is True

    def test_citations_invalid_range(self):
        validator = ResponseValidator()
        resp = "Refer to [5] for details."
        res = validator.validate_citations(resp, num_sources=3)

        assert res["valid"] is False
        assert res["invalid_citations"] == [5]

    def test_citations_missing(self):
        validator = ResponseValidator()
        resp = "Taxes are good for the country."
        res = validator.validate_citations(resp, num_sources=3)

        assert res["has_citations"] is False
        assert res["valid"] is False

    def test_disclaimer_present(self):
        validator = ResponseValidator()
        resp = "Answer content...\n--- Disclaimer: educational purposes..."
        res = validator.validate_disclaimer(resp)
        assert res["valid"] is True

    def test_disclaimer_missing(self):
        validator = ResponseValidator()
        resp = "Answer content without disclaimer."
        res = validator.validate_disclaimer(resp)
        assert res["valid"] is False

    def test_refusal_detection(self):
        validator = ResponseValidator()
        resp = "I cannot find sufficient information to answer this question."
        res = validator.validate_refusal(resp)
        assert res["is_refusal"] is True
        assert res["refusal_phrase"] == "cannot find sufficient information"


# ── RAG Pipeline Integration Tests (Mocked/Conditional) ────────────────────────


class TestRAGPipeline:
    @pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
    def test_pipeline_full_run(self):
        """Full run test. Requires active Groq API key."""
        from app.generation.pipeline import RAGPipeline

        pipeline = RAGPipeline()
        res = pipeline.run("What are the deductions under Section 80C?", domain="tax")

        assert res["success"] is True
        assert len(res["answer"]) > 0
        assert "[" in res["answer"]  # Should have citations
        assert len(res["sources"]) > 0
        assert res["metadata"]["total_time_ms"] > 0
