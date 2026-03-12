try:
    from app.tools.executor import ToolExecutor
    print("Imported ToolExecutor")
    from app.tools.implementations.budget_data import lookup_budget_data
    print("Imported lookup_budget_data")
    from app.tools.implementations.gst_lookup import lookup_gst_rate
    print("Imported lookup_gst_rate")
    from app.tools.implementations.tax_calculator import calculate_income_tax
    print("Imported calculate_income_tax")
    from app.tools.registry import ToolRegistry
    print("Imported ToolRegistry")
    print("SUCCESS: All imports worked!")
except Exception as e:
    print(f"FAILURE: {e}")
