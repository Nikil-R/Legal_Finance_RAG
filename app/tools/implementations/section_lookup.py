import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.tools.implementations.document_search import search_legal_documents

def lookup_act_section(
    section: str,
    act: str = "Income Tax Act"
) -> Dict[str, Any]:
    """
    Look up a specific section of an Indian Act.
    """
    data_path = Path(__file__).parent.parent / "data" / "sections_summary.json"
    
    # Try local summary first
    if data_path.exists():
        with open(data_path, "r") as f:
            sections_data = json.load(f)
            
        if act in sections_data and section in sections_data[act]:
            section_info = sections_data[act][section]
            return {
                "found": True,
                "act": act,
                "section": section,
                "title": section_info.get("title"),
                "max_deduction": section_info.get("max_deduction"),
                "applicable_to": section_info.get("applicable_to"),
                "key_investments": section_info.get("key_investments"),
                "summary": section_info.get("summary"),
                "source": "local_database"
            }
            
    # Fallback to document search
    search_query = f"{act} Section {section}"
    search_result = search_legal_documents(query=search_query, num_results=3)
    
    if search_result["success"] and search_result["results"]:
        return {
            "found": True,
            "act": act,
            "section": section,
            "summary": search_result["results"][0]["content"],
            "source": "document_search",
            "search_results": search_result["results"]
        }
        
    return {
        "found": False,
        "act": act,
        "section": section,
        "message": f"Could not find specific details for {act} Section {section}."
    }
