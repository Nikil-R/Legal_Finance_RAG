import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

def calculate_income_tax(
    income: float,
    regime: str = "new",
    age_group: str = "below_60"
) -> Dict[str, Any]:
    """
    Calculate Indian income tax liability for a given annual income for FY 2026-27.
    """
    if income <= 0:
        return {"success": False, "error": "Income must be positive"}

    # Load slab data
    data_path = Path(__file__).parent.parent / "data" / "tax_slabs_2026.json"
    with open(data_path, "r") as f:
        data = json.load(f)["fy_2026_27"]

    standard_deduction = 0
    slabs = []
    rebate_limit = 0

    if regime == "new":
        regime_data = data["new_regime"]
        standard_deduction = regime_data["standard_deduction"]
        slabs = regime_data["slabs"]
        rebate_limit = regime_data["rebate_87a_limit"]
    else:
        regime_data = data["old_regime"]
        standard_deduction = regime_data["standard_deduction"]
        # Select slabs based on age group
        if age_group not in regime_data["slabs"]:
            age_group = "below_60"
        slabs = regime_data["slabs"][age_group]
        rebate_limit = regime_data["rebate_87a_limit"]

    taxable_income = max(0, income - standard_deduction)
    tax_before_cess = 0
    slab_breakdown = []
    
    # Calculate tax based on slabs
    remaining_income = taxable_income
    previous_limit = 0
    
    for slab in slabs:
        limit = slab["limit"]
        rate = slab["rate"]
        
        if limit is None:
            # Last slab
            taxable_amount = remaining_income
            slab_text = f"Above ₹{previous_limit/100000:g}L"
        else:
            slab_range = limit - previous_limit
            taxable_amount = min(remaining_income, slab_range)
            slab_text = f"₹{previous_limit/100000:g}L - ₹{limit/100000:g}L"
            
        tax_on_slab = max(0, taxable_amount * rate)
        tax_before_cess += tax_on_slab
        
        slab_breakdown.append({
            "slab": slab_text,
            "rate": f"{int(rate * 100)}%",
            "taxable_amount": taxable_amount,
            "tax": tax_on_slab
        })
        
        remaining_income -= taxable_amount
        previous_limit = limit
        if remaining_income <= 0:
            break

    # Rebate u/s 87A
    rebate_applied = False
    if taxable_income <= rebate_limit:
        tax_before_cess = 0
        rebate_applied = True
        # Zero out slab taxes if rebate applies
        for item in slab_breakdown:
            item["tax"] = 0

    # Surcharge
    surcharge_amount = 0
    for s_slab in data["surcharge"]:
        s_limit = s_slab["limit"]
        s_rate = s_slab["rate"]
        if s_limit is None or taxable_income < s_limit:
            surcharge_amount = tax_before_cess * s_rate
            break
            
    # Cess
    cess_amount = (tax_before_cess + surcharge_amount) * data["cess_rate"]
    total_tax = tax_before_cess + surcharge_amount + cess_amount
    
    effective_rate = (total_tax / income * 100) if income > 0 else 0

    return {
        "success": True,
        "regime": regime,
        "gross_income": income,
        "standard_deduction": standard_deduction,
        "taxable_income": taxable_income,
        "tax_before_cess": tax_before_cess,
        "surcharge": surcharge_amount,
        "cess": cess_amount,
        "total_tax": round(total_tax, 2),
        "effective_rate": f"{effective_rate:.2f}%",
        "slab_breakdown": slab_breakdown,
        "rebate_applied": rebate_applied,
        "note": f"Tax calculated under {regime.capitalize()} Regime for FY 2026-27"
    }
