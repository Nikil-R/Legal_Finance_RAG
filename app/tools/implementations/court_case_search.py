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
    Scans both the central database and individual case files.
    """
    try:
        all_cases = []
        
        # 1. Load from central data file
        central_path = Path(__file__).parent.parent / "data" / "court_cases.json"
        if central_path.exists():
            with open(central_path, "r", encoding="utf-8") as f:
                central_data = json.load(f)
                all_cases.extend(central_data.get("cases", []))
        
        # 2. Load from individual case files (e.g., in data/real/court_cases)
        # Assuming project root is 3 levels up from this file: app/tools/implementations/court_case_search.py
        real_cases_dir = Path(__file__).parent.parent.parent.parent / "data" / "real" / "court_cases"
        if real_cases_dir.exists():
            for json_file in real_cases_dir.glob("*.json"):
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        case_data = json.load(f)
                        if isinstance(case_data, dict):
                            # Avoid duplicates if they are already in the central file
                            if not any(c.get("case_id") == case_data.get("case_id") for c in all_cases):
                                all_cases.append(case_data)
                except Exception:
                    continue

        results = []
        query_lower = str(query).lower()
        
        # Search through cases
        for case in all_cases:
            if not isinstance(case, dict):
                continue
                
            # Basic relevance scoring
            relevance_score: float = 0.0
            
            # Check citation match
            citation = str(case.get("citation", "")).lower()
            if query_lower in citation:
                relevance_score += 10.0
            
            # Check title match
            title = str(case.get("title", "") or case.get("case_name", "")).lower()
            if query_lower in title:
                relevance_score += 8.0
            
            # Check legal principles / subcategories
            principles = case.get("legal_principles", []) or case.get("legal_issues", []) or case.get("subcategories", [])
            if isinstance(principles, list):
                for principle in principles:
                    if query_lower in str(principle).lower():
                        relevance_score += 3.0
            
            # Check summary
            summary = str(case.get("summary", "")).lower()
            if query_lower in summary:
                relevance_score += 4.0
            
            # Court name filter
            actual_court = str(case.get("court", "")).lower()
            if court_name and court_name.lower() not in actual_court:
                continue
            
            # Date range filter
            decision_date = str(case.get("decision_date") or case.get("judgment_date") or "")
            if date_range and decision_date:
                from_date = str(date_range.get("from", ""))
                to_date = str(date_range.get("to", ""))
                if from_date and decision_date < from_date:
                    continue
                if to_date and decision_date > to_date:
                    continue
            
            # Additional keywords filter
            if case_keywords:
                kw_matches = 0
                principles_str = " ".join(map(str, principles)) if isinstance(principles, list) else str(principles)
                combined_text = (title + " " + principles_str + " " + summary).lower()
                for keyword in case_keywords:
                    if str(keyword).lower() in combined_text:
                        kw_matches += 1
                relevance_score += float(kw_matches) * 2.0
            
            if relevance_score > 0:
                results.append({
                    "case": case,
                    "score": relevance_score
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: float(x.get("score", 0.0)), reverse=True)
        results = results[:num_results]
        
        # Format results
        formatted_results = []
        for item in results:
            case = item.get("case", {})
            score = float(item.get("score", 0.0))
            formatted_results.append({
                "citation": str(case.get("citation", "N/A")),
                "case_name": str(case.get("title") or case.get("case_name", "N/A")),
                "court": str(case.get("court", "N/A")),
                "judgment_date": str(case.get("decision_date") or case.get("judgment_date", "N/A")),
                "judges": list(case.get("judges", [])),
                "legal_issues": list(case.get("legal_principles", []) or case.get("legal_issues", [])),
                "ratio_decidendi": str(case.get("summary", "N/A")),
                "key_principles": list(case.get("key_holdings", []) or case.get("key_principles", [])),
                "relevance_score": score
            })
        
        return {
            "success": True,
            "query": query,
            "results_count": len(formatted_results),
            "cases": formatted_results,
            "summary": f"Found {len(formatted_results)} relevant court cases across central and local repositories.",
            "next_steps": "Review the case summaries or citations for legal research."
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"{str(e)}\n{traceback.format_exc()}"
        }
