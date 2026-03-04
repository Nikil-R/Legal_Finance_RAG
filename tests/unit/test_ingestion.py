"""
Unit tests for document ingestion.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestDocumentLoader:
    """Tests for DocumentLoader."""
    
    def test_load_txt_file(self, test_data_dir):
        """Test loading a text file."""
        from app.ingestion.loader import DocumentLoader
        
        loader = DocumentLoader()
        content = loader.load_txt(str(test_data_dir / "raw" / "tax" / "income_tax.txt"))
        
        assert content != ""
        assert "Section 80C" in content
    
    def test_load_directory(self, test_data_dir):
        """Test loading all documents from directory."""
        from app.ingestion.loader import DocumentLoader
        
        loader = DocumentLoader()
        documents = loader.load_directory(str(test_data_dir / "raw"))
        
        # income_tax.txt, rbi_kyc.txt, contract_act.txt
        assert len(documents) == 3
        
        domains = {doc["metadata"]["domain"] for doc in documents}
        assert domains == {"tax", "finance", "legal"}
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file."""
        from app.ingestion.loader import DocumentLoader
        
        loader = DocumentLoader()
        content = loader.load_txt("/nonexistent/file.txt")
        
        assert content == ""


class TestDocumentChunker:
    """Tests for DocumentChunker."""
    
    def test_chunk_document(self):
        """Test chunking a document."""
        from app.ingestion.chunker import DocumentChunker
        
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        
        document = {
            "content": "A" * 250,  # 250 characters
            "metadata": {
                "source": "test.txt",
                "domain": "tax",
                "file_path": "/path/to/test.txt"
            }
        }
        
        chunks = chunker.chunk_document(document)
        
        assert len(chunks) >= 2
        assert all("chunk_id" in c["metadata"] for c in chunks)
        assert all("chunk_index" in c["metadata"] for c in chunks)
    
    def test_chunk_preserves_metadata(self):
        """Test that chunking preserves original metadata."""
        from app.ingestion.chunker import DocumentChunker
        
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        
        document = {
            "content": "Test content " * 20,
            "metadata": {
                "source": "test.txt",
                "domain": "legal",
                "file_path": "/path/test.txt"
            }
        }
        
        chunks = chunker.chunk_document(document)
        
        for chunk in chunks:
            assert chunk["metadata"]["source"] == "test.txt"
            assert chunk["metadata"]["domain"] == "legal"
    
    def test_chunk_empty_document(self):
        """Test chunking empty document."""
        from app.ingestion.chunker import DocumentChunker
        
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        
        document = {
            "content": "",
            "metadata": {"source": "empty.txt", "domain": "tax", "file_path": "/path"}
        }
        
        chunks = chunker.chunk_document(document)
        
        assert len(chunks) == 0


class TestVectorStoreManager:
    """Tests for VectorStoreManager."""
    
    def test_initialization(self, chroma_test_dir):
        """Test VectorStoreManager initialization."""
        from app.ingestion.embedder import VectorStoreManager
        
        manager = VectorStoreManager(
            persist_dir=str(chroma_test_dir),
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        assert manager is not None
    
    def test_embed_and_store(self, chroma_test_dir, sample_chunks):
        """Test embedding and storing chunks."""
        from app.ingestion.embedder import VectorStoreManager
        
        manager = VectorStoreManager(
            persist_dir=str(chroma_test_dir / "test_store"),
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        count = manager.embed_and_store(sample_chunks)
        
        assert count == len(sample_chunks)
        assert manager.get_collection_count() == len(sample_chunks)
    
    def test_clear_collection(self, chroma_test_dir, sample_chunks):
        """Test clearing the collection."""
        from app.ingestion.embedder import VectorStoreManager
        
        manager = VectorStoreManager(
            persist_dir=str(chroma_test_dir / "test_clear"),
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        manager.embed_and_store(sample_chunks)
        assert manager.get_collection_count() > 0
        
        manager.clear_collection()
        assert manager.get_collection_count() == 0
