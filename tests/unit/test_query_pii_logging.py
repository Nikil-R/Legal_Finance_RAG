from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from starlette.requests import Request

from app.api.models import QueryRequest, RetrievalOnlyRequest
from app.api.routes import query as query_routes
from app.api.security import AuthenticatedUser


class _DummyRagPipeline:
    def run(self, **kwargs):
        return {
            "success": True,
            "answer": "ok",
            "sources": [],
            "validation": {},
            "metadata": {},
        }


class _DummyRetrievalPipeline:
    def run(self, **kwargs):
        return {
            "success": True,
            "sources": [],
            "candidates_found": 0,
            "total_time_ms": 0,
        }


def _make_request(path: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": path,
            "headers": [],
            "client": ("testclient", 1234),
            "scheme": "http",
            "server": ("testserver", 80),
        }
    )


@pytest.mark.asyncio
async def test_query_logs_redacted_question(monkeypatch: pytest.MonkeyPatch) -> None:
    query_request = QueryRequest(
        question="test@example.com 9876543210 details",
        domain="tax",
        include_sources=False,
    )
    info_mock = MagicMock()

    monkeypatch.setattr(query_routes.settings, "PII_REDACTION_ENABLED", True)
    monkeypatch.setattr(query_routes.logger, "info", info_mock)

    await query_routes.query.__wrapped__(
        query_request=query_request,
        request=_make_request("/api/v1/query"),
        user=AuthenticatedUser(id="test-user"),
        pipeline=_DummyRagPipeline(),
    )

    first_call = info_mock.call_args_list[0]
    logged_preview = first_call.args[1]
    assert "test@example.com" not in logged_preview
    assert "9876543210" not in logged_preview
    assert "[REDACTED_EMAIL]" in logged_preview
    assert "[REDACTED_PHONE]" in logged_preview


@pytest.mark.asyncio
async def test_retrieval_logs_redacted_question(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retrieval_request = RetrievalOnlyRequest(
        question="Email jane@corp.com PAN ABCDE1234F for details",
        domain="legal",
        top_k=3,
    )
    info_mock = MagicMock()

    monkeypatch.setattr(query_routes.settings, "PII_REDACTION_ENABLED", True)
    monkeypatch.setattr(query_routes.logger, "info", info_mock)

    await query_routes.retrieve_only.__wrapped__(
        retrieval_request=retrieval_request,
        request=_make_request("/api/v1/query/retrieve"),
        user=AuthenticatedUser(id="test-user"),
        pipeline=_DummyRetrievalPipeline(),
    )

    first_call = info_mock.call_args_list[0]
    logged_preview = first_call.args[1]
    assert "jane@corp.com" not in logged_preview
    assert "ABCDE1234F" not in logged_preview
    assert "[REDACTED_EMAIL]" in logged_preview
    assert "[REDACTED_PAN]" in logged_preview
