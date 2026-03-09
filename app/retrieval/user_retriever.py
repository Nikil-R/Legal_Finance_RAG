"""
User Document Retriever — retrieves chunks from session-isolated collections.
"""

import chromadb

from app.config import get_settings
from app.retrieval.bm25_search import BM25Retriever
from app.retrieval.vector_search import VectorRetriever
from app.utils.logger import get_logger
from app.utils.session_ownership import verify_session_ownership

logger = get_logger(__name__)


class UserDocumentRetriever:
    """Retrieves chunks from a user's isolated collection."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.persist_dir = self.settings.CHROMA_PERSIST_DIR
        self.embedding_model = self.settings.EMBEDDING_MODEL

    def _collection_exists(self, collection_name: str) -> bool:
        """Check if a session-specific collection exists."""
        client = chromadb.PersistentClient(path=self.persist_dir)
        try:
            client.get_collection(name=collection_name)
            return True
        except Exception:
            return False

    def search(
        self, query: str, session_id: str, owner_id: str | None, top_k: int = 10
    ) -> list[dict]:
        """
        Embed query and search user collection.
        Returns empty list if collection doesn't exist.
        """
        collection_name = f"user_docs_{session_id}"

        if not owner_id:
            logger.warning(
                "Missing owner_id for session '%s'; denying user retrieval.", session_id
            )
            return []

        if not self._collection_exists(collection_name):
            logger.debug(
                "Session collection '%s' not found; skipping user search.",
                collection_name,
            )
            return []

        if not verify_session_ownership(
            session_id=session_id, owner_id=owner_id, persist_dir=self.persist_dir
        ):
            logger.warning(
                "Ownership check failed for session '%s'; skipping user retrieval.",
                session_id,
            )
            return []

        # Vector Search
        vector_retriever = VectorRetriever(
            persist_dir=self.persist_dir,
            embedding_model=self.embedding_model,
            collection_name=collection_name,
        )
        vector_results = vector_retriever.search(query, top_k=top_k)

        # BM25 Search
        bm25_retriever = BM25Retriever(
            persist_dir=self.persist_dir, collection_name=collection_name
        )
        bm25_results = bm25_retriever.search(query, top_k=top_k)

        # Mark results as origin="user"
        for result in vector_results:
            result["origin"] = "user"
        for result in bm25_results:
            result["origin"] = "user"

        return vector_results + bm25_results
