import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

def calculate_income_tax(
    income: float,
    regime: str = "new",
    age_group: str = "below_60",
    deductions: float = 0.0,
    section_80c: Optional[float] = None,
    section_80d: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate Indian income tax liability for a given annual income for FY 2026-27.
    Supports deductions primarily for the Old Regime.
    """
    if income <= 0:
        return {"success": False, "error": "Income must be positive"}

    # Map generic deductions if specific ones aren't provided
    if section_80c is None:
        section_80c = deductions
    
    # 80C is capped at 1.5L
    applied_80c = min(float(section_80c or 0), 150000.0)
    applied_80d = float(section_80d or 0)
    
    total_provided_deductions = applied_80c + applied_80d

    # Load slab data
    data_path = Path(__file__).parent.parent / "data" / "tax_slabs_2026.json"
    with open(data_path, "r") as f:
        data = json.load(f)["fy_2026_27"]

    standard_deduction = 0
    slabs = []
    rebate_limit = 0
    applied_regime_deductions = 0

    if regime == "new":
        regime_data = data["new_regime"]
        standard_deduction = regime_data["standard_deduction"]
        slabs = regime_data["slabs"]
        rebate_limit = regime_data["rebate_87a_limit"]
        applied_regime_deductions = standard_deduction # New regime generally doesn't allow 80C/80D
    else:
        regime_data = data["old_regime"]
        standard_deduction = regime_data["standard_deduction"]
        # Select slabs based on age group
        if age_group not in regime_data["slabs"]:
            age_group = "below_60"
        slabs = regime_data["slabs"][age_group]
        rebate_limit = regime_data["rebate_87a_limit"]
        applied_regime_deductions = standard_deduction + total_provided_deductions

    taxable_income = max(0.0, income - applied_regime_deductions)
    tax_before_cess = 0.0
    slab_breakdown = []
    
    # Calculate tax based on slabs
    remaining_income = float(taxable_income)
    previous_limit_val: float = 0.0
    
    for slab in slabs:
        limit = slab.get("limit")
        rate = float(slab.get("rate", 0.0))
        
        if limit is None:
            # Last slab
            taxable_amount = remaining_income
            slab_text = f"Above ₹{previous_limit_val/100000.0:g}L"
        else:
            limit_val = float(limit)
            slab_range = limit_val - previous_limit_val
            taxable_amount = min(remaining_income, slab_range)
            slab_text = f"₹{previous_limit_val/100000.0:g}L - ₹{limit_val/100000.0:g}L"
            
        tax_on_slab = max(0.0, taxable_amount * rate)
        tax_before_cess += tax_on_slab
        
        slab_breakdown.append({
            "slab": slab_text,
            "rate": f"{int(rate * 100)}%",
            "taxable_amount": taxable_amount,
            "tax": tax_on_slab
        })
        
        remaining_income -= taxable_amount
        if limit is not None:
            previous_limit_val = float(limit)
            
        if remaining_income <= 0:
            break

    # Rebate u/s 87A
    rebate_applied = False
    if taxable_income <= rebate_limit:
        tax_before_cess = 0.0
        rebate_applied = True
        # Zero out slab taxes if rebate applies
        for item in slab_breakdown:
            item["tax"] = 0.0
    
    # Marginal Relief could be added here, but skipping for simplicity unless requested

    # Surcharge
    surcharge_amount = 0.0
    for s_slab in data.get("surcharge", []):
        s_limit = s_slab.get("limit")
        s_rate = float(s_slab.get("rate", 0.0))
        if s_limit is None or taxable_income < float(s_limit):
            surcharge_amount = tax_before_cess * s_rate
            break
            
    # Cess
    cess_amount = (tax_before_cess + surcharge_amount) * float(data.get("cess_rate", 0.04))
    total_tax = tax_before_cess + surcharge_amount + cess_amount
    
    effective_rate = (float(total_tax) / float(income) * 100.0) if income > 0 else 0.0

    result: Dict[str, Any] = {
        "success": True,
        "regime": str(regime),
        "gross_income": float(income),
        "deductions_applied": float(applied_regime_deductions),
        "taxable_income": float(taxable_income),
        "tax_before_cess": float(tax_before_cess),
        "surcharge": float(surcharge_amount),
        "cess": float(cess_amount),
        "total_tax": round(float(total_tax), 2),
        "effective_rate": f"{effective_rate:.2f}%",
        "slab_breakdown": slab_breakdown,
        "rebate_applied": bool(rebate_applied),
        "note": f"Tax calculated under {str(regime).capitalize()} Regime for FY 2026-27."
    }
    
    if regime == "new" and total_provided_deductions > 0:
        current_note = str(result.get("note", ""))
        result["note"] = current_note + " Warning: 80C/80D deductions are usually not allowed in New Regime."

    return result
