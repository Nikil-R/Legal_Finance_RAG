"""
Comprehensive tests for newly added tools in the Legal Finance RAG system.
Tests cover all high-priority, medium-priority tools.
"""

import pytest
from app.tools import ToolRegistry
from app.tools.implementations.court_case_search import search_court_cases
from app.tools.implementations.compliance_checker import check_compliance
from app.tools.implementations.financial_ratio_calculator import calculate_financial_ratios
from app.tools.implementations.amendment_tracker import track_amendments
from app.tools.implementations.penalty_interest_calculator import calculate_penalties_and_interest
from app.tools.implementations.document_comparison import compare_documents


class TestCourtCaseSearch:
    """Test suite for Court Case Search Tool"""
    
    def test_search_by_citation(self):
        result = search_court_cases(query="2023 SCC 456")
        assert result["success"] is True
        assert result["results_count"] > 0
        
    def test_search_by_case_name(self):
        result = search_court_cases(query="ABC Corporation v. State")
        assert result["success"] is True
        assert len(result["cases"]) > 0
        
    def test_search_with_keywords(self):
        result = search_court_cases(
            query="income tax",
            case_keywords=["unexplained income", "deposits"]
        )
        assert result["success"] is True
        
    def test_search_by_court(self):
        result = search_court_cases(
            query="income tax",
            court_name="High Court"
        )
        assert result["success"] is True
        
    def test_search_with_date_range(self):
        result = search_court_cases(
            query="income",
            date_range={"from": "2023-01-01", "to": "2023-12-31"}
        )
        assert result["success"] is True
        
    def test_case_details_structure(self):
        result = search_court_cases(query="2023 SCC 456", num_results=1)
        assert result["success"] is True
        if result["cases"]:
            case = result["cases"][0]
            assert "citation" in case
            assert "case_name" in case
            assert "court" in case
            assert "ratio_decidendi" in case
            assert "key_principles" in case


class TestComplianceChecker:
    """Test suite for Compliance Checker Tool"""
    
    def test_sole_proprietor_compliance(self):
        result = check_compliance(business_type="sole_proprietor")
        assert result["success"] is True
        assert result["business_type"] == "sole_proprietor"
        assert "requirements" in result
        
    def test_private_limited_compliance(self):
        result = check_compliance(business_type="private_limited_company")
        assert result["success"] is True
        assert "requirements" in result
        assert "applicable_penalties" in result
        
    def test_compliance_with_industry(self):
        result = check_compliance(
            business_type="private_limited_company",
            industry_sector="pharmaceuticals"
        )
        assert result["success"] is True
        
    def test_compliance_with_state(self):
        result = check_compliance(
            business_type="private_limited_company",
            state="Maharashtra"
        )
        assert result["success"] is True
        
    def test_compliance_calendar(self):
        result = check_compliance(business_type="private_limited_company")
        assert result["success"] is True
        assert "compliance_calendar" in result
        assert isinstance(result["compliance_calendar"], list)
        
    def test_compliance_recommendations(self):
        result = check_compliance(business_type="private_limited_company")
        assert result["success"] is True
        assert "recommendations" in result
        assert len(result["recommendations"]) > 0


class TestFinancialRatioCalculator:
    """Test suite for Financial Ratio Calculator Tool"""
    
    def test_calculate_profitability_ratios(self):
        balance_sheet = {
            "current_assets": 100000,
            "current_liabilities": 50000,
            "inventory": 20000,
            "total_assets": 500000,
            "total_equity": 300000,
            "total_debt": 200000,
            "cash": 50000,
            "accounts_receivable": 30000
        }
        income_statement = {
            "revenue": 1000000,
            "gross_profit": 300000,
            "operating_income": 200000,
            "net_income": 150000,
            "cost_of_goods_sold": 700000,
            "ebit": 200000,
            "interest_expense": 10000
        }
        
        result = calculate_financial_ratios(balance_sheet, income_statement)
        assert result["success"] is True
        assert "profitability_ratios" in result["calculated_ratios"]
        
    def test_profitability_ratio_values(self):
        balance_sheet = {
            "current_assets": 100000,
            "current_liabilities": 50000,
            "total_assets": 500000,
            "total_equity": 300000,
            "total_debt": 200000,
            "cash": 50000,
            "accounts_receivable": 30000,
            "inventory": 20000
        }
        income_statement = {
            "revenue": 1000000,
            "gross_profit": 300000,
            "operating_income": 200000,
            "net_income": 100000,
            "cost_of_goods_sold": 700000,
            "ebit": 200000,
            "interest_expense": 10000
        }
        
        result = calculate_financial_ratios(balance_sheet, income_statement)
        assert result["success"] is True
        
        prof_ratios = result["calculated_ratios"]["profitability_ratios"]
        assert prof_ratios["net_profit_margin"]["value"] == 10.0
        assert prof_ratios["gross_profit_margin"]["value"] == 30.0
        
    def test_liquidity_ratios(self):
        balance_sheet = {
            "current_assets": 200000,
            "current_liabilities": 100000,
            "inventory": 40000,
            "total_assets": 500000,
            "total_equity": 300000,
            "total_debt": 200000,
            "cash": 60000,
            "accounts_receivable": 30000
        }
        income_statement = {
            "revenue": 1000000,
            "gross_profit": 300000,
            "operating_income": 200000,
            "net_income": 100000,
            "cost_of_goods_sold": 700000,
            "ebit": 200000,
            "interest_expense": 10000
        }
        
        result = calculate_financial_ratios(balance_sheet, income_statement)
        assert result["success"] is True
        assert "liquidity_ratios" in result["calculated_ratios"]
        
        liq_ratios = result["calculated_ratios"]["liquidity_ratios"]
        assert liq_ratios["current_ratio"]["value"] == 2.0
        
    def test_leverage_ratios(self):
        balance_sheet = {
            "current_assets": 100000,
            "current_liabilities": 50000,
            "total_assets": 500000,
            "total_equity": 300000,
            "total_debt": 200000,
            "cash": 50000,
            "accounts_receivable": 30000,
            "inventory": 20000
        }
        income_statement = {
            "revenue": 1000000,
            "gross_profit": 300000,
            "operating_income": 200000,
            "net_income": 100000,
            "cost_of_goods_sold": 700000,
            "ebit": 200000,
            "interest_expense": 10000
        }
        
        result = calculate_financial_ratios(balance_sheet, income_statement)
        assert result["success"] is True
        assert "leverage_ratios" in result["calculated_ratios"]
        
    def test_negative_working_capital_flag(self):
        balance_sheet = {
            "current_assets": 50000,
            "current_liabilities": 100000,
            "total_assets": 500000,
            "total_equity": 300000,
            "total_debt": 200000,
            "cash": 20000,
            "accounts_receivable": 10000,
            "inventory": 20000
        }
        income_statement = {
            "revenue": 1000000,
            "gross_profit": 300000,
            "operating_income": 200000,
            "net_income": 100000,
            "cost_of_goods_sold": 700000,
            "ebit": 200000,
            "interest_expense": 10000
        }
        
        result = calculate_financial_ratios(balance_sheet, income_statement)
        assert result["success"] is True
        assert len(result["critical_flags"]) > 0
        assert any("negative" in flag.lower() for flag in result["critical_flags"])


class TestAmendmentTracker:
    """Test suite for Amendment Tracker Tool"""
    
    def test_track_all_amendments(self):
        result = track_amendments()
        assert result["success"] is True
        assert "amendments" in result
        
    def test_track_by_act(self):
        result = track_amendments(act_name="Income Tax Act")
        assert result["success"] is True
        
    def test_track_by_amendment_type(self):
        result = track_amendments(amendment_type="Finance Act")
        assert result["success"] is True
        
    def test_amendment_details_structure(self):
        result = track_amendments(num_results=1)
        assert result["success"] is True
        if result["amendments"]:
            amendment = result["amendments"][0]
            assert "title" in amendment
            assert "act" in amendment
            assert "effective_date" in amendment
            assert "comparison" in amendment
            assert "impact_analysis" in amendment
            
    def test_amendment_timeline(self):
        result = track_amendments()
        assert result["success"] is True
        assert "timeline" in result
        
    def test_compliance_impact_assessment(self):
        result = track_amendments()
        assert result["success"] is True
        assert "compliance_impact" in result


class TestPenaltyInterestCalculator:
    """Test suite for Penalty and Interest Calculator Tool"""
    
    def test_late_income_tax_filing(self):
        result = calculate_penalties_and_interest(
            violation_type="income_tax_return_filing",
            violation_details={
                "principal_amount": 50000,
                "days_delayed": 60,
                "applicable_law": "Section 271F",
                "entity_type": "individual"
            }
        )
        assert result["success"] is True
        assert "penalties" in result
        
    def test_gst_late_payment(self):
        result = calculate_penalties_and_interest(
            violation_type="gst_non_payment",
            violation_details={
                "principal_amount": 100000,
                "days_delayed": 90,
                "applicable_law": "GST Act",
                "entity_type": "business"
            }
        )
        assert result["success"] is True
        assert result["total_financial_liability"]["total"] > result["total_financial_liability"]["principal"]
        
    def test_corporate_filing_penalty(self):
        result = calculate_penalties_and_interest(
            violation_type="corporate_late_filing",
            violation_details={
                "principal_amount": 0,
                "days_delayed": 30,
                "applicable_law": "director_report",
                "entity_type": "private_limited_company"
            }
        )
        assert result["success"] is True
        
    def test_penalty_breakdown(self):
        result = calculate_penalties_and_interest(
            violation_type="gst_non_payment",
            violation_details={
                "principal_amount": 100000,
                "days_delayed": 60,
                "applicable_law": "GST Act",
                "entity_type": "business"
            }
        )
        assert result["success"] is True
        assert "total_financial_liability" in result
        assert "violation_type" in result
        
    def test_compound_interest_calculation(self):
        result = calculate_penalties_and_interest(
            violation_type="gst_non_payment",
            violation_details={
                "principal_amount": 100000,
                "days_delayed": 180,
                "applicable_law": "GST Act",
                "entity_type": "business"
            }
        )
        assert result["success"] is True
        assert "interest_calculation" in result


class TestDocumentComparison:
    """Test suite for Multi-Document Comparison Tool"""
    
    def test_compare_two_documents(self):
        documents = [
            {
                "name": "Contract v1",
                "content": "This is a contract with termination clause and liability limitations. All rights reserved.",
                "version": "1.0",
                "date": "2024-01-01"
            },
            {
                "name": "Contract v2",
                "content": "This is an updated contract with enhanced termination clause and expanded liability limitations. All rights reserved.",
                "version": "2.0",
                "date": "2024-06-01"
            }
        ]
        
        result = compare_documents(documents)
        assert result["success"] is True
        assert result["document_count"] == 2
        
    def test_comparison_includes_differences(self):
        documents = [
            {
                "name": "Doc A",
                "content": "Payment terms are 30 days net",
                "version": "1.0",
                "date": "2024-01-01"
            },
            {
                "name": "Doc B",
                "content": "Payment terms are 45 days net with 2% discount",
                "version": "1.0",
                "date": "2024-06-01"
            }
        ]
        
        result = compare_documents(documents)
        assert result["success"] is True
        assert "provision_differences" in result["comparison_results"]
        
    def test_clause_analysis(self):
        documents = [
            {
                "name": "Agreement 1",
                "content": "Termination clause: Either party may terminate with 30 days notice. Liability limited to contract value. Governing law is Indian law.",
                "version": "1.0",
                "date": "2024-01-01"
            },
            {
                "name": "Agreement 2",
                "content": "Termination clause: Either party may terminate with 60 days notice. Liability limited to twice contract value. Governing law is Singapore law.",
                "version": "2.0",
                "date": "2024-06-01"
            }
        ]
        
        result = compare_documents(documents, comparison_types=["clauses"])
        assert result["success"] is True
        
    def test_conflict_identification(self):
        documents = [
            {
                "name": "Contract Version 1",
                "content": "Governing Law: Indian Law. Jurisdiction: Delhi High Court",
                "version": "1.0",
                "date": "2024-01-01"
            },
            {
                "name": "Contract Version 2",
                "content": "Governing Law: Singapore Law. Jurisdiction: Singapore Court",
                "version": "2.0",
                "date": "2024-06-01"
            }
        ]
        
        result = compare_documents(documents)
        assert result["success"] is True
        assert "conflicting_provisions" in result["comparison_results"]
        
    def test_side_by_side_comparison(self):
        documents = [
            {
                "name": "Old Policy",
                "content": "Copay: ₹500 per visit. Deductible: ₹1000",
                "version": "1.0",
                "date": "2024-01-01"
            },
            {
                "name": "New Policy",
                "content": "Copay: ₹300 per visit. Deductible: ₹500",
                "version": "2.0",
                "date": "2024-06-01"
            }
        ]
        
        result = compare_documents(documents)
        assert result["success"] is True
        assert "side_by_side" in result


class TestToolRegistry:
    """Test suite for updated Tool Registry with new tools"""
    
    def test_all_tools_registered(self):
        registry = ToolRegistry()
        definitions = registry.get_tool_definitions()
        tool_names = [d["function"]["name"] for d in definitions]
        
        # Check original tools
        assert "calculate_income_tax" in tool_names
        assert "lookup_gst_rate" in tool_names
        
        # Check new high-priority tools
        assert "search_court_cases" in tool_names
        assert "check_compliance" in tool_names
        assert "calculate_financial_ratios" in tool_names
        
        # Check new medium-priority tools
        assert "track_amendments" in tool_names
        assert "calculate_penalties_and_interest" in tool_names
        assert "compare_documents" in tool_names
        
    def test_tool_count(self):
        registry = ToolRegistry()
        tools = registry.list_tools()
        assert len(tools) >= 11  # 5 original + 6 new tools
        
    def test_tool_function_retrieval(self):
        registry = ToolRegistry()
        
        func = registry.get_tool_function("search_court_cases")
        assert callable(func)
        
        func = registry.get_tool_function("check_compliance")
        assert callable(func)
        
    def test_invalid_tool_raises_error(self):
        registry = ToolRegistry()
        with pytest.raises(ValueError):
            registry.get_tool_function("non_existent_tool")


class TestToolExecutor:
    """Test suite for Tool Executor with new tools"""
    
    def test_executor_can_execute_new_tools(self):
        from app.tools import ToolExecutor
        
        registry = ToolRegistry()
        executor = ToolExecutor(registry)
        
        result = executor.execute(
            "check_compliance",
            {"business_type": "sole_proprietor"}
        )
        assert result["success"] is True
        
    def test_compliance_tool_execution(self):
        from app.tools import ToolExecutor
        
        registry = ToolRegistry()
        executor = ToolExecutor(registry)
        
        result = executor.execute(
            "search_court_cases",
            {"query": "income tax"}
        )
        assert result["success"] is True
        assert "tool" in result
        assert result["tool"] == "search_court_cases"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
