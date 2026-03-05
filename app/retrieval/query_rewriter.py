"""
Query rewriting for robust retrieval (normalization + domain-aware expansion).
"""

from __future__ import annotations

import re


class QueryRewriter:
    def __init__(self) -> None:
        self._alias_map = {
            "80c": "section 80c deduction ppf elss nsc",
            "gst": "goods and services tax",
            "kyc": "know your customer",
            "tds": "tax deducted at source",
            "rbi": "reserve bank of india",
            "sebi": "securities and exchange board of india",
        }

    def rewrite(self, query: str, domain: str = "all") -> dict:
        clean = re.sub(r"\s+", " ", (query or "").strip().lower())
        expanded_terms: list[str] = []
        for token, expansion in self._alias_map.items():
            if token in clean:
                expanded_terms.append(expansion)

        domain_hint = ""
        if domain == "tax":
            domain_hint = "income tax act cgt gst cbdt"
        elif domain == "finance":
            domain_hint = "rbi banking compliance circular"
        elif domain == "legal":
            domain_hint = "act section clause legal provision"

        parts = [clean]
        if domain_hint:
            parts.append(domain_hint)
        if expanded_terms:
            parts.extend(expanded_terms)

        rewritten = " ".join(parts).strip()
        return {"original_query": query, "rewritten_query": rewritten}
