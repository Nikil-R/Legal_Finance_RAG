"""
User Document Ingestor — handles isolated document ingestion for user sessions.
"""

import os
from pathlib import Path
from datetime import datetime
import uuid

from app.ingestion.loader import DocumentLoader
from app.ingestion.chunker import DocumentChunker
from app.ingestion.embedder import VectorStoreManager
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserDocumentIngestor:
    """Handles uploading, text extraction, and storage for user-specific documents."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP
        )
        self.upload_dir = Path("data/user_uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _load_docx(self, file_path: str) -> str:
        """Extract text from a .docx file."""
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as exc:
            logger.warning("Could not read DOCX '%s': %s", file_path, exc)
            return ""

    def ingest_file(self, content: bytes, filename: str, session_id: str) -> dict:
        """
        Accept file content, extract text, chunk, and store in a session-specific collection.
        """
        # 1. Save file temporarily
        session_dir = self.upload_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        file_path = session_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(content)

        # 2. Extract text
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            text = self.loader.load_pdf(str(file_path))
        elif suffix == ".txt":
            text = self.loader.load_txt(str(file_path))
        elif suffix == ".docx":
            text = self._load_docx(str(file_path))
        else:
            return {"success": False, "error": f"Unsupported file type: {suffix}"}

        if not text.strip():
            return {"success": False, "error": "No text content found in file"}

        # 3. Create document object for chunker
        doc = {
            "content": text,
            "metadata": {
                "source": filename,
                "domain": "user_upload",
                "file_path": str(file_path),
                "session_id": session_id,
                "uploaded_at": datetime.now().isoformat(),
                "origin": "user"
            }
        }

        # 4. Chunk
        chunks = self.chunker.chunk_document(doc)
        if not chunks:
            return {"success": False, "error": "Could not split document into chunks"}

        # 5. Embed and store in isolated collection
        collection_name = f"user_docs_{session_id}"
        vsm = VectorStoreManager(
            persist_dir=self.settings.CHROMA_PERSIST_DIR,
            embedding_model=self.settings.EMBEDDING_MODEL,
            collection_name=collection_name
        )
        stored_count = vsm.embed_and_store(chunks)

        logger.info(
            "Ingested user file '%s' into collection '%s' (%d chunks).",
            filename,
            collection_name,
            stored_count
        )

        return {
            "success": True,
            "filename": filename,
            "chunks_created": stored_count,
            "session_id": session_id
        }
