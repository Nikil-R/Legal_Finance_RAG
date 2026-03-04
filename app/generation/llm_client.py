"""
Groq API Client — wrapper for interacting with Groq's LLM API.
"""

from __future__ import annotations

import time

from groq import Groq

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GroqClient:
    """Client for Groq LLM services."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL

        if not self.api_key:
            error_msg = (
                "GROQ_API_KEY not found in environment or config. "
                "Please add it to your .env file."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        self.client = Groq(api_key=self.api_key)
        logger.info("Initialized Groq client with model: %s", self.model)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ) -> dict:
        """
        Executes a chat completion request to Groq.
        """
        try:
            start_time = time.perf_counter()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=1.0,
            )

            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000

            usage = response.usage
            logger.info(
                "Generated response: %d tokens in %.1fms",
                usage.total_tokens,
                duration_ms,
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "model": self.model,
                "usage": {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                },
                "finish_reason": response.choices[0].finish_reason,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            error_str = str(e)
            error_type = "unknown"
            if "Rate limit" in error_str:
                error_type = "rate_limit"
            elif "API" in error_str or "Authentication" in error_str:
                error_type = "api_error"

            logger.error("Groq generation failed (%s): %s", error_type, error_str)
            return {"success": False, "error": error_str, "error_type": error_type}

    def health_check(self) -> bool:
        """Verifies API connectivity with a minimal request."""
        try:
            res = self.generate(
                system_prompt="You are a helper.",
                user_prompt="Say 'OK'",
                max_tokens=5,
            )
            return res.get("success", False)
        except Exception:
            return False
