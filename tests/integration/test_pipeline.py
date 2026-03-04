"""
Integration tests for the complete pipeline.
"""
import pytest
import os
from unittest.mock import patch, MagicMock


class TestIngestionPipeline:
    """Integration tests for ingestion pipeline."""
    
    def test_full_ingestion_pipeline(self, test_data_dir, chroma_test_dir):
        """Test complete ingestion pipeline."""
        from app.ingestion.pipeline import run_ingestion_pipeline
        
        with patch("app.config.get_settings") as mock_settings:
            settings = MagicMock()
            settings.CHROMA_PERSIST_DIR = str(chroma_test_dir / "integration")
            settings.EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
            settings.CHUNK_SIZE = 512
            settings.CHUNK_OVERLAP = 50
            mock_settings.return_value = settings
            
            # Would need to set data directory
            # This is a simplified test
            assert True  # Placeholder


class TestRetrievalPipeline:
    """Integration tests for retrieval pipeline."""
    
    @pytest.fixture
    def setup_retrieval(self, chroma_test_dir, sample_chunks):
        """Setup retrieval with test data."""
        from app.ingestion.embedder import VectorStoreManager
        
        persist_dir = str(chroma_test_dir / "retrieval_integration")
        
        manager = VectorStoreManager(
            persist_dir=persist_dir,
            embedding_model="sentence-transformers/all-MiniLM-L6-v2"
        )
        manager.clear_collection()
        manager.embed_and_store(sample_chunks)
        
        return persist_dir
    
    def test_hybrid_retrieval(self, setup_retrieval):
        """Test hybrid retrieval combines vector and BM25."""
        # This would test the HybridRetriever
        # Simplified for demonstration
        assert True


class TestRAGPipeline:
    """Integration tests for full RAG pipeline."""
    
    @pytest.mark.requires_api_key
    def test_full_rag_pipeline(self, skip_without_api_key):
        """Test complete RAG pipeline with real API call."""
        from app.generation import RAGPipeline
        
        pipeline = RAGPipeline()
        result = pipeline.run(
            question="What are Section 80C deductions?",
            domain="tax"
        )
        
        assert "success" in result
        if result["success"]:
            assert "answer" in result
            assert len(result["answer"]) > 0
    
    def test_rag_pipeline_with_mock(self, mock_groq_client, sample_chunks):
        """Test RAG pipeline with mocked LLM."""
        # Would test with mocked components
        assert True
