"""
Unit tests for session ownership verification.
"""

from __future__ import annotations

import app.utils.session_ownership as ownership_module
from app.utils.session_ownership import verify_session_ownership


class _MissingCollectionClient:
    def __init__(self, path: str):
        self.path = path

    def get_collection(self, name: str):
        raise RuntimeError("missing")


class _Collection:
    def __init__(self, metadatas: list[dict]):
        self._metadatas = metadatas

    def get(self, include: list[str], limit: int = 32) -> dict:
        return {"metadatas": self._metadatas[:limit]}


class _ClientWithCollection:
    def __init__(self, path: str, metadatas: list[dict]):
        self.path = path
        self._metadatas = metadatas

    def get_collection(self, name: str):
        return _Collection(self._metadatas)


def test_verify_session_ownership_allows_missing_collection(monkeypatch):
    monkeypatch.setattr(
        ownership_module.chromadb, "PersistentClient", _MissingCollectionClient
    )
    assert verify_session_ownership("session-1", "user-1", "./test_db") is True


def test_verify_session_ownership_requires_owner_metadata(monkeypatch):
    def _factory(path: str):
        return _ClientWithCollection(path=path, metadatas=[{"session_id": "session-1"}])

    monkeypatch.setattr(ownership_module.chromadb, "PersistentClient", _factory)
    assert verify_session_ownership("session-1", "user-1", "./test_db") is False


def test_verify_session_ownership_blocks_owner_mismatch(monkeypatch):
    def _factory(path: str):
        return _ClientWithCollection(
            path=path, metadatas=[{"owner_id": "key_hash:abc123"}]
        )

    monkeypatch.setattr(ownership_module.chromadb, "PersistentClient", _factory)
    assert verify_session_ownership("session-1", "key_hash:zzz999", "./test_db") is False


def test_verify_session_ownership_allows_owner_match(monkeypatch):
    def _factory(path: str):
        return _ClientWithCollection(
            path=path, metadatas=[{"owner_id": "key_hash:abc123"}]
        )

    monkeypatch.setattr(ownership_module.chromadb, "PersistentClient", _factory)
    assert verify_session_ownership("session-1", "key_hash:abc123", "./test_db") is True
