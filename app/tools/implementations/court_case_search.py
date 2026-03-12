import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

def search_court_cases(
    query: str,
    case_keywords: Optional[List[str]] = None,
    court_name: Optional[str] = None,
    date_range: Optional[Dict[str, str]] = None,
    num_results: int = 5
) -> Dict[str, Any]:
    """
    Search through Indian court judgments and legal precedents.
    
    Args:
        query: Main search query (citation, case name, or keywords)
        case_keywords: Additional keywords to filter by
        court_name: Specific court (Supreme Court, High Court, etc.)
        date_range: {"from": "YYYY-MM-DD", "to": "YYYY-MM-DD"}
        num_results: Number of results to return
    
    Returns:
        Dictionary with search results and case details
    """
    try:
        data_path = Path(__file__).parent.parent / "data" / "court_cases.json"
        with open(data_path, "r") as f:
            data = json.load(f)
        
        results = []
        query_lower = query.lower()
        
        # Search through cases
        for case in data["cases"]:
            # Basic relevance scoring
            relevance_score = 0
            
            # Check citation match
            if query_lower in case["citation"].lower():
                relevance_score += 10
            
            # Check case name match
            if query_lower in case["case_name"].lower():
                relevance_score += 8
            
            # Check legal issues
            for issue in case["legal_issues"]:
                if query_lower in issue.lower():
                    relevance_score += 3
            
            # Check keywords
            if query_lower in case.get("relevance_keywords", []):
                relevance_score += 5
            
            # Court name filter
            if court_name and court_name.lower() not in case["court"].lower():
                continue
            
            # Date range filter
            if date_range:
                case_date = case["judgment_date"]
                if date_range.get("from") and case_date < date_range["from"]:
                    continue
                if date_range.get("to") and case_date > date_range["to"]:
                    continue
            
            # Additional keywords filter
            if case_keywords:
                keyword_matches = 0
                for keyword in case_keywords:
                    kw_lower = keyword.lower()
                    if (kw_lower in case["case_name"].lower() or 
                        kw_lower in " ".join(case["legal_issues"]).lower()):
                        keyword_matches += 1
                relevance_score += keyword_matches * 2
            
            if relevance_score > 0:
                results.append({
                    "case": case,
                    "score": relevance_score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:num_results]
        
        # Format results
        formatted_results = []
        for item in results:
            case = item["case"]
            formatted_results.append({
                "citation": case["citation"],
                "case_name": case["case_name"],
                "court": case["court"],
                "judgment_date": case["judgment_date"],
                "judges": case["judges"],
                "legal_issues": case["legal_issues"],
                "ratio_decidendi": case["ratio_decidendi"],
                "key_principles": case["key_principles"],
                "impact_level": case["impact_level"],
                "area_of_law": case["area_of_law"],
                "key_excerpts": case["excerpts"][:2],  # Top 2 excerpts
                "relevance_score": item["score"]
            })
        
        return {
            "success": True,
            "query": query,
            "results_count": len(formatted_results),
            "cases": formatted_results,
            "summary": f"Found {len(formatted_results)} relevant court cases",
            "next_steps": "Use case citations for further legal research or consult a lawyer for case-specific advice"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
