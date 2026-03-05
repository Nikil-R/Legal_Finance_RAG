"""
API security dependencies.
"""

from __future__ import annotations

import hashlib
import hmac
import os

from fastapi import HTTPException, Request

from app.config import settings


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


def require_api_key(request: Request) -> None:
    if os.getenv("TESTING", "").lower() == "true":
        return

    if not settings.API_AUTH_ENABLED:
        return

    provided_key = request.headers.get(settings.API_KEY_HEADER_NAME.lower())
    provided_key_id = request.headers.get(settings.API_KEY_ID_HEADER_NAME.lower(), "")
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
        return

    provided_hash = hashlib.sha256(provided_key.encode("utf-8")).hexdigest()
    if any(hmac.compare_digest(provided_hash, ref) for ref in candidate_hashes):
        return

    raise HTTPException(status_code=401, detail="Invalid or missing API key.")
