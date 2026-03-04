"""
Test script for Multi-Source RAG - verifying isolated collections.
"""

import chromadb

from app.ingestion.embedder import VectorStoreManager


def test_isolation(tmp_path):
    """Verify that user collections are isolated and don't leak data."""
    persist_dir = str(tmp_path / "chroma_iso_test")

    # 1. Create System Collection
    vsm_system = VectorStoreManager(
        persist_dir=persist_dir,
        embedding_model="all-MiniLM-L6-v2",
        collection_name="legal_finance_docs",
    )
    vsm_system.embed_and_store(
        [
            {
                "content": "This is a system document about GST rules in India.",
                "metadata": {
                    "chunk_id": "sys_1",
                    "source": "gst_rules.pdf",
                    "domain": "tax",
                    "origin": "system",
                },
            }
        ]
    )

    # 2. Create User Collection for Session A
    vsm_user_a = VectorStoreManager(
        persist_dir=persist_dir,
        embedding_model="all-MiniLM-L6-v2",
        collection_name="user_docs_session_A",
    )
    vsm_user_a.embed_and_store(
        [
            {
                "content": "My private contract says I get 10% commission.",
                "metadata": {
                    "chunk_id": "user_a_1",
                    "source": "my_contract.pdf",
                    "domain": "user_upload",
                    "origin": "user",
                },
            }
        ]
    )

    # 3. Create User Collection for Session B
    vsm_user_b = VectorStoreManager(
        persist_dir=persist_dir,
        embedding_model="all-MiniLM-L6-v2",
        collection_name="user_docs_session_B",
    )
    vsm_user_b.embed_and_store(
        [
            {
                "content": "Our balance sheet shows a profit of 50 Lakhs.",
                "metadata": {
                    "chunk_id": "user_b_1",
                    "source": "balance_sheet.txt",
                    "domain": "user_upload",
                    "origin": "user",
                },
            }
        ]
    )

    # 4. Verify isolation via ChromaDB
    # We use a NEW client instance to check what's on disk
    client = chromadb.PersistentClient(path=persist_dir)
    col_names = [c.name for c in client.list_collections()]

    # Verify all exist
    for col_name in [
        "legal_finance_docs",
        "user_docs_session_A",
        "user_docs_session_B",
    ]:
        assert col_name in col_names, f"Missing collection: {col_name}"
        col = client.get_collection(col_name)
        assert col.count() > 0, f"Collection '{col_name}' is empty!"

    # 5. Verify Session A cannot see Session B's data
    col_a = client.get_collection("user_docs_session_A")
    col_b = client.get_collection("user_docs_session_B")
    
    a_docs = col_a.get()["documents"]
    b_docs = col_b.get()["documents"]
    
    assert all(
        "balance sheet" not in d for d in a_docs
    ), "Session A saw Session B's data!"
    assert all(
        "commission" not in d for d in b_docs
    ), "Session B saw Session A's data!"
