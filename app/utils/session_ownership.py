"""
Session ownership checks for user-uploaded collections.
"""

from __future__ import annotations

import hmac

import chromadb

from app.utils.logger import get_logger

logger = get_logger(__name__)


def verify_session_ownership(session_id: str, owner_id: str, persist_dir: str) -> bool:
    """
    Verify that an existing user session collection belongs to ``owner_id``.

    Behavior:
    - Missing collection or empty collection: returns True (safe to create/use).
    - Existing collection without owner metadata: returns False.
    - Existing collection with mixed owners: returns False.
    - Existing collection with one owner: compares to ``owner_id``.
    """
    session = (session_id or "").strip()
    owner = (owner_id or "").strip()
    if not session or not owner:
        return False

    collection_name = f"user_docs_{session}"
    client = chromadb.PersistentClient(path=persist_dir)
    try:
        collection = client.get_collection(name=collection_name)
    except Exception:
        return True

    try:
        sample = collection.get(include=["metadatas"], limit=32)
    except Exception as exc:
        logger.warning(
            "Session ownership check failed for '%s': %s", collection_name, exc
        )
        return False

    metadatas = sample.get("metadatas", []) if sample else []
    if not metadatas:
        return True

    owners = {
        m.get("owner_id", "").strip()
        for m in metadatas
        if isinstance(m, dict) and m.get("owner_id")
    }

    if len(owners) != 1:
        logger.warning(
            "Session ownership invalid for '%s' (owners=%s)", collection_name, owners
        )
        return False

    stored_owner = next(iter(owners))
    return hmac.compare_digest(stored_owner, owner)
