"""
Document management endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.api.rate_limit import limiter
from app.api.security_decorators import require_role
from app.models.auth import Role, User

from app.api.dependencies import clear_pipeline_cache, get_retriever
from app.api.models import (
    IngestJobResponse,
    IngestJobStatusResponse,
    IngestRequest,
    StatsResponse,
)
from app.infra.system_ingestion_jobs import system_ingestion_job_store
from app.ingestion.system_async_jobs import enqueue_system_ingestion_job
from app.observability import logger as obs_logger

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = obs_logger.bind(module="api.documents")


def _maybe_invalidate_cache_for_job(record: dict) -> dict:
    """
    Invalidate API pipeline caches once a Celery-backed ingestion job is complete.
    """
    if record.get("status") != "completed" or record.get("cache_invalidated"):
        return record

    clear_pipeline_cache()
    updated = system_ingestion_job_store.update_job(
        record["job_id"], cache_invalidated=True
    )
    if updated is not None:
        return updated

    # Fallback if persistence update fails.
    patched = dict(record)
    patched["cache_invalidated"] = True
    return patched


@router.get(
    "/stats",
    response_model=StatsResponse,
    summary="Get document statistics",
    description="Returns statistics about indexed documents including total counts and per-domain breakdown.",
)
async def get_stats() -> StatsResponse:
    """
    Get statistics about indexed documents.
    """
    try:
        retriever = get_retriever()
        stats = retriever.get_stats()
        last_ingestion = system_ingestion_job_store.get_last_completed_at()

        return StatsResponse(
            total_documents=stats.get("total_documents", 0),
            total_chunks=stats.get("total_chunks", 0),
            domains=stats.get("domains", {}),
            index_status="ready" if stats.get("total_chunks", 0) > 0 else "empty",
            last_ingestion=last_ingestion,
        )

    except Exception as e:
        logger.error("Stats error: %s", str(e))
        return StatsResponse(
            total_documents=0,
            total_chunks=0,
            domains={},
            index_status="error",
            last_ingestion=system_ingestion_job_store.get_last_completed_at(),
        )


@router.post(
    "/ingest",
    response_model=IngestJobResponse,
    status_code=202,
    summary="Trigger document ingestion",
    description="""
    Enqueue document ingestion in the background.
    
    The worker will:
    1. Load all documents from data/raw/ subfolders
    2. Chunk the documents
    3. Generate embeddings
    4. Store in ChromaDB
    
    Use clear_existing=true to remove old documents first.
    
    Poll /documents/ingest/jobs/{job_id} for completion status.
    """,
)
@limiter.limit("20/hour")
@require_role(Role.INGEST, Role.ADMIN)
async def ingest_documents(request: IngestRequest, user: User) -> IngestJobResponse:
    """
    Trigger document ingestion asynchronously.
    """
    logger.info(
        "System ingestion enqueue requested | clear_existing: %s", request.clear_existing
    )
    logger.debug("User %s triggered system ingestion request", user.email)

    try:
        result = enqueue_system_ingestion_job(clear_existing=request.clear_existing)
        return IngestJobResponse(
            success=True,
            job_id=result["job_id"],
            status=result.get("status", "queued"),
            clear_existing=bool(result.get("clear_existing", request.clear_existing)),
            backend=result.get("backend"),
            message="Ingestion accepted. Poll job status endpoint for completion.",
        )
    except Exception as e:
        logger.error("Failed to enqueue ingestion job: %s", str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to enqueue ingestion job.") from e


@router.get("/ingest/jobs/{job_id}", response_model=IngestJobStatusResponse)
@require_role(Role.QUERY, Role.INGEST, Role.ADMIN)
async def get_ingestion_job_status(job_id: str, user: User) -> IngestJobStatusResponse:
    """
    Get status of an asynchronous system-ingestion job.
    """
    logger.debug("Ingestion status requested by %s for job %s", user.email, job_id)
    record = system_ingestion_job_store.get_job(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Ingestion job not found.")

    record = _maybe_invalidate_cache_for_job(record)

    return IngestJobStatusResponse(
        success=True,
        job_id=record["job_id"],
        status=record["status"],
        clear_existing=bool(record.get("clear_existing", False)),
        backend=record.get("backend"),
        documents_loaded=int(record.get("documents_loaded", 0)),
        chunks_created=int(record.get("chunks_created", 0)),
        chunks_stored=int(record.get("chunks_stored", 0)),
        domains=record.get("domains", {}),
        time_taken_seconds=float(record.get("time_taken_seconds", 0.0)),
        cache_invalidated=bool(record.get("cache_invalidated", False)),
        error=record.get("error"),
        created_at=record.get("created_at"),
        updated_at=record.get("updated_at"),
    )


@router.get(
    "/domains",
    summary="List available domains",
    description="Returns list of available document domains.",
)
async def list_domains() -> dict:
    """
    List available domains.
    """
    return {
        "domains": [
            {
                "id": "tax",
                "name": "Tax Laws",
                "description": "Indian income tax, GST, and related tax legislation",
            },
            {
                "id": "finance",
                "name": "Financial Regulations",
                "description": "RBI guidelines, banking regulations, SEBI rules",
            },
            {
                "id": "legal",
                "name": "Legal Provisions",
                "description": "Contract Act, Companies Act, general legal provisions",
            },
            {
                "id": "all",
                "name": "All Domains",
                "description": "Search across all domains",
            },
        ]
    }
