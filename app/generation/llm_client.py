"""
Groq API Client — wrapper for interacting with Groq's LLM API.
"""

from __future__ import annotations

import random
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError

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
        def _single_call() -> object:
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
            return response

        start_time = time.perf_counter()
        attempts = max(1, int(settings.LLM_MAX_RETRIES))
        last_error = "unknown error"

        for attempt in range(1, attempts + 1):
            try:
                with ThreadPoolExecutor(max_workers=1) as pool:
                    future = pool.submit(_single_call)
                    response = future.result(
                        timeout=float(settings.LLM_REQUEST_TIMEOUT_SECONDS)
                    )

                end_time = time.perf_counter()
                duration_ms = (end_time - start_time) * 1000

                usage = response.usage
                logger.info(
                    "Generated response: %d tokens in %.1fms (attempt=%d/%d)",
                    usage.total_tokens,
                    duration_ms,
                    attempt,
                    attempts,
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
            except FutureTimeoutError:
                last_error = (
                    f"LLM request timed out after {settings.LLM_REQUEST_TIMEOUT_SECONDS}s"
                )
                logger.warning(
                    "Groq request timeout (attempt=%d/%d): %s",
                    attempt,
                    attempts,
                    last_error,
                )
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    "Groq request failed (attempt=%d/%d): %s",
                    attempt,
                    attempts,
                    last_error,
                )

            if attempt < attempts:
                base = max(0.1, float(settings.LLM_RETRY_BACKOFF_SECONDS))
                jitter = random.uniform(0.0, 0.25)  # nosec B311 \x2014 Non-cryptographic use (retry jitter)
                sleep_for = (base * (2 ** (attempt - 1))) + jitter
                time.sleep(sleep_for)

        error_type = "unknown"
        if "rate limit" in last_error.lower():
            error_type = "rate_limit"
        elif "timeout" in last_error.lower():
            error_type = "timeout"
        elif "api" in last_error.lower() or "authentication" in last_error.lower():
            error_type = "api_error"

        logger.error("Groq generation failed (%s): %s", error_type, last_error)
        return {"success": False, "error": last_error, "error_type": error_type}

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
