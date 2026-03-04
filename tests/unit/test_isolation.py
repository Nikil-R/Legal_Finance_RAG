"""
Test script for Multi-Source RAG - verifying isolated collections.
"""
import gc
import os
import shutil
import chromadb
from app.ingestion.embedder import VectorStoreManager


def test_isolation():
    persist_dir = "temp_test_chroma"
    clients_to_close = []  # Track all chromadb objects for explicit cleanup

    def _force_remove(path):
        """Windows-safe directory removal — chmod before delete."""
        def _onerror(func, fpath, _):
            os.chmod(fpath, 0o777)
            func(fpath)
        if os.path.exists(path):
            shutil.rmtree(path, onerror=_onerror)

    _force_remove(persist_dir)
        
    try:
        # 1. Create System Collection
        vsm_system = VectorStoreManager(
            persist_dir=persist_dir,
            embedding_model="all-MiniLM-L6-v2",
            collection_name="legal_finance_docs",
        )
        vsm_system.embed_and_store([{
            "content": "This is a system document about GST rules in India.",
            "metadata": {"source": "gst_rules.pdf", "domain": "tax", "origin": "system"},
        }])
        
        # 2. Create User Collection for Session A
        vsm_user_a = VectorStoreManager(
            persist_dir=persist_dir,
            embedding_model="all-MiniLM-L6-v2",
            collection_name="user_docs_session_A",
        )
        vsm_user_a.embed_and_store([{
            "content": "My private contract says I get 10% commission.",
            "metadata": {"source": "my_contract.pdf", "domain": "user_upload", "origin": "user"},
        }])
        
        # 3. Create User Collection for Session B
        vsm_user_b = VectorStoreManager(
            persist_dir=persist_dir,
            embedding_model="all-MiniLM-L6-v2",
            collection_name="user_docs_session_B",
        )
        vsm_user_b.embed_and_store([{
            "content": "Our balance sheet shows a profit of 50 Lakhs.",
            "metadata": {"source": "balance_sheet.txt", "domain": "user_upload", "origin": "user"},
        }])
        
        # 4. Verify isolation via ChromaDB
        client = chromadb.PersistentClient(path=persist_dir)
        col_names = [c.name for c in client.list_collections()]
        print(f"\nCollections found: {col_names}")

        for col_name in ["legal_finance_docs", "user_docs_session_A", "user_docs_session_B"]:
            assert col_name in col_names, f"❌ Missing collection: {col_name}"
            col = client.get_collection(col_name)
            count = col.count()
            print(f"  '{col_name}' → {count} chunk(s)")
            assert count > 0, f"❌ Collection '{col_name}' is empty!"

        # 5. Verify Session A cannot see Session B's data
        col_a = client.get_collection("user_docs_session_A")
        col_b = client.get_collection("user_docs_session_B")
        a_docs = col_a.get()["documents"]
        b_docs = col_b.get()["documents"]
        assert all("balance sheet" not in d for d in a_docs), "❌ Session A saw Session B's data!"
        assert all("commission" not in d for d in b_docs), "❌ Session B saw Session A's data!"

        print("\n✅ All isolation checks passed!")

    finally:
        # Release all ChromaDB handles so Windows can delete the SQLite file
        vsm_system = vsm_user_a = vsm_user_b = client = None
        gc.collect()
        _force_remove(persist_dir)

if __name__ == "__main__":
    test_isolation()
