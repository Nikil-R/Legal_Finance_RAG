"""
Document Chunker — splits raw document text into overlapping chunks.

Input document shape (from DocumentLoader):
    {
        "content": "<full text>",
        "metadata": { "source": ..., "domain": ..., "file_path": ... }
    }

Output chunk shape:
    {
        "content": "<chunk text>",
        "metadata": {
            "source":      "<filename>",
            "domain":      "tax" | "finance" | "legal",
            "file_path":   "<path>",
            "chunk_index": 0,
            "chunk_id":    "<source_stem>_chunk_0",
        }
    }
"""

import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.logger import get_logger

logger = get_logger(__name__)


def _make_chunk_id(source: str, index: int) -> str:
    """Build a filesystem-safe unique chunk ID from a filename and index."""
    stem = re.sub(r"[^a-zA-Z0-9_]", "_", source)  # replace dots / spaces / etc.
    return f"{stem}_chunk_{index}"


class DocumentChunker:
    """Splits documents into overlapping text chunks using LangChain's splitter."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            length_function=len,
            is_separator_regex=False,
        )
        logger.info(
            "DocumentChunker initialised (chunk_size=%d, chunk_overlap=%d).",
            chunk_size,
            chunk_overlap,
        )

    # ------------------------------------------------------------------

    def chunk_document(self, document: dict) -> list[dict]:
        """
        Split a single document into chunks and enrich each chunk's metadata.

        Returns an empty list if the document content is blank.
        """
        content: str = document.get("content", "")
        base_meta: dict = document.get("metadata", {})

        if not content.strip():
            logger.warning(
                "Document '%s' has no content; skipping chunking.",
                base_meta.get("source", "<unknown>"),
            )
            return []

        raw_chunks: list[str] = self._splitter.split_text(content)
        source: str = base_meta.get("source", "unknown")

        chunks: list[dict] = []
        for idx, text in enumerate(raw_chunks):
            chunk_meta = {
                **base_meta,
                "chunk_index": idx,
                "chunk_id": _make_chunk_id(source, idx),
            }
            chunks.append({"content": text, "metadata": chunk_meta})

        return chunks

    # ------------------------------------------------------------------

    def chunk_all(self, documents: list[dict]) -> list[dict]:
        """
        Chunk every document and return a flat list of all chunks.

        Logs the total number of chunks created.
        """
        all_chunks: list[dict] = []
        for doc in documents:
            all_chunks.extend(self.chunk_document(doc))

        logger.info(
            "Total chunks created: %d from %d document(s).",
            len(all_chunks),
            len(documents),
        )
        return all_chunks
