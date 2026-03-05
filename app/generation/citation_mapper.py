"""
Maps answer citations to source-level highlights.
"""

from __future__ import annotations

import re


class CitationMapper:
    _citation_pattern = re.compile(r"\[(\d+)\]")

    def build_source_highlights(self, answer: str, sources: list[dict]) -> dict[int, list[dict]]:
        """
        Returns mapping: reference_id -> list of highlight spans for UI rendering.
        """
        spans_by_ref: dict[int, list[dict]] = {}
        if not answer or not sources:
            return spans_by_ref

        sentences = re.split(r"(?<=[.!?])\s+", answer)
        source_map = {int(s.get("reference_id", -1)): s for s in sources}

        for sentence in sentences:
            refs = [int(m) for m in self._citation_pattern.findall(sentence)]
            if not refs:
                continue
            clean_sentence = self._citation_pattern.sub("", sentence).strip()
            if not clean_sentence:
                continue
            claim = clean_sentence[:240]
            for ref in refs:
                src = source_map.get(ref)
                if not src:
                    continue
                excerpt = (src.get("excerpt") or "")[:1000]
                lower_excerpt = excerpt.lower()
                lower_claim = claim.lower()
                start = lower_excerpt.find(lower_claim[:64]) if excerpt else -1
                end = start + min(len(claim), len(excerpt[start:])) if start >= 0 else -1
                span = {
                    "claim": claim,
                    "start": start,
                    "end": end,
                }
                spans_by_ref.setdefault(ref, []).append(span)
        return spans_by_ref
