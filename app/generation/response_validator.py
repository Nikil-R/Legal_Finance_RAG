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
        Checks if citations in response are present and valid for the number of sources.
        """
        citations = [int(match) for match in self.citation_pattern.findall(response)]
        unique_citations = sorted(list(set(citations)))

        has_citations = len(unique_citations) > 0
        invalid_citations = [c for c in unique_citations if c < 1 or c > num_sources]

        valid = has_citations and len(invalid_citations) == 0

        message = ""
        if not has_citations:
            message = "No citations found in the response."
        elif invalid_citations:
            message = f"Invalid citations found: {invalid_citations}. Max valid is {num_sources}."

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
        has_title = "disclaimer" in lower_resp
        has_content = (
            "educational purposes" in lower_resp
            or "not be considered as professional" in lower_resp
        )

        valid = has_title and has_content

        return {
            "valid": valid,
            "has_disclaimer": valid,
            "message": (
                "" if valid else "Mandatory disclaimer is missing or incomplete."
            ),
        }

    def validate_refusal(self, response: str) -> dict:
        """Detects if the LLM refused to answer due to lack of evidence."""
        refusal_patterns = [
            "cannot find sufficient information",
            "not have enough information",
            "not able to answer",
            "please consult a qualified professional",
            "consult a qualified professional",
        ]

        lower_resp = response.lower()
        for pattern in refusal_patterns:
            if pattern in lower_resp:
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

        return {
            "overall_valid": overall_valid,
            "citations": citations,
            "disclaimer": disclaimer,
            "refusal": refusal,
            "issues": issues,
        }
