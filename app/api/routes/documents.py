"""
Document management endpoints.
"""

import time
from datetime import datetime, timezone

from fastapi import APIRouter

from app.api.dependencies import clear_pipeline_cache, get_retriever
from app.api.models import IngestRequest, IngestResponse, StatsResponse
from app.ingestion.pipeline import run_ingestion_pipeline
from app.utils.logger import get_logger

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = get_logger(__name__)

# Track last ingestion time
_last_ingestion: datetime | None = None


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

        return StatsResponse(
            total_documents=stats.get("total_documents", 0),
            total_chunks=stats.get("total_chunks", 0),
            domains=stats.get("domains", {}),
            index_status="ready" if stats.get("total_chunks", 0) > 0 else "empty",
            last_ingestion=_last_ingestion,
        )

    except Exception as e:
        logger.error("Stats error: %s", str(e))
        return StatsResponse(
            total_documents=0,
            total_chunks=0,
            domains={},
            index_status="error",
            last_ingestion=None,
        )


@router.post(
    "/ingest",
    response_model=IngestResponse,
    summary="Trigger document ingestion",
    description="""
    Triggers the document ingestion pipeline.
    
    This will:
    1. Load all documents from data/raw/ subfolders
    2. Chunk the documents
    3. Generate embeddings
    4. Store in ChromaDB
    
    Use clear_existing=true to remove old documents first.
    
    Note: This is a synchronous operation and may take a while for large document sets.
    """,
)
async def ingest_documents(request: IngestRequest) -> IngestResponse:
    """
    Trigger document ingestion.
    """
    global _last_ingestion

    logger.info("Ingestion triggered | clear_existing: %s", request.clear_existing)

    try:
        start = time.time()

        # Run ingestion
        result = run_ingestion_pipeline(clear_existing=request.clear_existing)

        elapsed = time.time() - start
        _last_ingestion = datetime.now(timezone.utc)

        # Clear cached pipelines so they pick up new documents
        clear_pipeline_cache()

        logger.info(
            "Ingestion complete | Chunks: %d | Time: %.2fs",
            result["chunks_stored"],
            elapsed,
        )

        return IngestResponse(
            success=True,
            documents_loaded=result.get("documents_loaded", 0),
            chunks_created=result.get("chunks_created", 0),
            chunks_stored=result.get("chunks_stored", 0),
            domains=result.get("domains", {}),
            time_taken_seconds=elapsed,
        )

    except Exception as e:
        logger.error("Ingestion error: %s", str(e), exc_info=True)
        return IngestResponse(
            success=False,
            documents_loaded=0,
            chunks_created=0,
            chunks_stored=0,
            domains={},
            time_taken_seconds=0,
            error=str(e),
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
