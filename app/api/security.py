"""
API security dependencies.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

from fastapi import HTTPException, Request

from app.config import settings


@dataclass(frozen=True)
class AuthenticatedUser:
    """Authenticated principal resolved from API key headers."""

    id: str
    key_id: str | None = None
    auth_method: str = "api_key"


def _parse_key_records(raw: str) -> dict[str, str]:
    records: dict[str, str] = {}
    for idx, item in enumerate([v.strip() for v in raw.split(",") if v.strip()]):
        if ":" in item:
            key_id, value = item.split(":", 1)
            records[key_id.strip()] = value.strip()
        else:
            records[f"__idx_{idx}"] = item
    return records


def _contains_default_placeholder(values: dict[str, str]) -> bool:
    return any("replace_with_strong_key" in v.lower() for v in values.values())


def _cache_user(request: Request, user: AuthenticatedUser) -> None:
    state = getattr(request, "state", None)
    if state is not None:
        state.authenticated_user = user


def _cached_user(request: Request) -> AuthenticatedUser | None:
    state = getattr(request, "state", None)
    if state is None:
        return None
    return getattr(state, "authenticated_user", None)


def _resolve_user_id(provided_key: str, provided_key_id: str) -> str:
    if provided_key_id:
        return f"key_id:{provided_key_id}"
    provided_hash = hashlib.sha256(provided_key.encode("utf-8")).hexdigest()
    return f"key_hash:{provided_hash}"


def _authenticate_request(request: Request) -> AuthenticatedUser:
    cached = _cached_user(request)
    if cached is not None:
        return cached

    if settings.TESTING and settings.ENVIRONMENT != "production":
        test_user_id = request.headers.get("x-test-user-id", "test-user")
        user = AuthenticatedUser(id=test_user_id, key_id="test", auth_method="testing")
        _cache_user(request, user)
        return user

    if not settings.API_AUTH_ENABLED:
        user = AuthenticatedUser(id="anonymous", auth_method="auth_disabled")
        _cache_user(request, user)
        return user

    provided_key = request.headers.get(settings.API_KEY_HEADER_NAME.lower())
    provided_key_id = request.headers.get(settings.API_KEY_ID_HEADER_NAME.lower(), "").strip()
    if not provided_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    if len(provided_key) < settings.API_KEY_MIN_LENGTH:
        raise HTTPException(status_code=401, detail="Invalid API key length.")

    allowed_plain = _parse_key_records(settings.API_KEYS)
    allowed_hashed = _parse_key_records(settings.API_KEYS_HASHED)
    if settings.REJECT_DEFAULT_API_KEYS and _contains_default_placeholder(allowed_plain):
        raise HTTPException(
            status_code=503,
            detail="API keys are set to placeholders; configure production keys.",
        )
    if not allowed_plain and not allowed_hashed:
        raise HTTPException(
            status_code=503,
            detail="API auth is enabled but no API keys are configured.",
        )

    if settings.API_REQUIRE_KEY_ID and not provided_key_id:
        raise HTTPException(status_code=401, detail="Missing API key id header.")

    candidate_plain: list[str] = []
    candidate_hashes: list[str] = []
    if provided_key_id:
        if provided_key_id in allowed_plain:
            candidate_plain.append(allowed_plain[provided_key_id])
        if provided_key_id in allowed_hashed:
            candidate_hashes.append(allowed_hashed[provided_key_id])
    else:
        candidate_plain.extend(allowed_plain.values())
        candidate_hashes.extend(allowed_hashed.values())

    if any(hmac.compare_digest(provided_key, ref) for ref in candidate_plain):
        user = AuthenticatedUser(
            id=_resolve_user_id(provided_key, provided_key_id),
            key_id=provided_key_id or None,
            auth_method="api_key",
        )
        _cache_user(request, user)
        return user

    provided_hash = hashlib.sha256(provided_key.encode("utf-8")).hexdigest()
    if any(hmac.compare_digest(provided_hash, ref) for ref in candidate_hashes):
        user = AuthenticatedUser(
            id=_resolve_user_id(provided_key, provided_key_id),
            key_id=provided_key_id or None,
            auth_method="api_key",
        )
        _cache_user(request, user)
        return user

    raise HTTPException(status_code=401, detail="Invalid or missing API key.")


def require_api_key(request: Request) -> None:
    _authenticate_request(request)


def get_current_user(request: Request) -> AuthenticatedUser:
    return _authenticate_request(request)
