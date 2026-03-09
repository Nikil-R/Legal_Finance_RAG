"""
User Document API Routes — handles uploading, listing, and deleting user-specific documents.
"""

import shutil
import uuid
from pathlib import Path
from typing import Optional

import chromadb
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile

from app.api.models import (
    UserDocumentInfo,
    UserDocumentsResponse,
    UserUploadJobStatusResponse,
    UserUploadResponse,
)
from app.api.security import AuthenticatedUser, get_current_user
from app.config import get_settings
from app.infra.ingestion_jobs import ingestion_job_store
from app.ingestion.async_jobs import enqueue_ingestion_job
from app.ingestion.user_ingestor import sanitize_upload
from app.utils.logger import get_logger
from app.utils.session_ownership import verify_session_ownership

logger = get_logger(__name__)
router = APIRouter(prefix="/user", tags=["User Documents"])
UPLOAD_READ_CHUNK_SIZE = 8192


async def read_upload_safely(file: UploadFile, max_upload_size: int) -> bytes:
    """Read upload stream in bounded chunks to cap memory usage per request."""
    chunks: list[bytes] = []
    total_size = 0

    while chunk := await file.read(UPLOAD_READ_CHUNK_SIZE):
        total_size += len(chunk)
        if total_size > max_upload_size:
            raise HTTPException(status_code=413, detail="File too large")
        chunks.append(chunk)

    return b"".join(chunks)


def _stage_user_upload(content: bytes, filename: str, session_id: str) -> Path:
    staging_dir = (Path("data/user_upload_jobs") / session_id).resolve()
    staging_dir.mkdir(parents=True, exist_ok=True)
    staged_path = sanitize_upload(filename, staging_dir)
    staged_path.write_bytes(content)
    return staged_path


@router.post("/upload", response_model=UserUploadResponse, status_code=202)
async def upload_user_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Query(None),
    user: AuthenticatedUser = Depends(get_current_user),
):
    """
    Upload a personal document (PDF, TXT, DOCX) to a session-isolated collection.
    If session_id is not provided, it will be generated.
    """
    settings = get_settings()
    if not session_id:
        session_id = str(uuid.uuid4())
    else:
        if not verify_session_ownership(
            session_id=session_id,
            owner_id=user.id,
            persist_dir=settings.CHROMA_PERSIST_DIR,
        ):
            raise HTTPException(
                status_code=403, detail="Session does not belong to current user."
            )

    # Check file type
    filename = file.filename or ""
    if not filename.strip():
        raise HTTPException(status_code=400, detail="Filename is required.")
    if not any(filename.lower().endswith(ext) for ext in [".pdf", ".txt", ".docx"]):
        raise HTTPException(
            status_code=400, detail="Unsupported file format. Use PDF, TXT, or DOCX."
        )

    try:
        content = await read_upload_safely(
            file=file, max_upload_size=settings.USER_UPLOAD_MAX_BYTES
        )
        staged_path = _stage_user_upload(
            content=content,
            filename=filename,
            session_id=session_id,
        )
        try:
            result = enqueue_ingestion_job(
                staged_file_path=str(staged_path),
                filename=Path(filename).name,
                session_id=session_id,
                owner_id=user.id,
            )
        except Exception:
            staged_path.unlink(missing_ok=True)
            raise

        return UserUploadResponse(
            success=True,
            session_id=session_id,
            filename=Path(filename).name,
            status=result.get("status", "queued"),
            job_id=result.get("job_id"),
            chunks_created=result.get("chunks_created"),
            backend=result.get("backend"),
            message="Upload accepted. Poll job status endpoint for completion.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error uploading user document: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to upload document.") from e


@router.get("/upload/jobs/{job_id}", response_model=UserUploadJobStatusResponse)
async def get_upload_job_status(
    job_id: str, user: AuthenticatedUser = Depends(get_current_user)
) -> UserUploadJobStatusResponse:
    record = ingestion_job_store.get_job(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Upload job not found.")
    if record.get("owner_id") != user.id:
        raise HTTPException(status_code=403, detail="Upload job does not belong to user.")

    return UserUploadJobStatusResponse(
        success=True,
        job_id=record["job_id"],
        session_id=record["session_id"],
        filename=record["filename"],
        status=record["status"],
        chunks_created=int(record.get("chunks_created", 0)),
        backend=record.get("backend"),
        error=record.get("error"),
        created_at=record.get("created_at"),
        updated_at=record.get("updated_at"),
    )


@router.get("/documents", response_model=UserDocumentsResponse)
async def list_user_documents(
    session_id: str, user: AuthenticatedUser = Depends(get_current_user)
):
    """
    List all uploaded documents for a specific session.
    """
    settings = get_settings()
    if not verify_session_ownership(
        session_id=session_id,
        owner_id=user.id,
        persist_dir=settings.CHROMA_PERSIST_DIR,
    ):
        raise HTTPException(
            status_code=403, detail="Session does not belong to current user."
        )
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
                    "chunks": 0,
                }
            docs_map[source]["chunks"] += 1

        return UserDocumentsResponse(
            success=True,
            session_id=session_id,
            documents=[UserDocumentInfo(**d) for d in docs_map.values()],
        )
    except Exception:
        # Collection not found or empty
        return UserDocumentsResponse(success=True, session_id=session_id, documents=[])


@router.delete("/documents/{session_id}")
async def clear_user_documents(
    session_id: str, user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Deletes all uploaded documents and the associated collection for a session.
    """
    settings = get_settings()
    if not verify_session_ownership(
        session_id=session_id,
        owner_id=user.id,
        persist_dir=settings.CHROMA_PERSIST_DIR,
    ):
        raise HTTPException(
            status_code=403, detail="Session does not belong to current user."
        )
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
    staging_dir = Path("data/user_upload_jobs") / session_id
    if staging_dir.exists():
        shutil.rmtree(staging_dir)

    return {"success": True, "message": f"Session {session_id} data cleared."}
