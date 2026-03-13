"""
Main Generator — handles prompting LLMs and validating the final response.
"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional

from app.generation.llm_fabric import LLMFabric
from app.generation.response_validator import ResponseValidator
from app.prompts.prompt_manager import PromptManager
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGGenerator:
    """Generates answers using LLMs with retrieved context."""

    def __init__(self, prompt_version: str = "v1") -> None:
        self.prompt_version = prompt_version
        self.prompt_manager = PromptManager()
        self.llm_fabric = LLMFabric()
        self.validator = ResponseValidator()
        logger.info(
            "RAGGenerator initialized with prompt version: %s", self.prompt_version
        )

    @property
    def system_prompt(self) -> str:
        """Returns the system prompt according to current version."""
        return self.prompt_manager.get_system_prompt(self.prompt_version)

    def generate(
        self, 
        question: str, 
        context: str, 
        sources: list[dict],
        history: list[dict] = None
    ) -> dict:
        """
        Generates a grounded answer based on question and context.
        """
        if not question.strip():
            logger.warning("RAGGenerator received an empty question.")
            return {"success": False, "error": "Question is empty"}

        # 1. Get Prompts
        try:
            system_prompt = self.prompt_manager.get_system_prompt(self.prompt_version)
            
            # Format history for the prompt
            history_str = ""
            if history:
                history_str = "\n".join([f"{h['role'].capitalize()}: {h['content']}" for h in history])
            
            user_prompt = self.prompt_manager.format_user_prompt(
                self.prompt_version, context, question
            )
            
            # Append history if present
            if history_str:
                user_prompt = f"Previous conversation history:\n{history_str}\n\nCurrent question based on context and history:\n{user_prompt}"

            params = self.prompt_manager.get_parameters(self.prompt_version)
        except Exception as e:
            logger.error("Failed to prepare prompts: %s", str(e))
            return {"success": False, "error": f"Prompt error: {str(e)}"}

        # 2. Call LLM
        llm_result = self.llm_fabric.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=params.get("temperature", 0.0),
            max_tokens=params.get("max_tokens", 1024),
        )

        if not llm_result["success"]:
            return llm_result

        # 3. Validate Response
        response_text = llm_result["content"]
        validation = self.validator.validate_response(response_text, len(sources))

        # 4. Post-process: Auto-add disclaimer if missing
        if not validation["disclaimer"]["valid"]:
            logger.warning("Disclaimer missing in LLM response, auto-appending.")
            disclaimer_text = (
                "\n\n---\n**Disclaimer:** This information is for educational purposes only "
                "and should not be considered as professional legal, tax, or financial advice. "
                "Please consult qualified professionals for advice specific to your situation."
            )
            response_text += disclaimer_text
            # Re-validate after fixing
            validation = self.validator.validate_response(response_text, len(sources))

        return {
            "success": True,
            "answer": response_text,
            "question": question,
            "sources": sources,
            "validation": validation,
            "usage": llm_result["usage"],
            "duration_ms": llm_result.get("duration_ms", 0.0),
            "model": llm_result["model"],
            "prompt_version": self.prompt_version,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z",
        }

    def generate_with_retrieval(
        self, question: str, domain: str = "all", session_id: str | None = None
    ) -> dict:
        """
        End-to-end: retrieval + generation.
        """
        from app.reranking.pipeline import RetrievalPipeline

        # Initialize here to avoid circular imports at top level if any exists
        pipeline = RetrievalPipeline()
        retrieval_result = pipeline.run(question, domain=domain, session_id=session_id)

        if not retrieval_result["success"]:
            # Even if retrieval fails, we can either error out or ask LLM with empty context
            # Usually better to return the retrieval failure directly for cleaner error messages
            return {
                "success": False,
                "error": retrieval_result["error"],
                "retrieval_stats": retrieval_result,
            }

        gen_result = self.generate(
            question=question,
            context=retrieval_result["context"],
            sources=retrieval_result["sources"],
        )

        # Merge retrieval stats into result
        if gen_result["success"]:
            gen_result["retrieval_stats"] = {
                "candidates_found": retrieval_result["candidates_found"],
                "candidates_reranked": retrieval_result["candidates_reranked"],
                "top_score": retrieval_result["top_score"],
                "total_time_ms": retrieval_result["total_time_ms"],
            }

        return gen_result
