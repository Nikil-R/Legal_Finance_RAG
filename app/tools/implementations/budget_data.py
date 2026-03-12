import json
from pathlib import Path
from typing import Dict, Any, List, Optional

def lookup_budget_data(
    metric: str,
    years: List[str] = None,
    estimate_type: str = "BE"
) -> Dict[str, Any]:
    """
    Look up specific Indian Union Budget figures and compare across years.
    """
    if years is None:
        years = ["2026-27"]

    data_path = Path(__file__).parent.parent / "data" / "budget_figures.json"
    with open(data_path, "r") as f:
        budget_data = json.load(f)

    results = {}
    found_any = False

    for year in years:
        if year in budget_data:
            year_data = budget_data[year]
            if metric in year_data:
                results[year] = {
                    "value": year_data[metric].get("value_formatted"),
                    "as_percent_gdp": year_data[metric].get("as_percent_gdp"),
                    "as_percent": year_data[metric].get("value_percent"),
                    "estimate_type": year_data.get("estimate_type", estimate_type)
                }
                found_any = True

    if not found_any:
        return {
            "success": False,
            "message": f"No data found for metric '{metric}' in the requested years."
        }

    # If multiple years, perform comparison
    comparison = None
    change = None
    if len(years) >= 2 and all(y in results for y in years[:2]):
        y1, y2 = years[0], years[1]
        v1_raw = budget_data[y1][metric].get("value_crore")
        v2_raw = budget_data[y2][metric].get("value_crore")
        
        if v1_raw and v2_raw:
            diff = v1_raw - v2_raw
            pct_change = (diff / v2_raw) * 100
            
            comparison = {
                y1: results[y1],
                y2: results[y2]
            }
            change = {
                "absolute": f"₹{abs(diff):,} crore {'increase' if diff > 0 else 'decrease'}",
                "percentage": f"{abs(pct_change):.2f}% {'increase' if diff > 0 else 'decrease'}"
            }

    return {
        "success": True,
        "metric": metric,
        "years": results,
        "comparison": comparison,
        "change": change
    }
