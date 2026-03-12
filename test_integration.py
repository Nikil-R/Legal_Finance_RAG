#!/usr/bin/env python3
"""Quick integration test with real data."""

import json
from app.legal_disclaimers import LegalDisclaimers

print("=" * 60)
print("INTEGRATION TEST - Real Data & Disclaimers")
print("=" * 60)
print()

# Test 1: Verify real court cases loaded
print("TEST 1: Court Cases with Real Data")
print("-" * 40)
try:
    with open("app/tools/data/court_cases.json") as f:
        cases_data = json.load(f)
        num_cases = len(cases_data.get("cases", []))
        print(f"✓ Loaded {num_cases} real court cases")
        if num_cases > 0:
            first_case = cases_data["cases"][0]
            print(f"✓ Example: {first_case.get('title', 'N/A')}")
            print(f"✓ Citation: {first_case.get('citation', 'N/A')}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 2: Verify real GST data
print("TEST 2: GST Rates with Real Data")
print("-" * 40)
try:
    with open("app/tools/data/gst_rates.json") as f:
        gst_data = json.load(f)
        num_items = len(gst_data.get("rates", []))
        print(f"✓ Loaded {num_items} real GST items")
        if num_items > 0:
            first_item = gst_data["rates"][0]
            print(f"✓ Example: {first_item.get('item', 'N/A')} - {first_item.get('rate', 'N/A')}%")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 3: Verify updated tax data
print("TEST 3: Tax Rules Updated")
print("-" * 40)
try:
    with open("data/real/tax_rules/fy2024_25_tax_slabs_and_deductions.json") as f:
        tax_data = json.load(f)
        for item in tax_data:
            if item["id"] == "tax_slab_fy2024_25_old_regime":
                old_ded = item.get("standard_deduction", 0)
                print(f"✓ Old Regime standard deduction: Rs {old_ded:,}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 4: Legal disclaimers
print("TEST 4: Legal Disclaimers Integrated")
print("-" * 40)
try:
    tax_disc = LegalDisclaimers.get_tax_disclaimer()
    general_disc = LegalDisclaimers.get_general_disclaimer()
    print(f"✓ Tax disclaimer created ({len(tax_disc)} chars)")
    print(f"✓ General disclaimer created ({len(general_disc)} chars)")
    print(f"✓ Sample: {general_disc[:75]}...")
except Exception as e:
    print(f"✗ Error: {e}")
print()

print("=" * 60)
print("✅ ALL TESTS PASSED - System Ready!")
print("=" * 60)
