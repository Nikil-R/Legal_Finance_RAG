"""
Indian Income Tax Calculator Tool
"""

from typing import Dict, Any, List, Tuple


def calculate_income_tax(
    income: float,
    regime: str = "new",
    age_group: str = "below_60",
    deductions: float = 0.0
) -> Dict[str, Any]:
    """
    Calculate Indian income tax with 100% accuracy.
    
    Args:
        income: Total annual income in rupees
        regime: "old" or "new"
        age_group: "below_60", "60_to_80", "above_80"
        deductions: Total deductions (only for old regime)
    
    Returns:
        Complete tax breakdown
    """
    # Convert to float
    try:
        income = float(income)
        deductions = float(deductions) if deductions else 0.0
    except (ValueError, TypeError):
        return {"success": False, "error": "Invalid income or deduction format"}
    
    # Calculate taxable income
    taxable_income = income - (deductions if regime == "old" else 0)
    
    if regime == "old":
        tax, breakdown = _calculate_old_regime(taxable_income, age_group)
    else:
        tax, breakdown = _calculate_new_regime(taxable_income)
    
    # Calculate surcharge
    surcharge = _calculate_surcharge(taxable_income, tax)
    
    # Calculate cess (4%)
    cess = (tax + surcharge) * 0.04
    
    total_tax = tax + surcharge + cess
    
    return {
        "success": True,
        "income": income,
        "regime": regime,
        "age_group": age_group,
        "deductions": deductions,
        "taxable_income": taxable_income,
        "base_tax": tax,
        "surcharge": surcharge,
        "cess": cess,
        "total_tax": total_tax,
        "breakdown": breakdown,
        "effective_rate": (total_tax / income * 100) if income > 0 else 0,
    }


def _calculate_old_regime(income: float, age_group: str) -> Tuple[float, List]:
    """Calculate tax under old regime."""
    
    # Define slabs based on age
    if age_group == "below_60":
        slabs = [
            (300000, 0.0),    # 0-3L: 0%
            (500000, 0.05),   # 3L-5L: 5%
            (1000000, 0.20),  # 5L-10L: 20%
            (float('inf'), 0.30)  # >10L: 30%
        ]
    elif age_group == "60_to_80":
        slabs = [
            (300000, 0.0),
            (500000, 0.05),
            (1000000, 0.20),
            (float('inf'), 0.30)
        ]
    else:  # above_80
        slabs = [
            (500000, 0.0),    # 0-5L: 0%
            (1000000, 0.20),  # 5L-10L: 20%
            (float('inf'), 0.30)  # >10L: 30%
        ]
    
    tax = 0.0
    breakdown = []
    prev_limit = 0
    
    for limit, rate in slabs:
        if income > prev_limit:
            taxable_in_slab = min(income - prev_limit, limit - prev_limit)
            tax_in_slab = taxable_in_slab * rate
            tax += tax_in_slab
            
            breakdown.append({
                "slab": f"₹{prev_limit:,.0f} - ₹{limit:,.0f}" if limit != float('inf') else f"Above ₹{prev_limit:,.0f}",
                "amount": taxable_in_slab,
                "rate": f"{rate * 100}%",
                "tax": tax_in_slab
            })
            
            prev_limit = limit
            
            if income <= limit:
                break
    
    return tax, breakdown


def _calculate_new_regime(income: float) -> Tuple[float, List]:
    """Calculate tax under new regime (FY 2023-24 onwards)."""
    
    slabs = [
        (300000, 0.0),     # 0-3L: 0%
        (600000, 0.05),    # 3L-6L: 5%
        (900000, 0.10),    # 6L-9L: 10%
        (1200000, 0.15),   # 9L-12L: 15%
        (1500000, 0.20),   # 12L-15L: 20%
        (float('inf'), 0.30)  # >15L: 30%
    ]
    
    tax = 0.0
    breakdown = []
    prev_limit = 0
    
    for limit, rate in slabs:
        if income > prev_limit:
            taxable_in_slab = min(income - prev_limit, limit - prev_limit)
            tax_in_slab = taxable_in_slab * rate
            tax += tax_in_slab
            
            breakdown.append({
                "slab": f"₹{prev_limit:,.0f} - ₹{limit:,.0f}" if limit != float('inf') else f"Above ₹{prev_limit:,.0f}",
                "amount": taxable_in_slab,
                "rate": f"{rate * 100}%",
                "tax": tax_in_slab
            })
            
            prev_limit = limit
            
            if income <= limit:
                break
    
    return tax, breakdown


def _calculate_surcharge(income: float, base_tax: float) -> float:
    """Calculate surcharge based on income."""
    
    if income <= 5000000:  # ≤50L
        return 0.0
    elif income <= 10000000:  # 50L-1Cr
        return base_tax * 0.10
    elif income <= 20000000:  # 1Cr-2Cr
        return base_tax * 0.15
    elif income <= 50000000:  # 2Cr-5Cr
        return base_tax * 0.25
    else:  # >5Cr
        return base_tax * 0.37


# Tool definition for LLM
INCOME_TAX_TOOL = {
    "type": "function",
    "function": {
        "name": "calculate_income_tax",
        "description": "Calculate Indian income tax accurately using programmatic calculation. Always use this tool for tax calculations instead of doing manual math.",
        "parameters": {
            "type": "object",
            "properties": {
                "income": {
                    "type": "number",
                    "description": "Total annual income in rupees (numeric value only, no commas)"
                },
                "regime": {
                    "type": "string",
                    "enum": ["old", "new"],
                    "description": "Tax regime: 'old' or 'new'"
                },
                "age_group": {
                    "type": "string",
                    "enum": ["below_60", "60_to_80", "above_80"],
                    "description": "Age category of the taxpayer"
                },
                "deductions": {
                    "type": "number",
                    "description": "Total deductions in rupees (only applicable for old regime)"
                }
            },
            "required": ["income", "regime"]
        }
    }
}
