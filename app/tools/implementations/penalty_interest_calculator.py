import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

def calculate_penalties_and_interest(
    violation_type: str,
    violation_details: Dict[str, Any],
    jurisdiction: str = "federal"
) -> Dict[str, Any]:
    """
    Calculate penalties, interest, and late fees for various compliance violations.
    
    Args:
        violation_type: Type of violation (tax_filing, gst_payment, corporate_filing, etc.)
        violation_details: {
            "principal_amount": float (amount at stake),
            "days_delayed": int,
            "applicable_law": str,
            "entity_type": str
        }
        jurisdiction: Jurisdiction level (federal, state)
    
    Returns:
        Calculated penalties, interest, and total liability
    """
    try:
        data_path = Path(__file__).parent.parent / "data" / "penalties_interest.json"
        with open(data_path, "r") as f:
            data = json.load(f)
        
        penalty_schedules = data["penalty_schedules"]
        interest_calculations = data["interest_calculations"]
        
        principal_amount = violation_details.get("principal_amount", 0)
        days_delayed = violation_details.get("days_delayed", 0)
        applicable_law = violation_details.get("applicable_law", "")
        entity_type = violation_details.get("entity_type", "")
        
        breakdown = {
            "principal_amount": principal_amount,
            "days_delayed": days_delayed
        }
        
        penalties = {}
        interest_amount = 0
        total_liability = principal_amount
        
        # INCOME TAX VIOLATIONS
        if "income_tax" in violation_type.lower() or "tax_filing" in violation_type.lower():
            breakdown["violation_category"] = "Income Tax"
            
            if "return_filing" in violation_type.lower():
                penalties["late_filing_penalty"] = {
                    "name": "Late Return Filing Penalty (Section 271F)",
                    "amount": 5000,
                    "applicability": "Any return filed after due date",
                    "description": "Flat penalty of ₹5,000 for filing late"
                }
                total_liability += 5000
                
                # Interest on tax difference
                if principal_amount > 0:
                    months_delayed = max(1, days_delayed // 30)
                    interest_rate = 0.01  # 1% per month
                    interest_amount = principal_amount * interest_rate * months_delayed
                    
                    breakdown["interest"] = {
                        "rate": "1% per month",
                        "months": months_delayed,
                        "calculation": f"₹{principal_amount} × 1% × {months_delayed} months",
                        "amount": interest_amount
                    }
                    total_liability += interest_amount
            
            elif "non_filing" in violation_type.lower():
                # Determine if deliberate or not
                penalty_amount = min(0.5 * principal_amount, 50000) if principal_amount > 0 else 5000
                
                penalties["non_filing_penalty"] = {
                    "name": "Non-Filing Penalty (Section 271A / Criminal u/s 276CC)",
                    "penalty_range": f"50% to 300% of tax payable (approx ₹{penalty_amount})",
                    "applicability": "Deliberate non-filing to evade tax",
                    "criminal_prosecution": "Up to 2 years imprisonment + fine",
                    "note": "Exact amount depends on intent and circumstances"
                }
                total_liability += max(penalty_amount, 10000)
            
            elif "concealment" in violation_type.lower():
                # Slab-based penalty
                if principal_amount == 0:
                    penalty_slab = 0
                elif principal_amount * 0.50 < principal_amount * 0.25:
                    penalty_slab = 0.50 * principal_amount  # 50% for up to 25%
                elif principal_amount * 0.50 < principal_amount * 0.50:
                    penalty_slab = 1.0 * principal_amount  # 100% for 25-50%
                else:
                    penalty_slab = 1.5 * principal_amount  # 150% for above 50%
                
                penalties["concealment_penalty"] = {
                    "name": "Concealment Penalty (Section 271(1)(c))",
                    "amount": penalty_slab,
                    "slab_description": "Based on degree of concealment (50%-300% of tax)",
                    "calculation": f"Estimated at ₹{penalty_slab}"
                }
                total_liability += penalty_slab
        
        # GST VIOLATIONS
        elif "gst" in violation_type.lower():
            breakdown["violation_category"] = "GST"
            
            if "late_return" in violation_type.lower():
                # GST late filing penalty
                daily_penalty = 100
                max_penalty = 5000
                penalty_amount = min(daily_penalty * days_delayed, max_penalty)
                
                penalties["late_gstr_filing"] = {
                    "name": "Late GSTR-1/GSTR-3B Filing Penalty",
                    "calculation": f"₹100 per day × {days_delayed} days (max ₹5,000)",
                    "amount": penalty_amount,
                    "compounding_option": f"Available with additional 50% (₹{penalty_amount * 1.5})"
                }
                total_liability += penalty_amount
            
            elif "non_payment" in violation_type.lower():
                # GST non-payment penalty and interest
                gst_penalty_rate = 0.10  # 10%
                gst_penalty = principal_amount * gst_penalty_rate
                
                # Interest at 18% p.a.
                months_delayed = max(1, days_delayed // 30)
                interest_rate = 0.18 / 12  # 1.5% per month
                gst_interest = principal_amount * interest_rate * months_delayed
                
                penalties["non_payment_penalty"] = {
                    "name": "GST Non-Payment Penalty",
                    "penalty": {
                        "amount": gst_penalty,
                        "rate": "10% of tax amount"
                    },
                    "interest": {
                        "amount": gst_interest,
                        "rate": "18% p.a. (1.5% per month)",
                        "months": months_delayed,
                        "calculation": f"₹{principal_amount} × 1.5% × {months_delayed} months"
                    },
                    "total_financial_liability": gst_penalty + gst_interest
                }
                
                total_liability += gst_penalty + gst_interest
                
                if days_delayed > 180:
                    penalties["criminal_prosecution"] = {
                        "severity": "Criminal offense",
                        "penalty": "Imprisonment up to 6 months + ₹1,00,000 fine",
                        "applies_when": "Persistent non-payment or fraudulent evasion"
                    }
        
        # CORPORATE LAW VIOLATIONS
        elif "corporate" in violation_type.lower() or "mca" in violation_type.lower():
            breakdown["violation_category"] = "Corporate Law"
            
            if "late_filing" in violation_type.lower():
                # MCA late filing penalties vary by document
                penalty_amount = {
                    "director_report": 5000,
                    "financial_statements": 5000,
                    "annual_return": 25000
                }
                
                default_amount = penalty_amount.get(applicable_law, 5000)
                
                penalties["mca_late_filing"] = {
                    "name": "Late MCA Filing Penalty",
                    "amount": default_amount,
                    "applicability": f"Late filing of {applicable_law}",
                    "criminal_prosecution_possible": True
                }
                total_liability += default_amount
            
            elif "director_disqualification" in violation_type.lower():
                penalties["director_disqualification"] = {
                    "name": "Director Disqualification",
                    "period": "6 months to 5 years or permanent",
                    "financial_impact": "Loss of salary/directorship income",
                    "severity": "High"
                }
        
        # Build compound interest scenario
        compound_scenario = _calculate_compound_scenario(
            principal_amount,
            interest_rate=0.01 if "gst" not in violation_type.lower() else 0.015,
            months=months_delayed if 'months_delayed' in locals() else 12
        )
        
        return {
            "success": True,
            "violation_type": violation_type,
            "breakdown": breakdown,
            "penalties": penalties,
            "interest_calculation": {
                "total_interest": interest_amount,
                "compound_scenario": compound_scenario
            },
            "total_financial_liability": {
                "principal": principal_amount,
                "penalties": sum(p.get("amount", p.get("penalty", {}).get("amount", 0)) for p in penalties.values() if isinstance(p, dict)),
                "interest": interest_amount,
                "total": total_liability
            },
            "liability_breakdown": _generate_liability_breakdown(total_liability, principal_amount),
            "recommendations": _generate_penalty_recommendations(violation_type, total_liability),
            "next_steps": _generate_next_steps(violation_type)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _calculate_compound_scenario(principal: float, interest_rate: float, months: int) -> Dict:
    """Calculate compound interest scenario"""
    
    # Simple interest
    simple = principal * interest_rate * months
    
    # Compound monthly
    monthly_rate = interest_rate
    compound = principal * ((1 + monthly_rate) ** months - 1)
    
    scenario_months = [3, 6, 12, 24]
    scenarios = []
    
    for m in scenario_months:
        simple_amt = principal * interest_rate * m
        compound_amt = principal * ((1 + monthly_rate) ** m - 1)
        scenarios.append({
            "months": m,
            "simple_interest": round(simple_amt, 2),
            "compound_interest": round(compound_amt, 2),
            "total_with_compound": round(principal + compound_amt, 2)
        })
    
    return {
        "interest_rate": f"{interest_rate * 100}% per month",
        "simple_interest_total": round(simple, 2),
        "compound_interest_total": round(compound, 2),
        "scenarios": scenarios,
        "note": "Compound interest is typically used for GST, simple for income tax"
    }

def _generate_liability_breakdown(total: float, principal: float) -> Dict:
    """Generate a breakdown of liability composition"""
    penalty_portion = total - principal
    
    return {
        "principal_percentage": round((principal / total) * 100, 2) if total > 0 else 0,
        "penalty_interest_percentage": round((penalty_portion / total) * 100, 2) if total > 0 else 0,
        "message": f"Additional ₹{penalty_portion} added to original amount"
    }

def _generate_penalty_recommendations(violation_type: str, total_liability: float) -> List[str]:
    """Generate recommendations for penalty management"""
    recommendations = []
    
    if total_liability > 100000:
        recommendations.append("URGENT: Consider legal representation to explore penalties waiver options")
    
    if "criminal" in violation_type.lower():
        recommendations.append("Consult criminal law expert immediately - potential imprisonment")
    
    recommendations.extend([
        "Immediately rectify the non-compliance to stop further penalties",
        "Maintain detailed documentation and communication with authorities",
        "Explore statutory relief provisions available under applicable law",
        "File representation/appeal if amount seems excessive"
    ])
    
    return recommendations

def _generate_next_steps(violation_type: str) -> List[str]:
    """Generate specific next steps based on violation"""
    steps = [
        "Quantify exact liability with professional help",
        "Assess payment options and installment possibilities"
    ]
    
    if "criminal" in violation_type.lower():
        steps.insert(0, "Engage criminal lawyer for possible defense")
    
    steps.extend([
        "File any applicable representation or appeal",
        "Ensure full compliance going forward"
    ])
    
    return steps
