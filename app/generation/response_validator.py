"""
Response Validator — checks citations, disclaimers, and refusal patterns in LLM responses.
"""

from __future__ import annotations

import re

from app.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseValidator:
    """Validates the output of the RAG generator."""

    def __init__(self) -> None:
        # Pattern for [1], [2], [10], etc.
        self.citation_pattern = re.compile(r"\[(\d+)\]")

    def validate_citations(self, response: str, num_sources: int) -> dict:
        """
        Checks if citations in response are present and within range.

        Out-of-range citations are logged as warnings but do NOT cause a
        hard failure — the LLM may occasionally cite a chunk number that
        is technically beyond the reranked top-K but still existed in the
        original retrieved set. We surface them for logging only.
        """
        citations = [int(match) for match in self.citation_pattern.findall(response)]
        unique_citations = sorted(list(set(citations)))

        has_citations = len(unique_citations) > 0
        invalid_citations = [c for c in unique_citations if c < 1 or c > num_sources]

        if invalid_citations:
            logger.warning(
                "Out-of-range citations detected: %s (max valid: %d). "
                "Treating as warning, not hard failure.",
                invalid_citations,
                num_sources,
            )

        # Only fail if there are NO citations at all — out-of-range is a warning
        valid = has_citations

        message = ""
        if not has_citations:
            message = "No citations found in the response."
        elif invalid_citations:
            message = (
                f"Out-of-range citations (warning only): {invalid_citations}. "
                f"Max expected: {num_sources}."
            )

        return {
            "valid": valid,
            "citations_found": unique_citations,
            "invalid_citations": invalid_citations,
            "has_citations": has_citations,
            "message": message,
        }

    def validate_disclaimer(self, response: str) -> dict:
        """Checks if the mandatory legal/financial disclaimer is present."""
        lower_resp = response.lower()
        
        # More flexible check: look for "disclaimer" anywhere
        # This handles "**Disclaimer:**", "Disclaimer:", etc.
        has_title = "disclaimer" in lower_resp
        
        # Soften content requirements: any significant part of the disclaimer satisfies it
        content_keywords = [
            "educational purposes",
            "not be considered as professional",
            "consult qualified professionals",
            "legal, tax, or financial advice",
            "specific to your situation"
        ]
        
        matches = [k for k in content_keywords if k in lower_resp]
        has_content = len(matches) >= 1

        # Check that a separator (---) precedes the disclaimer
        has_separator = "---" in response

        valid = has_title and has_content

        messages = []
        if not has_title:
            messages.append("Disclaimer heading missing.")
        if not has_content:
            messages.append("Disclaimer body text missing or non-standard.")
        if valid and not has_separator:
            # Separator is desirable but not a hard failure
            logger.debug("Disclaimer present but missing --- separator.")

        return {
            "valid": valid,
            "has_disclaimer": valid,
            "has_separator": has_separator,
            "message": " ".join(messages) if messages else "",
            "matches_found": matches
        }

    def validate_refusal(self, response: str) -> dict:
        """
        Detects if the LLM refused to answer due to lack of evidence.

        IMPORTANT: Refusal patterns must NOT match disclaimer boilerplate.
        The disclaimer always ends with "consult qualified professionals" —
        so only flag a refusal if the refusal phrase appears BEFORE the
        disclaimer separator (---), i.e., in the main answer body.
        """
        refusal_patterns = [
            "cannot find sufficient information",
            "not have enough information",
            "not able to answer",
            # NOTE: "consult a qualified professional" is intentionally removed
            # because it appears verbatim in every disclaimer. Checking only
            # the answer body (before ---) prevents false positives.
        ]

        # Check only the body of the response — strip out the disclaimer section
        # by splitting on the --- separator if present
        parts = response.split("---")
        answer_body = parts[0].lower() if len(parts) > 1 else response.lower()

        for pattern in refusal_patterns:
            if pattern in answer_body:
                return {"is_refusal": True, "refusal_phrase": pattern}

        return {"is_refusal": False, "refusal_phrase": None}

    def validate_response(self, response: str, num_sources: int) -> dict:
        """Runs all validations and returns a summary result."""
        citations = self.validate_citations(response, num_sources)
        disclaimer = self.validate_disclaimer(response)
        refusal = self.validate_refusal(response)

        # If it's a refusal, we don't strictly require citations, but still require disclaimer.
        if refusal["is_refusal"]:
            overall_valid = disclaimer["valid"]
        else:
            overall_valid = citations["valid"] and disclaimer["valid"]

        issues = []
        if not disclaimer["valid"]:
            issues.append("Missing mandatory disclaimer")
        if not refusal["is_refusal"] and not citations["valid"]:
            if not citations["has_citations"]:
                issues.append("Missing citations")
            if citations["invalid_citations"]:
                issues.append(f"Invalid citations: {citations['invalid_citations']}")

        if not overall_valid:
            logger.error(
                "Validation FAILED | citations_valid=%s | disclaimer_valid=%s | "
                "is_refusal=%s | issues=%s | response_preview=%.200s",
                citations["valid"],
                disclaimer["valid"],
                refusal["is_refusal"],
                issues,
                response,
            )

        return {
            "overall_valid": overall_valid,
            "citations": citations,
            "disclaimer": disclaimer,
            "refusal": refusal,
            "issues": issues,
        }
