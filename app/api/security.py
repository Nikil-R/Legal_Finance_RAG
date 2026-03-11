"""
API security dependencies.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from functools import lru_cache

from fastapi import Depends, HTTPException, Request

from app.config import settings
from app.models.auth import Role


@dataclass(frozen=True)
class AuthenticatedUser:
    """Authenticated principal resolved from API key headers."""

    id: str
    role: Role = Role.QUERY
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


@lru_cache(maxsize=1)
def _parse_role_records(raw: str) -> dict[str, Role]:
    records: dict[str, Role] = {}
    for item in [v.strip() for v in (raw or "").split(",") if v.strip()]:
        if ":" not in item:
            continue
        key_id, role_name = item.split(":", 1)
        key = key_id.strip()
        value = role_name.strip().lower()
        if not key:
            continue
        try:
            records[key] = Role(value)
        except ValueError:
            # Ignore unknown roles rather than fail auth initialization.
            continue
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


def _resolve_user_role(key_id: str | None) -> Role:
    role_map = _parse_role_records(getattr(settings, "API_KEY_ROLES", ""))
    if key_id and key_id in role_map:
        return role_map[key_id]
    return Role.QUERY


def _match_plain_key(
    provided_key: str,
    provided_key_id: str,
    allowed_plain: dict[str, str],
) -> str | None:
    if provided_key_id:
        ref = allowed_plain.get(provided_key_id)
        if ref and hmac.compare_digest(provided_key, ref):
            return provided_key_id
        return None

    for key_id, ref in allowed_plain.items():
        if hmac.compare_digest(provided_key, ref):
            return key_id
    return None


def _match_hashed_key(
    provided_key: str,
    provided_key_id: str,
    allowed_hashed: dict[str, str],
) -> str | None:
    provided_hash = hashlib.sha256(provided_key.encode("utf-8")).hexdigest()
    if provided_key_id:
        ref = allowed_hashed.get(provided_key_id)
        if ref and hmac.compare_digest(provided_hash, ref):
            return provided_key_id
        return None

    for key_id, ref in allowed_hashed.items():
        if hmac.compare_digest(provided_hash, ref):
            return key_id
    return None


def _authenticate_request(request: Request) -> AuthenticatedUser:
    cached = _cached_user(request)
    if cached is not None:
        return cached

    testing = bool(getattr(settings, "TESTING", False))
    environment = str(getattr(settings, "ENVIRONMENT", "local"))
    if testing and environment != "production":
        test_user_id = request.headers.get("x-test-user-id", "test-user")
        user = AuthenticatedUser(
            id=test_user_id, role=Role.ADMIN, key_id="test", auth_method="testing"
        )
        _cache_user(request, user)
        return user

    if not bool(getattr(settings, "API_AUTH_ENABLED", True)):
        user = AuthenticatedUser(id="anonymous", role=Role.ADMIN, auth_method="auth_disabled")
        _cache_user(request, user)
        return user

    key_header = str(getattr(settings, "API_KEY_HEADER_NAME", "x-api-key")).lower()
    key_id_header = str(
        getattr(settings, "API_KEY_ID_HEADER_NAME", "x-api-key-id")
    ).lower()
    provided_key = request.headers.get(key_header)
    provided_key_id = request.headers.get(key_id_header, "").strip()
    if not provided_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key.")
    if len(provided_key) < int(getattr(settings, "API_KEY_MIN_LENGTH", 24)):
        raise HTTPException(status_code=401, detail="Invalid API key length.")

    allowed_plain = _parse_key_records(str(getattr(settings, "API_KEYS", "")))
    allowed_hashed = _parse_key_records(str(getattr(settings, "API_KEYS_HASHED", "")))
    if bool(getattr(settings, "REJECT_DEFAULT_API_KEYS", True)) and _contains_default_placeholder(
        allowed_plain
    ):
        raise HTTPException(
            status_code=503,
            detail="API keys are set to placeholders; configure production keys.",
        )
    if not allowed_plain and not allowed_hashed:
        raise HTTPException(
            status_code=503,
            detail="API auth is enabled but no API keys are configured.",
        )

    if bool(getattr(settings, "API_REQUIRE_KEY_ID", False)) and not provided_key_id:
        raise HTTPException(status_code=401, detail="Missing API key id header.")

    matched_plain_key_id = _match_plain_key(provided_key, provided_key_id, allowed_plain)
    if matched_plain_key_id is not None:
        user = AuthenticatedUser(
            id=_resolve_user_id(provided_key, provided_key_id),
            role=_resolve_user_role(matched_plain_key_id),
            key_id=provided_key_id or None,
            auth_method="api_key",
        )
        _cache_user(request, user)
        return user

    matched_hashed_key_id = _match_hashed_key(provided_key, provided_key_id, allowed_hashed)
    if matched_hashed_key_id is not None:
        user = AuthenticatedUser(
            id=_resolve_user_id(provided_key, provided_key_id),
            role=_resolve_user_role(matched_hashed_key_id),
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


def require_role(*allowed_roles: Role):
    """Dependency factory to enforce role-based access control."""

    def dependency(user: AuthenticatedUser = Depends(get_current_user)):
        if user.role == Role.ADMIN:
            return user
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden. Required roles: {[r.value for r in allowed_roles]}",
            )
        return user
    return dependency
