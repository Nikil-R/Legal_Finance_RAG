import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

def track_amendments(
    act_name: Optional[str] = None,
    date_range: Optional[Dict[str, str]] = None,
    legal_domain: Optional[str] = None,
    amendment_type: Optional[str] = None,
    num_results: int = 10
) -> Dict[str, Any]:
    """
    Track recent amendments, notifications, and circulars related to tax laws and regulations.
    
    Args:
        act_name: Specific act name (e.g., "Income Tax Act, 1961")
        date_range: {"from": "YYYY-MM-DD", "to": "YYYY-MM-DD"}
        legal_domain: Domain (income_tax, gst, nbfc_rbi, corporate_law, labor_law)
        amendment_type: Type of change (Finance Act, Circular, Regulatory Notification)
        num_results: Number of results to return
    
    Returns:
        Recent amendments with impact analysis and comparison of old vs new provisions
    """
    try:
        data_path = Path(__file__).parent.parent / "data" / "amendments_circulars.json"
        with open(data_path, "r") as f:
            data = json.load(f)
        
        amendments_list = data["recent_amendments"]
        results = []
        
        # Filter amendments based on criteria
        for amendment in amendments_list:
            # Act name filter
            if act_name and act_name.lower() not in amendment.get("act_name", "").lower():
                continue
            
            # Amendment type filter
            if amendment_type and amendment_type.lower() != amendment.get("amendment_type", "").lower():
                continue
            
            # Date range filter
            if date_range:
                amend_date = amendment.get("amendment_date", "")
                if date_range.get("from") and amend_date < date_range["from"]:
                    continue
                if date_range.get("to") and amend_date > date_range["to"]:
                    continue
            
            results.append(amendment)
        
        # Generate detailed impact analysis
        detailed_results = []
        for amendment in results[:num_results]:
            impact_analysis = {
                "citation": amendment.get("notification_number"),
                "title": amendment.get("title"),
                "act": amendment.get("act_name"),
                "amendment_date": amendment.get("amendment_date"),
                "effective_date": amendment.get("effective_date"),
                "type": amendment.get("amendment_type"),
                "issuing_authority": amendment.get("issuing_authority"),
                "summary": amendment.get("summary"),
                "old_provision": amendment.get("old_provision"),
                "new_provision": amendment.get("new_provision"),
                "key_changes": _extract_key_changes(amendment),
                "comparison": {
                    "old": amendment.get("old_provision") or amendment.get("old_position"),
                    "new": amendment.get("new_provision") or amendment.get("new_position"),
                    "impact": "Broadly favorable" if _is_favorable(amendment) else "May increase compliance burden"
                },
                "applicable_to": amendment.get("if_applicable", []),
                "implementation_status": amendment.get("implementation_status"),
                "impact_analysis": amendment.get("impact_analysis"),
                "transitional_provisions": amendment.get("transitional_provisions"),
                "related_sections": amendment.get("related_sections", []),
                "financial_impact": _estimate_financial_impact(amendment),
                "action_items": _generate_action_items(amendment)
            }
            
            detailed_results.append(impact_analysis)
        
        # Build amendment timeline
        timeline = _build_amendment_timeline(detailed_results)
        
        return {
            "success": True,
            "filters_applied": {
                "act": act_name or "All",
                "domain": legal_domain or "All",
                "type": amendment_type or "All"
            },
            "total_amendments_found": len(results),
            "amendments_count": len(detailed_results),
            "amendments": detailed_results,
            "timeline": timeline,
            "summary": _generate_amendment_summary(detailed_results),
            "compliance_impact": _assess_compliance_impact(detailed_results),
            "recommendations": _generate_amendment_recommendations(detailed_results)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _extract_key_changes(amendment: Dict) -> List[str]:
    """Extract key changes from amendment"""
    changes = []
    
    if "requirements" in amendment:
        changes.extend([f"New requirement: {req}" for req in amendment["requirements"]])
    
    if "conditions" in amendment:
        changes.extend([f"Condition: {cond}" for cond in amendment["conditions"]])
    
    return changes[:3]  # Return top 3 key changes

def _is_favorable(amendment: Dict) -> bool:
    """Determine if amendment is generally favorable"""
    unfavorable_keywords = ["penalty", "criminal", "jail", "prosecution", "enhanced"]
    title_lower = amendment.get("title", "").lower()
    return not any(keyword in title_lower for keyword in unfavorable_keywords)

def _estimate_financial_impact(amendment: Dict) -> Dict:
    """Estimate financial impact of amendment"""
    impact = amendment.get("impact_analysis", "")
    
    if "save" in impact.lower() or "benefit" in impact.lower():
        return {
            "type": "Positive",
            "description": "Potential tax savings or compliance benefits",
            "benefit_range": "₹5,000-50,000+ depending on taxpayer profile"
        }
    elif "cost" in impact.lower() or "penalty" in impact.lower():
        return {
            "type": "Negative",
            "description": "Potential increased compliance cost or penalties",
            "cost_range": "₹5,000-1,00,000+ for non-compliance"
        }
    else:
        return {
            "type": "Neutral",
            "description": "Clarification or procedural changes"
        }

def _generate_action_items(amendment: Dict) -> List[str]:
    """Generate specific action items for the amendment"""
    actions = []
    
    effective_date = amendment.get("effective_date")
    if effective_date:
        actions.append(f"Ensure full compliance by {effective_date}")
    
    if "transitional_provisions" in amendment:
        actions.append("Review and understand all transitional provisions")
    
    if "if_applicable" in amendment:
        applicable = amendment["if_applicable"]
        if applicable:
            actions.append(f"Verify applicability: {', '.join(applicable[:2])}")
    
    actions.append("Consult with tax/legal professional for entity-specific implications")
    
    return actions

def _build_amendment_timeline(amendments: List[Dict]) -> List[Dict]:
    """Build a chronological timeline of amendments"""
    sorted_amends = sorted(amendments, key=lambda x: x.get("effective_date", ""), reverse=True)
    
    timeline = []
    for amend in sorted_amends:
        timeline.append({
            "effective_date": amend.get("effective_date"),
            "amendment_date": amend.get("amendment_date"),
            "act": amend.get("act"),
            "change": amend.get("title"),
            "status": amend.get("implementation_status")
        })
    
    return timeline

def _generate_amendment_summary(amendments: List[Dict]) -> str:
    """Generate summary of amendments"""
    if not amendments:
        return "No amendments found matching the specified criteria."
    
    recent_count = len(amendments)
    latest = amendments[0] if amendments else {}
    
    return f"Found {recent_count} recent amendments and regulations. Most recent: {latest.get('title', 'N/A')} (Effective: {latest.get('effective_date', 'N/A')})"

def _assess_compliance_impact(amendments: List[Dict]) -> Dict:
    """Assess overall compliance impact"""
    high_impact = sum(1 for a in amendments if "penalty" in str(a).lower())
    procedural_changes = sum(1 for a in amendments if "filing" in str(a).lower())
    
    return {
        "high_impact_changes": high_impact,
        "procedural_changes": procedural_changes,
        "overall_complexity": "High" if high_impact > 2 else "Medium" if high_impact > 0 else "Low",
        "urgent_action_needed": high_impact > 0
    }

def _generate_amendment_recommendations(amendments: List[Dict]) -> List[str]:
    """Generate recommendations for handling amendments"""
    recommendations = []
    
    if any("effective" in str(a.get("effective_date", "")).lower() for a in amendments):
        recommendations.append("Review all amendments with effective dates in current or coming quarters")
    
    has_penalties = any("penalty" in str(a).lower() for a in amendments)
    if has_penalties:
        recommendations.append("Engage immediate compliance review to avoid penalties")
    
    recommendations.extend([
        "Maintain clear documentation of amendment compliance",
        "Brief your team on new requirements immediately",
        "Review vendor/client contracts for potential implications"
    ])
    
    return recommendations
