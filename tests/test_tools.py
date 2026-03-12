from app.tools import ToolExecutor, ToolRegistry
from app.tools.implementations import (
    calculate_income_tax,
    lookup_budget_data,
    lookup_gst_rate,
)


def test_tax_calculator():
    # Test ₹8L (No tax in new regime with rebate)
    res = calculate_income_tax(income=800000, regime="new")
    assert res["success"] is True
    assert res["total_tax"] == 0
    assert res["rebate_applied"] is True

    # Test ₹15L in new regime
    res = calculate_income_tax(income=1500000, regime="new")
    assert res["success"] is True
    assert res["total_tax"] > 0
    assert "10%" in [s["rate"] for s in res["slab_breakdown"]]

def test_gst_lookup():
    # Test category search
    res = lookup_gst_rate(query="restaurant")
    assert res["found"] is True
    assert any(r["rate"] == 5 for r in res["results"])

    # Test HSN search
    res = lookup_gst_rate(query="7113") # Gold
    assert res["found"] is True
    assert res["results"][0]["rate"] == 3

def test_budget_data():
    # Test single year metric
    res = lookup_budget_data(metric="fiscal_deficit", years=["2026-27"])
    assert res["success"] is True
    assert "2026-27" in res["years"]
    assert res["years"]["2026-27"]["as_percent_gdp"] == 4.3

    # Test comparison
    res = lookup_budget_data(metric="capital_expenditure", years=["2026-27", "2025-26"])
    assert res["success"] is True
    assert res["comparison"] is not None
    assert res["change"] is not None

def test_tool_registry():
    registry = ToolRegistry()
    definitions = registry.get_tool_definitions()
    assert len(definitions) >= 5
    names = [d["function"]["name"] for d in definitions]
    assert "calculate_income_tax" in names
    assert "search_legal_documents" in names

def test_tool_executor():
    registry = ToolRegistry()
    executor = ToolExecutor(registry)
    
    # ₹10L under new regime = zero tax (87A rebate)
    res = executor.execute("calculate_income_tax", {"income": 1000000})
    assert res["success"] is True
    assert res["result"]["total_tax"] == 0  # Rebate applies
    
    # ₹20L under new regime = tax > 0 (above rebate limit)
    res2 = executor.execute("calculate_income_tax", {"income": 2000000})
    assert res2["success"] is True
    assert res2["result"]["total_tax"] > 0  # No rebate at this level
    
    # Invalid tool
    res = executor.execute("non_existent_tool", {})
    assert res["success"] is False
    assert "not found" in res["error"].lower()
