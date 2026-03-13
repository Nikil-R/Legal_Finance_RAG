"""
Streaming query endpoint — Server-Sent Events (SSE).
GET /api/v2/stream?question=...&domain=...&session_id=...
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_rag_pipeline
from app.api.security import AuthenticatedUser, require_role
from app.config import settings
from app.models.auth import Role
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Streaming"])


def _sse_event(data: Dict[str, Any], event: str = "message") -> str:
    """Format a dict as an SSE event string."""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"


async def _stream_rag_response(
    question: str,
    domain: str,
    session_id: str | None,
    owner_id: str,
    pipeline: Any,
) -> AsyncGenerator[str, None]:
    """
    Core streaming generator.

    Strategy:
      1. Emit `status` events during retrieval.
      2. Run full pipeline in threadpool (FastAPI/Groq don't support token streaming).
      3. Simulate token-level streaming by yielding the answer word-by-word.
      4. Emit `sources` and `done` events at the end.
    """
    start = time.perf_counter()

    # --- Phase 1: status ping ---
    yield _sse_event({"status": "Searching knowledge base…"}, event="status")
    await asyncio.sleep(0)   # give event loop a tick

    try:
        # --- Phase 2: run pipeline in background thread ---
        loop = asyncio.get_event_loop()
        result: Dict[str, Any] = await loop.run_in_executor(
            None,
            lambda: pipeline.run(
                question=question,
                domain=domain,
                session_id=session_id,
                owner_id=owner_id,
            ),
        )

        if not result.get("success"):
            yield _sse_event(
                {"error": result.get("error", "Unknown error")}, event="error"
            )
            return

        answer: str = result.get("answer", "")
        sources = result.get("sources", [])
        meta = result.get("metadata", {})

        yield _sse_event({"status": "Generating answer…"}, event="status")
        await asyncio.sleep(0)

        # --- Phase 3: stream the answer word-by-word ---
        words = answer.split(" ")
        chunk_size = 3   # emit N words at a time for a smooth feel
        buffer: list[str] = []

        for i, word in enumerate(words):
            buffer.append(word)
            if len(buffer) >= chunk_size or i == len(words) - 1:
                token = " ".join(buffer)
                if i < len(words) - 1:
                    token += " "
                yield _sse_event({"token": token}, event="token")
                buffer = []
                await asyncio.sleep(0.015)   # ~15 ms delay → natural cadence

        # --- Phase 4: send metadata ---
        total_ms = (time.perf_counter() - start) * 1000

        # Normalise sources to JSON-safe dicts
        safe_sources = []
        for src in sources:
            if hasattr(src, "model_dump"):
                safe_sources.append(src.model_dump())
            elif isinstance(src, dict):
                safe_sources.append(src)

        yield _sse_event(
            {
                "sources": safe_sources,
                "metadata": {
                    "total_time_ms": round(float(total_ms), 1),
                    "model": meta.get("model", "unknown"),
                    "cache_hit": meta.get("cache_hit", False),
                },
                "disclaimer": result.get("disclaimer", ""),
            },
            event="sources",
        )

        yield _sse_event({"done": True, "total_time_ms": round(float(total_ms), 1)}, event="done")

    except asyncio.CancelledError:
        logger.info("Streaming cancelled by client")
        yield _sse_event({"error": "Stream cancelled"}, event="error")
    except Exception as exc:
        logger.error("Streaming error: %s", exc, exc_info=True)
        yield _sse_event({"error": str(exc)}, event="error")


@router.get("")
async def stream_query(
    request: Request,
    question: str = Query(..., description="The question to ask"),
    domain: str = Query("all", description="Domain: tax, legal, finance, or all"),
    session_id: str | None = Query(None, description="Optional session ID"),
    user: AuthenticatedUser = Depends(
        require_role(Role.QUERY, Role.INGEST, Role.ADMIN)
    ),
    pipeline: Any = Depends(get_rag_pipeline),
) -> StreamingResponse:
    """
    Server-Sent Events streaming endpoint.

    Event types emitted (in order):
      status  — processing phase updates
      token   — answer token chunks (word-by-word)
      sources — citation sources + metadata
      done    — stream complete signal
      error   — error if something went wrong
    """
    logger.info(
        "stream_query | user=%s | domain=%s | q=%.50s",
        user.id,
        domain,
        str(question),
    )

    return StreamingResponse(
        _stream_rag_response(
            question=question,
            domain=domain,
            session_id=session_id,
            owner_id=user.id,
            pipeline=pipeline,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable Nginx buffering
            "Connection": "keep-alive",
        },
    )
