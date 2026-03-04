"""
Context Builder — formats reranked chunks into a numbered context string
ready to be injected into the LLM prompt, plus citation metadata.
"""

from __future__ import annotations

from app.utils.logger import get_logger

logger = get_logger(__name__)

_TRUNCATION_SUFFIX = "\n... [truncated]"


class ContextBuilder:
    """
    Converts a ranked list of chunks into a formatted context string
    and structured source-citation metadata.
    """

    def __init__(self, max_context_length: int = 3000) -> None:
        self._max_length = max_context_length

    # ------------------------------------------------------------------

    def build_context(self, chunks: list[dict]) -> str:
        """
        Format *chunks* into a numbered, readable context string.

        Each chunk is rendered as::

            [N] Source: filename.pdf | Domain: tax
            <chunk content>

        Chunks are separated by blank lines.
        The result is hard-capped to ``max_context_length`` characters;
        if truncated, ``"... [truncated]"`` is appended.

        Returns an empty string when *chunks* is empty.
        """
        if not chunks:
            return ""

        parts: list[str] = []
        for idx, chunk in enumerate(chunks, start=1):
            meta = chunk.get("metadata", {})
            source = meta.get("source", "unknown")
            domain = meta.get("domain", "unknown")
            content = chunk.get("content", "")
            parts.append(f"[{idx}] Source: {source} | Domain: {domain}\n{content}")

        context = "\n\n".join(parts)

        if len(context) <= self._max_length:
            return context

        # Truncate and append marker
        truncated = context[: self._max_length] + _TRUNCATION_SUFFIX
        logger.debug(
            "Context truncated from %d to %d chars.",
            len(context),
            len(truncated),
        )
        return truncated

    # ------------------------------------------------------------------

    def build_context_with_metadata(self, chunks: list[dict]) -> dict:
        """
        Build the context string and return it together with structured
        citation metadata.

        Returns
        -------
        {
            "context_string": str,
            "sources": [
                {
                    "reference_id": int,       # matches [N] in context
                    "chunk_id":     str,
                    "source":       str,        # filename
                    "domain":       str,
                    "rerank_score": float | None,
                }
            ],
            "total_chunks": int,
            "truncated": bool,
        }
        """
        context_string = self.build_context(chunks)
        truncated = _TRUNCATION_SUFFIX in context_string

        sources: list[dict] = []
        for idx, chunk in enumerate(chunks, start=1):
            meta = chunk.get("metadata", {})
            sources.append(
                {
                    "reference_id": idx,
                    "chunk_id": chunk.get("chunk_id", ""),
                    "source": meta.get("source", "unknown"),
                    "domain": meta.get("domain", "unknown"),
                    "rerank_score": chunk.get("rerank_score"),  # may be None
                }
            )

        return {
            "context_string": context_string,
            "sources": sources,
            "total_chunks": len(chunks),
            "truncated": truncated,
        }
