import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

def check_compliance(
    business_type: str,
    industry_sector: Optional[str] = None,
    state: Optional[str] = None,
    specific_acts: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Check compliance requirements for a business entity and activities.
    
    Args:
        business_type: Type of entity (sole_proprietor, private_limited_company, llp, partnership)
        industry_sector: Industry type (pharmaceuticals, food_business, finance_nbfc, etc.)
        state: Indian state for jurisdiction-specific regulations
        specific_acts: Specific acts to query
    
    Returns:
        Comprehensive compliance requirements and deadlines
    """
    try:
        data_path = Path(__file__).parent.parent / "data" / "compliance_requirements.json"
        with open(data_path, "r") as f:
            data = json.load(f)
        
        compliance_matrix = data["compliance_matrix"]
        industry_specific = data["industry_specific"]
        state_regulations = data["state_regulations"]
        
        requirements = []
        deadlines = []
        filing_requirements = []
        penalties_list = []
        
        # Get entity-specific requirements
        if business_type in compliance_matrix:
            entity_reqs = compliance_matrix[business_type]
            
            for category, details in entity_reqs.items():
                if isinstance(details, dict):
                    requirements.append({
                        "category": category,
                        "details": details
                    })
                    
                    # Extract deadlines
                    if "filing_deadline" in details:
                        deadlines.append({
                            "category": category,
                            "deadline": details["filing_deadline"],
                            "frequency": details.get("filing_frequency", "annual")
                        })
                    
                    # Extract penalties
                    if "penalties" in details:
                        for penalty_type, penalty_info in details["penalties"].items():
                            penalties_list.append({
                                "violation": penalty_type,
                                "category": category,
                                "penalty": penalty_info
                            })
        
        # Add industry-specific requirements
        if industry_sector and industry_sector in industry_specific:
            industry_reqs = industry_specific[industry_sector]
            requirements.append({
                "category": f"industry_specific_{industry_sector}",
                "details": industry_reqs
            })
        
        # Add state-specific regulations
        if state and state.lower() in state_regulations:
            state_reqs = state_regulations[state.lower()]
            requirements.append({
                "category": f"state_specific_{state}",
                "details": state_reqs
            })
        
        # Build compliance calendar
        compliance_calendar = _build_compliance_calendar(deadlines, state)
        
        return {
            "success": True,
            "business_type": business_type,
            "industry_sector": industry_sector or "General",
            "state": state or "Pan-India",
            "total_requirements": len(requirements),
            "requirements": requirements,
            "critical_deadlines": sorted(deadlines, key=lambda x: _parse_deadline(x["deadline"])),
            "compliance_calendar": compliance_calendar,
            "applicable_penalties": penalties_list,
            "summary": _generate_compliance_summary(business_type, industry_sector, state),
            "recommendations": _generate_recommendations(business_type, industry_sector)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _parse_deadline(deadline_str: str) -> tuple:
    """Parse deadline string like '31-07' to sortable format"""
    try:
        day, month = map(int, deadline_str.split('-'))
        return (month, day)
    except:
        return (12, 31)  # Default to end of year

def _build_compliance_calendar(deadlines: List[Dict], state: Optional[str]) -> List[Dict]:
    """Build a comprehensive compliance calendar for the year"""
    calendar = []
    for deadline in deadlines:
        calendar.append({
            "filing_type": deadline["category"],
            "month_day": deadline["deadline"],
            "frequency": deadline["frequency"],
            "description": f"Submit {deadline['category']} by {deadline['deadline']}"
        })
    return sorted(calendar, key=lambda x: _parse_deadline(x["month_day"]))

def _generate_compliance_summary(business_type: str, industry: Optional[str], state: Optional[str]) -> str:
    """Generate a human-readable compliance summary"""
    summary = f"Compliance requirements for {business_type}"
    if industry:
        summary += f" in {industry} industry"
    if state:
        summary += f" in {state}"
    summary += " have been retrieved. Please review all deadlines carefully and ensure timely submissions to avoid penalties."
    return summary

def _generate_recommendations(business_type: str, industry: Optional[str]) -> List[str]:
    """Generate specific recommendations based on business type"""
    recommendations = [
        "Maintain organized records for minimum 6 years for audit trail",
        "Implement a compliance calendar system for deadline tracking",
        "Engage professional help (CA, CS) for regulatory matters"
    ]
    
    if business_type == "private_limited_company":
        recommendations.extend([
            "Conduct quarterly board meetings as per MCA requirements",
            "File annual returns within 30 days of AGM",
            "Maintain secretarial and audit compliance strictly"
        ])
    
    if industry == "pharmaceuticals":
        recommendations.extend([
            "Maintain GMP certification validity",
            "Implement anti-counterfeiting measures",
            "Regular DCO approvals for manufacturing"
        ])
    
    return recommendations
