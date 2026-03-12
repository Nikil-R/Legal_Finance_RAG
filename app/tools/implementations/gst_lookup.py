import json
from pathlib import Path
from typing import Dict, Any, List

def lookup_gst_rate(query: str) -> Dict[str, Any]:
    """
    Look up the GST rate for a specific good or service in India.
    """
    data_path = Path(__file__).parent.parent / "data" / "gst_rates.json"
    with open(data_path, "r") as f:
        gst_data = json.load(f)

    query = query.lower().strip()
    results = []

    for category in gst_data:
        # Check if query matches category name
        if query in category["category"].lower():
            results.append(category)
            continue
            
        # Check if matches HSN/SAC
        if "hsn" in category and query in category["hsn"].lower():
            results.append(category)
            continue
        if "sac" in category and query in category["sac"].lower():
            results.append(category)
            continue

        # Check items in category
        for item in category["items"]:
            if query in item.lower() or item.lower() in query:
                results.append(category)
                break

    if not results:
        return {
            "found": False,
            "query": query,
            "message": "No matching GST rate found. Please provide more specific details."
        }

    # Format results
    formatted_results = []
    for res in results:
        formatted_results.append({
            "category": res["category"],
            "rate": res["rate"],
            "rate_formatted": f"{res['rate']}%",
            "hsn_sac": res.get("hsn", res.get("sac")),
            "note": res.get("note", ""),
            "igst": res["rate"],
            "cgst": res["rate"] / 2,
            "sgst": res["rate"] / 2
        })

    return {
        "found": True,
        "results": formatted_results,
        "query": query,
        "disclaimer": "Rates as per GST Council. Verify with official GST portal for specific cases."
    }
