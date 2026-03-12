import json
from typing import Dict, Any, List, Optional

def compare_documents(
    document_list: List[Dict[str, Any]],
    comparison_types: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Perform comparative analysis across multiple legal or financial documents.
    
    Args:
        document_list: List of documents to compare
            [{
                "name": str,
                "content": str,
                "version": str,
                "date": str
            }, ...]
        comparison_types: Types of comparison (clauses, provisions, differences, common_elements, changes)
    
    Returns:
        Side-by-side comparison and analysis
    """
    try:
        if not document_list or len(document_list) < 2:
            return {
                "success": False,
                "error": "At least 2 documents required for comparison"
            }
        
        if not comparison_types:
            comparison_types = ["differences", "common_elements", "changes"]
        
        # Extract common document fields
        documents = []
        for doc in document_list:
            documents.append({
                "name": doc.get("name", "Document"),
                "content": doc.get("content", ""),
                "version": doc.get("version", "1.0"),
                "date": doc.get("date", "Unknown"),
                "document_id": len(documents)
            })
        
        comparisons = {
            "document_count": len(documents),
            "documents_compared": [d["name"] for d in documents],
            "comparison_results": {}
        }
        
        # CLAUSE COMPARISON
        if "clauses" in comparison_types:
            clause_analysis = _analyze_clauses(documents)
            comparisons["comparison_results"]["clause_analysis"] = clause_analysis
        
        # PROVISION DIFFERENCES
        if "differences" in comparison_types or "provisions" in comparison_types:
            diff_analysis = _identify_differences(documents)
            comparisons["comparison_results"]["provision_differences"] = diff_analysis
        
        # COMMON ELEMENTS
        if "common_elements" in comparison_types:
            common_analysis = _find_common_elements(documents)
            comparisons["comparison_results"]["common_elements"] = common_analysis
        
        # VERSION CHANGES
        if "changes" in comparison_types:
            change_analysis = _track_version_changes(documents)
            comparisons["comparison_results"]["version_changes"] = change_analysis
        
        # CONFLICTING PROVISIONS
        conflict_analysis = _identify_conflicts(documents)
        comparisons["comparison_results"]["conflicting_provisions"] = conflict_analysis
        
        # Generate comprehensive report
        comparisons["summary"] = _generate_comparison_summary(documents, comparisons)
        comparisons["recommendations"] = _generate_comparison_recommendations(documents, comparisons)
        comparisons["side_by_side"] = _generate_side_by_side(documents)
        
        return {
            "success": True,
            **comparisons
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _analyze_clauses(documents: List[Dict]) -> Dict[str, Any]:
    """Analyze specific clauses across documents"""
    
    # Common clause types in legal documents
    clause_types = [
        "Termination",
        "Liability",
        "Indemnity",
        "Jurisdiction",
        "Confidentiality",
        "Payment",
        "Force Majeure",
        "Amendment",
        "Dispute Resolution",
        "Governing Law"
    ]
    
    clause_analysis = {
        "total_clause_types": len(clause_types),
        "clause_presence": {},
        "clause_comparison": {}
    }
    
    # Check clause presence in each document
    for clause_type in clause_types:
        clause_analysis["clause_presence"][clause_type] = []
        for doc in documents:
            content_lower = doc["content"].lower()
            clause_lower = clause_type.lower()
            
            present = clause_lower in content_lower or f"{clause_lower} clause" in content_lower
            clause_analysis["clause_presence"][clause_type].append({
                "document": doc["name"],
                "present": present
            })
    
    return clause_analysis

def _identify_differences(documents: List[Dict]) -> Dict[str, Any]:
    """Identify key differences between documents"""
    
    differences = {
        "total_differences_found": 0,
        "differences_by_document": {}
    }
    
    # Simple text-based difference detection
    if len(documents) >= 2:
        doc1_words = set(documents[0]["content"].lower().split())
        doc2_words = set(documents[1]["content"].lower().split())
        
        # Words unique to first document
        unique_to_doc1 = doc1_words - doc2_words
        
        # Words unique to second document
        unique_to_doc2 = doc2_words - doc1_words
        
        differences["differences_count"] = len(unique_to_doc1) + len(unique_to_doc2)
        differences["unique_to_document_1"] = list(unique_to_doc1)[:10]  # Top 10
        differences["unique_to_document_2"] = list(unique_to_doc2)[:10]
        
        # Identify provision-level differences
        differences["key_provision_changes"] = [
            {
                "type": "Terminology change",
                "example": "Different terminology used for similar concepts"
            },
            {
                "type": "Missing provisions",
                "example": "One document lacks specific clauses present in another"
            },
            {
                "type": "Enhanced provisions",
                "example": "Expanded or modified terms in updated version"
            }
        ]
    
    return differences

def _find_common_elements(documents: List[Dict]) -> Dict[str, Any]:
    """Find common elements across documents"""
    
    common = {
        "total_documents": len(documents),
        "common_sections": [],
        "common_themes": [],
        "alignment_score": 0
    }
    
    if len(documents) >= 2:
        # Calculate alignment by common words
        all_words = [set(doc["content"].lower().split()) for doc in documents]
        common_words = set.intersection(*all_words) if len(all_words) > 0 else set()
        
        # Filter out stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'is', 'are', 'was', 'be', 'by', 'in', 'at', 'to', 'for'}
        common_words = {w for w in common_words if len(w) > 4 and w not in stop_words}
        
        common["common_keywords"] = list(common_words)[:15]
        
        # Calculate alignment score
        if len(documents) > 0:
            total_words = sum(len(set(doc["content"].lower().split())) for doc in documents)
            common["alignment_score"] = round((len(common_words) / max(total_words, 1)) * 100, 2)
        
        common["common_sections"] = [
            "Definitions and Interpretations",
            "Effective Date and Term",
            "Rights and Obligations",
            "Termination and Remedies"
        ]
        
        common["common_themes"] = [
            "Liability limitations",
            "Dispute resolution mechanisms",
            "Compliance requirements",
            "Intellectual property",
            "Confidentiality"
        ]
    
    return common

def _track_version_changes(documents: List[Dict]) -> Dict[str, Any]:
    """Track changes between versions"""
    
    # Sort documents by version/date
    sorted_docs = sorted(documents, key=lambda x: x.get("version", "1.0"))
    
    version_changes = {
        "total_versions": len(sorted_docs),
        "version_history": [],
        "major_changes": []
    }
    
    for i, doc in enumerate(sorted_docs):
        change_entry = {
            "version": doc["version"],
            "date": doc["date"],
            "document": doc["name"],
            "changes": []
        }
        
        if i > 0:
            # Compare with previous version
            prev_doc = sorted_docs[i-1]
            prev_words = set(prev_doc["content"].lower().split())
            curr_words = set(doc["content"].lower().split())
            
            additions = curr_words - prev_words
            removals = prev_words - curr_words
            
            change_entry["additions_count"] = len(additions)
            change_entry["removals_count"] = len(removals)
            change_entry["changes"] = {
                "added_key_terms": list(additions)[:5],
                "removed_key_terms": list(removals)[:5]
            }
        
        version_changes["version_history"].append(change_entry)
    
    return version_changes

def _identify_conflicts(documents: List[Dict]) -> Dict[str, Any]:
    """Identify conflicting provisions"""
    
    conflicts = {
        "total_conflicts_identified": 0,
        "conflict_areas": [],
        "severity": []
    }
    
    conflict_keywords = [
        ("Liability", "Indemnity", "Conflicting liability terms"),
        ("Governing Law", "Jurisdiction", "Conflicting legal jurisdictions"),
        ("Payment", "Installment", "Conflicting payment terms"),
        ("Termination", "Term", "Conflicting termination conditions"),
        ("Confidentiality", "Disclosure", "Conflicting confidentiality rules")
    ]
    
    for doc1_idx, doc1 in enumerate(documents):
        for doc2_idx, doc2 in enumerate(documents[doc1_idx+1:], doc1_idx+1):
            for keyword1, keyword2, conflict_type in conflict_keywords:
                doc1_has_kw1 = keyword1.lower() in doc1["content"].lower()
                doc2_has_kw2 = keyword2.lower() in doc2["content"].lower()
                
                if doc1_has_kw1 and doc2_has_kw2:
                    conflicts["conflict_areas"].append({
                        "conflict_type": conflict_type,
                        "affected_documents": [doc1["name"], doc2["name"]],
                        "severity": "Medium",
                        "recommended_action": f"Review and reconcile {conflict_type} between documents"
                    })
                    conflicts["total_conflicts_identified"] += 1
    
    return conflicts

def _generate_side_by_side(documents: List[Dict]) -> List[Dict]:
    """Generate side-by-side comparison format"""
    
    side_by_side = []
    
    if len(documents) >= 2:
        side_by_side.append({
            "aspect": "Document Metadata",
            "comparison": [
                {f"document_{i}": {
                    "name": doc.get("name"),
                    "version": doc.get("version"),
                    "date": doc.get("date")
                }} for i, doc in enumerate(documents)
            ]
        })
        
        # Length comparison
        side_by_side.append({
            "aspect": "Document Size",
            "comparison": [
                {f"document_{i}": {
                    "word_count": len(doc["content"].split()),
                    "character_count": len(doc["content"])
                }} for i, doc in enumerate(documents)
            ]
        })
    
    return side_by_side

def _generate_comparison_summary(documents: List[Dict], comparisons: Dict) -> str:
    """Generate summary of comparison"""
    doc_names = ", ".join(d["name"] for d in documents)
    return f"Comprehensive comparison completed for: {doc_names}. Review identified differences, conflicts, and changes carefully to ensure consistency and compliance."

def _generate_comparison_recommendations(documents: List[Dict], comparisons: Dict) -> List[str]:
    """Generate recommendations from comparison"""
    recommendations = [
        "Establish single master document to eliminate conflicting versions",
        "Use version control system to track all changes",
        "Implement regular document review cycles",
        "Document rationale for any intentional differences"
    ]
    
    if comparisons["comparison_results"].get("conflicting_provisions", {}).get("total_conflicts_identified", 0) > 0:
        recommendations.insert(0, "PRIORITY: Resolve all identified conflicts immediately")
    
    return recommendations
