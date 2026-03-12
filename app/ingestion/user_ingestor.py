"""
User Document Ingestor — handles isolated document ingestion for user sessions.
"""

import re
import secrets
from datetime import datetime
from pathlib import Path

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal and remove special characters.
    
    Guarantees:
    1. Strip directories (Path.name)
    2. Remove non-alphanumeric/special chars ([^\\w\\-.])
    3. Block hidden files and parent directory references
    """
    # 1. Strip directories
    safe = Path(filename).name
    
    # 2. Remove special characters (keep alphanum, underscore, hyphen, dot)
    safe = re.sub(r'[^\w\-.]', '_', safe)
    
    # 3. Block hidden files and parent directory references
    if '..' in safe or safe.startswith('.'):
        raise ValueError("Invalid filename")
        
    return safe


def sanitize_upload(filename: str, storage_dir: Path) -> Path:
    """
    Build a safe upload path inside ``storage_dir``.

    Security guarantees:
    1. Strip any incoming path components.
    2. Normalize filename to a safe character set.
    3. Add a random prefix to avoid collisions.
    4. Enforce that resolved path remains inside ``storage_dir``.
    """
    # Start with the user's requested stricter logic
    safe_basename = sanitize_filename(filename)
    
    # 2. Add random prefix for collision safety
    unique_name = f"{secrets.token_hex(8)}_{safe_basename}"
    storage_root = storage_dir.resolve()
    save_path = (storage_root / unique_name).resolve()

    if not save_path.is_relative_to(storage_root):
        raise ValueError("Invalid file path.")

    return save_path


class UserDocumentIngestor:
    """Handles uploading, text extraction, and storage for user-specific documents."""

    def __init__(self) -> None:
        from app.ingestion.chunker import DocumentChunker
        from app.ingestion.loader import DocumentLoader

        self.settings = get_settings()
        self.loader = DocumentLoader()
        self.chunker = DocumentChunker(
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP,
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

    def ingest_file(
        self, content: bytes, filename: str, session_id: str, owner_id: str
    ) -> dict:
        """
        Accept file content, extract text, chunk, and store in a session-specific collection.
        """
        from app.ingestion.embedder import VectorStoreManager

        # 1. Save file temporarily
        session_dir = (self.upload_dir / session_id).resolve()
        session_dir.mkdir(parents=True, exist_ok=True)
        file_path = sanitize_upload(filename, session_dir)
        display_name = Path(filename).name

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
            file_path.unlink(missing_ok=True)
            return {"success": False, "error": f"Unsupported file type: {suffix}"}

        if not text.strip():
            file_path.unlink(missing_ok=True)
            return {"success": False, "error": "No text content found in file"}

        # 3. Create document object for chunker
        doc = {
            "content": text,
            "metadata": {
                "source": display_name,
                "domain": "user_upload",
                "file_path": str(file_path),
                "stored_filename": file_path.name,
                "session_id": session_id,
                "owner_id": owner_id,
                "uploaded_at": datetime.now().isoformat(),
                "origin": "user",
            },
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
            collection_name=collection_name,
        )
        stored_count = vsm.embed_and_store(chunks)

        logger.info(
            "Ingested user file '%s' into collection '%s' (%d chunks).",
            display_name,
            collection_name,
            stored_count,
        )

        return {
            "success": True,
            "filename": display_name,
            "chunks_created": stored_count,
            "session_id": session_id,
        }
