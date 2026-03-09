"""
Security tests for user upload ingestion path handling.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import app.ingestion.user_ingestor as user_ingestor_module
from app.ingestion.user_ingestor import UserDocumentIngestor, sanitize_upload


def test_sanitize_upload_strips_path_components(tmp_path: Path) -> None:
    storage_dir = tmp_path / "session"
    storage_dir.mkdir(parents=True, exist_ok=True)

    safe_path = sanitize_upload("../../../etc/passwd.txt", storage_dir)

    assert safe_path.is_relative_to(storage_dir.resolve())
    assert safe_path.name.endswith("_passwd.txt")
    assert ".." not in safe_path.name


def test_sanitize_upload_rejects_invalid_name(tmp_path: Path) -> None:
    storage_dir = tmp_path / "session"
    storage_dir.mkdir(parents=True, exist_ok=True)

    with pytest.raises(ValueError):
        sanitize_upload("..", storage_dir)


def test_ingest_file_uses_sanitized_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    ingestor = UserDocumentIngestor()
    ingestor.upload_dir = tmp_path

    captured: dict = {}

    def fake_load_txt(file_path: str) -> str:
        captured["loaded_file_path"] = file_path
        return "Sample user text for chunking."

    def fake_chunk_document(doc: dict) -> list[dict]:
        captured["doc"] = doc
        return [{"content": "chunk", "metadata": {"chunk_id": "chunk_1"}}]

    class DummyVectorStoreManager:
        def __init__(self, *args, **kwargs):
            pass

        def embed_and_store(self, chunks: list[dict]) -> int:
            return len(chunks)

    monkeypatch.setattr(ingestor.loader, "load_txt", fake_load_txt)
    monkeypatch.setattr(ingestor.chunker, "chunk_document", fake_chunk_document)
    monkeypatch.setattr(
        user_ingestor_module, "VectorStoreManager", DummyVectorStoreManager
    )

    result = ingestor.ingest_file(
        b"hello", "../../../evil.txt", "session-1", owner_id="test-user"
    )

    assert result["success"] is True
    assert result["filename"] == "evil.txt"

    session_dir = (tmp_path / "session-1").resolve()
    saved_files = list(session_dir.iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].is_relative_to(session_dir)
    assert saved_files[0].name.endswith("_evil.txt")

    metadata = captured["doc"]["metadata"]
    assert metadata["source"] == "evil.txt"
    assert Path(metadata["file_path"]).resolve().is_relative_to(session_dir)


def test_ingest_file_removes_unsupported_upload(tmp_path: Path) -> None:
    ingestor = UserDocumentIngestor()
    ingestor.upload_dir = tmp_path

    result = ingestor.ingest_file(
        b"binary", "payload.exe", "session-2", owner_id="test-user"
    )

    assert result["success"] is False
    assert "Unsupported file type" in result["error"]
    session_dir = (tmp_path / "session-2").resolve()
    assert session_dir.exists()
    assert list(session_dir.iterdir()) == []
