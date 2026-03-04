"""
User Document API Routes — handles uploading, listing, and deleting user-specific documents.
"""
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, Depends
from typing import Optional
import uuid
import shutil
from pathlib import Path
import chromadb

from app.api.models import UserUploadResponse, UserDocumentsResponse, UserDocumentInfo
from app.ingestion.user_ingestor import UserDocumentIngestor
from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/user", tags=["User Documents"])

@router.post("/upload", response_model=UserUploadResponse)
async def upload_user_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Query(None)
):
    """
    Upload a personal document (PDF, TXT, DOCX) to a session-isolated collection.
    If session_id is not provided, it will be generated.
    """
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Check file type
    filename = file.filename
    if not any(filename.lower().endswith(ext) for ext in [".pdf", ".txt", ".docx"]):
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF, TXT, or DOCX.")

    try:
        content = await file.read()
        ingestor = UserDocumentIngestor()
        result = ingestor.ingest_file(content, filename, session_id)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Ingestion failed"))
            
        return UserUploadResponse(
            success=True,
            session_id=session_id,
            filename=filename,
            chunks_created=result["chunks_created"]
        )
    except Exception as e:
        logger.error("Error uploading user document: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=UserDocumentsResponse)
async def list_user_documents(session_id: str):
    """
    List all uploaded documents for a specific session.
    """
    settings = get_settings()
    collection_name = f"user_docs_{session_id}"
    
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    try:
        collection = client.get_collection(name=collection_name)
        # Fetch metadata for distinct documents
        # ChromaDB doesn't have a direct 'distinct' query, so we'll fetch metadatas
        # and extract distinct sources/dates manually.
        raw = collection.get(include=["metadatas"])
        metadatas = raw["metadatas"]
        
        docs_map = {}
        for m in metadatas:
            source = m.get("source")
            if source not in docs_map:
                docs_map[source] = {
                    "filename": source,
                    "uploaded_at": m.get("uploaded_at"),
                    "chunks": 0
                }
            docs_map[source]["chunks"] += 1
            
        return UserDocumentsResponse(
            success=True,
            session_id=session_id,
            documents=[UserDocumentInfo(**d) for d in docs_map.values()]
        )
    except Exception:
        # Collection not found or empty
        return UserDocumentsResponse(success=True, session_id=session_id, documents=[])

@router.delete("/documents/{session_id}")
async def clear_user_documents(session_id: str):
    """
    Deletes all uploaded documents and the associated collection for a session.
    """
    settings = get_settings()
    collection_name = f"user_docs_{session_id}"
    
    # 1. Clear ChromaDB
    client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    try:
        client.delete_collection(name=collection_name)
    except Exception as e:
        logger.warning("Could not delete collection %s: %s", collection_name, str(e))
        
    # 2. Delete temporary files
    session_dir = Path("data/user_uploads") / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)
        
    return {"success": True, "message": f"Session {session_id} data cleared."}
