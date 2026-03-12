from typing import Dict, Any, List, Optional
from app.reranking.pipeline import RetrievalPipeline
from app.config import settings

def search_legal_documents(
    query: str,
    num_results: int = 5,
    domain: str = "all"
) -> Dict[str, Any]:
    """
    Search through legal and financial documents using the RAG pipeline.
    """
    pipeline = RetrievalPipeline()
    
    # Run the retrieval and reranking process
    result = pipeline.run(
        query=query,
        domain=domain,
        rerank_top_k=num_results
    )
    
    if not result["success"]:
        return {
            "success": False,
            "error": result.get("error", "Search failed")
        }
        
    formatted_results = []
    for src in result.get("sources", []):
        formatted_results.append({
            "citation_id": src["reference_id"],
            "content": src["content"],
            "source": src["source"],
            "page": src.get("page"),
            "domain": src["domain"],
            "relevance_score": src.get("rerank_score", 0.0)
        })
        
    return {
        "success": True,
        "results": formatted_results,
        "total_found": result.get("candidates_found", 0),
        "query": query
    }
