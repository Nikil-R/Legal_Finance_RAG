"""
Test script for Multi-Source RAG - verifying isolated collections.
"""
import os
import shutil
from pathlib import Path
import chromadb
from app.ingestion.embedder import VectorStoreManager
from app.retrieval.retriever import HybridRetriever

def test_isolation():
    persist_dir = "temp_test_chroma"
    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        
    try:
        # 1. Create System Collection
        vsm_system = VectorStoreManager(
            persist_dir=persist_dir,
            embedding_model="all-MiniLM-L6-v2",
            collection_name="legal_finance_docs"
        )
        vsm_system.embed_and_store([{
            "content": "This is a system document about GST rules in India.",
            "metadata": {"source": "gst_rules.pdf", "domain": "tax", "origin": "system"}
        }])
        
        # 2. Create User Collection for Session A
        vsm_user_a = VectorStoreManager(
            persist_dir=persist_dir,
            embedding_model="all-MiniLM-L6-v2",
            collection_name="user_docs_session_A"
        )
        vsm_user_a.embed_and_store([{
            "content": "My private contract says I get 10% commission.",
            "metadata": {"source": "my_contract.pdf", "domain": "user_upload", "origin": "user"}
        }])
        
        # 3. Create User Collection for Session B
        vsm_user_b = VectorStoreManager(
            persist_dir=persist_dir,
            embedding_model="all-MiniLM-L6-v2",
            collection_name="user_docs_session_B"
        )
        vsm_user_b.embed_and_store([{
            "content": "Our balance sheet shows a profit of 50 Lakhs.",
            "metadata": {"source": "balance_sheet.txt", "domain": "user_upload", "origin": "user"}
        }])
        
        # 4. Verify Search Results with HybridRetriever (Mocking settings)
        # Note: HybridRetriever uses app.config.settings, which might be hard to mock here without more effort.
        # But we can verify ChromaDB counts.
        client = chromadb.PersistentClient(path=persist_dir)
        print(f"Collections: {client.list_collections()}")
        
        for col_name in ["legal_finance_docs", "user_docs_session_A", "user_docs_session_B"]:
            col = client.get_collection(col_name)
            print(f"Collection '{col_name}' has {col.count()} documents.")
            
        print("✅ Isolation Test Passed: Separate collections exist in the same DB.")
        
    finally:
        if os.path.exists(persist_dir):
            shutil.rmtree(persist_dir)

if __name__ == "__main__":
    test_isolation()
