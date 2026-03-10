import hashlib
import os
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.security import require_api_key


def _make_request(headers: dict[str, str]):
    return SimpleNamespace(headers=headers)


def test_require_api_key_accepts_plain_key(monkeypatch):
    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setattr(
        "app.api.security.settings",
        SimpleNamespace(
            API_AUTH_ENABLED=True,
            API_KEYS="k1:aaaaaaaaaaaaaaaaaaaaaaaa",
            API_KEYS_HASHED="",
            API_KEY_MIN_LENGTH=24,
            API_REQUIRE_KEY_ID=True,
            API_KEY_HEADER_NAME="x-api-key",
            API_KEY_ID_HEADER_NAME="x-api-key-id",
            REJECT_DEFAULT_API_KEYS=True,
        ),
    )
    require_api_key(
        _make_request(
            {"x-api-key": "aaaaaaaaaaaaaaaaaaaaaaaa", "x-api-key-id": "k1"}
        )
    )


def test_require_api_key_accepts_hashed_key(monkeypatch):
    monkeypatch.setenv("TESTING", "false")
    raw = "bbbbbbbbbbbbbbbbbbbbbbbb"
    hashed = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    monkeypatch.setattr(
        "app.api.security.settings",
        SimpleNamespace(
            API_AUTH_ENABLED=True,
            API_KEYS="",
            API_KEYS_HASHED=f"k2:{hashed}",
            API_KEY_MIN_LENGTH=24,
            API_REQUIRE_KEY_ID=True,
            API_KEY_HEADER_NAME="x-api-key",
            API_KEY_ID_HEADER_NAME="x-api-key-id",
            REJECT_DEFAULT_API_KEYS=True,
        ),
    )
    require_api_key(_make_request({"x-api-key": raw, "x-api-key-id": "k2"}))


def test_require_api_key_rejects_placeholder(monkeypatch):
    monkeypatch.setenv("TESTING", "false")
    monkeypatch.setattr(
        "app.api.security.settings",
        SimpleNamespace(
            API_AUTH_ENABLED=True,
            API_KEYS="replace_with_strong_key_1",  # gitleaks:allow
            API_KEYS_HASHED="",
            API_KEY_MIN_LENGTH=24,
            API_REQUIRE_KEY_ID=False,
            API_KEY_HEADER_NAME="x-api-key",
            API_KEY_ID_HEADER_NAME="x-api-key-id",
            REJECT_DEFAULT_API_KEYS=True,
        ),
    )
    with pytest.raises(HTTPException) as exc:
        require_api_key(_make_request({"x-api-key": "cccccccccccccccccccccccc"}))
    assert exc.value.status_code == 503


@pytest.fixture(autouse=True)
def _cleanup_testing_env():
    yield
    os.environ["TESTING"] = "true"
