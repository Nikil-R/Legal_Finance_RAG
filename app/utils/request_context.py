"""
Request/trace context propagation for logs and responses.
"""

from __future__ import annotations

from contextvars import ContextVar

_request_id: ContextVar[str] = ContextVar("request_id", default="-")
_trace_id: ContextVar[str] = ContextVar("trace_id", default="-")


def set_request_context(request_id: str, trace_id: str) -> tuple:
    req_token = _request_id.set(request_id)
    trace_token = _trace_id.set(trace_id)
    return req_token, trace_token


def reset_request_context(tokens: tuple) -> None:
    req_token, trace_token = tokens
    _request_id.reset(req_token)
    _trace_id.reset(trace_token)


def get_request_id() -> str:
    return _request_id.get()


def get_trace_id() -> str:
    return _trace_id.get()
