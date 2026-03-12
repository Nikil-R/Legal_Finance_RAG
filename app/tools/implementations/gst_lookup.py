import json
from pathlib import Path
from typing import Dict, Any, List

def lookup_gst_rate(query: str) -> Dict[str, Any]:
    """
    Look up the GST rate for a specific good or service in India.
    Supports searching by item name, category, or HSN/SAC code.
    """
    try:
        data_path = Path(__file__).parent.parent / "data" / "gst_rates.json"
        if not data_path.exists():
            return {
                "success": False,
                "error": f"GST database not found at {data_path}"
            }
            
        with open(data_path, "r", encoding="utf-8") as f:
            gst_data = json.load(f)

        query = query.lower().strip()
        results = []

        # Check if gst_data is a list of entries (new format)
        if isinstance(gst_data, list):
            for entry in gst_data:
                # 1. Check item name (supports 'item' or 'item_name')
                item_name = str(entry.get("item") or entry.get("item_name") or "").lower()
                if query in item_name or item_name in query:
                    results.append(entry)
                    continue
                
                # 2. Check category
                category = str(entry.get("category", "")).lower()
                if query in category:
                    results.append(entry)
                    continue
                    
                # 3. Check HSN/SAC (supports 'hsn_sac', 'hsn_code', 'hsn', 'sac')
                hsn_sac = str(entry.get("hsn_sac") or entry.get("hsn_code") or entry.get("hsn") or entry.get("sac") or "").lower()
                if query in hsn_sac and query != "":
                    results.append(entry)
                    continue
                
                # 4. Check description
                description = str(entry.get("description", "")).lower()
                if query in description:
                    results.append(entry)
                    continue

        if not results:
            return {
                "found": False,
                "query": query,
                "message": f"No matching GST rate found for '{query}'. Please try a more specific item name or HSN code."
            }

        # Format results (normalize field names for the response)
        formatted_results = []
        for res in results:
            rate = float(res.get("gst_rate") or res.get("rate") or 0)
            formatted_results.append({
                "item": res.get("item") or res.get("item_name") or "Unknown Product",
                "category": res.get("category", "General"),
                "rate": rate,
                "rate_formatted": f"{rate:g}%",
                "hsn_sac": res.get("hsn_sac") or res.get("hsn_code") or res.get("hsn") or res.get("sac") or "N/A",
                "description": res.get("description", ""),
                "note": res.get("notes") or res.get("note", ""),
                "igst": rate,
                "cgst": rate / 2,
                "sgst": rate / 2
            })

        # Deduplicate results if necessary (e.g., if multiple matches for same item)
        seen_items = set()
        final_results = []
        for res in formatted_results:
            key = f"{res['item']}_{res['rate']}_{res['hsn_sac']}"
            if key not in seen_items:
                final_results.append(res)
                seen_items.add(key)

        return {
            "success": True,
            "found": True,
            "results": final_results[:10], # Limit to top 10 matches
            "query": query,
            "disclaimer": "Rates as per GST Council notifications. Always verify with official GST portal (cbic-gst.gov.in) for critical compliance."
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Error looking up GST rate: {str(e)}",
            "traceback": traceback.format_exc()
        }
