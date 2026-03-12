from typing import Dict, Any, List, Callable
from app.tools.schemas import GroqTool, GroqToolFunction

# Import tool implementations
from app.tools.implementations.tax_calculator import calculate_income_tax
from app.tools.implementations.gst_lookup import lookup_gst_rate
from app.tools.implementations.budget_data import lookup_budget_data
from app.tools.implementations.document_search import search_legal_documents
from app.tools.implementations.section_lookup import lookup_act_section
# New high-priority tools
from app.tools.implementations.court_case_search import search_court_cases
from app.tools.implementations.compliance_checker import check_compliance
from app.tools.implementations.financial_ratio_calculator import calculate_financial_ratios
# New medium-priority tools
from app.tools.implementations.amendment_tracker import track_amendments
from app.tools.implementations.penalty_interest_calculator import calculate_penalties_and_interest
from app.tools.implementations.document_comparison import compare_documents

class ToolRegistry:
    """Manages all available tools for LLM tool calling."""
    
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], required: List[str], func: Callable):
        self._tools[name] = {
            "definition": GroqTool(
                function=GroqToolFunction(
                    name=name,
                    description=description,
                    parameters={
                        "type": "object",
                        "properties": parameters,
                        "required": required
                    }
                )
            ).model_dump(),
            "function": func
        }

    def _register_default_tools(self):
        # 1. Tax Calculator
        self.register_tool(
            name="calculate_income_tax",
            description="Calculate Indian income tax liability for a given annual income under the Old or New tax regime for FY 2026-27. Use this when the user asks how much tax they need to pay or wants a tax calculation.",
            parameters={
                "income": {
                    "type": "number",
                    "description": "Annual gross taxable income in INR"
                },
                "regime": {
                    "type": "string",
                    "enum": ["old", "new"],
                    "description": "Tax regime - 'old' for the old regime with deductions, 'new' for the new simplified regime",
                    "default": "new"
                },
                "age_group": {
                    "type": "string",
                    "enum": ["below_60", "60_to_80", "above_80"],
                    "description": "Age category of the taxpayer",
                    "default": "below_60"
                },
                "deductions": {
                    "type": "number",
                    "description": "Total tax-saving deductions (Section 80C, 80D, etc.) mainly for Old Regime. Standard deduction is automatically applied.",
                    "default": 0.0
                }
            },
            required=["income"],
            func=calculate_income_tax
        )

        # 2. GST Lookup
        self.register_tool(
            name="lookup_gst_rate",
            description="Look up the GST (Goods and Services Tax) rate for a specific good or service in India. Use this when the user asks about GST rates or HSN/SAC codes.",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Name of the good or service, or HSN/SAC code."
                }
            },
            required=["query"],
            func=lookup_gst_rate
        )

        # 3. Budget Data Lookup
        self.register_tool(
            name="lookup_budget_data",
            description="Look up specific Indian Union Budget figures (fiscal deficit, expenditure, etc.) and compare across years. Use this for precise numbers or year-over-year comparisons.",
            parameters={
                "metric": {
                    "type": "string",
                    "description": "The budget metric to look up. Examples: 'fiscal_deficit', 'total_expenditure', 'capital_expenditure'."
                },
                "years": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Financial years to look up e.g. ['2026-27', '2025-26']"
                }
            },
            required=["metric"],
            func=lookup_budget_data
        )

        # 4. Document Search
        self.register_tool(
            name="search_legal_documents",
            description="Search through the database of Indian legal and financial documents. Use this when the user asks about specific legal provisions, budget policies, or needs information from official documents.",
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query to find relevant documents."
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of relevant document chunks to return",
                    "default": 5
                }
            },
            required=["query"],
            func=search_legal_documents
        )

        # 5. Act Section Lookup
        self.register_tool(
            name="lookup_act_section",
            description="Look up a specific section of an Indian legal or financial act (e.g., Section 80C). Use this for quick summaries of specific law sections.",
            parameters={
                "section": {
                    "type": "string",
                    "description": "Section number (e.g. '80C', '44AD')."
                },
                "act": {
                    "type": "string",
                    "description": "Name of the act.",
                    "default": "Income Tax Act"
                }
            },
            required=["section"],
            func=lookup_act_section
        )

        # ===== HIGH-PRIORITY TOOLS =====
        
        # 6. Court Case Search
        self.register_tool(
            name="search_court_cases",
            description="Search through Indian court judgments and legal precedents. Find relevant case citations, court hierarchy, judgment dates, presiding judges, key legal principles, and ratio decidendi.",
            parameters={
                "query": {
                    "type": "string",
                    "description": "Search query: case citation (e.g., '2023 SCC 456'), case name, or legal keywords"
                },
                "case_keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional keywords to filter by"
                },
                "court_name": {
                    "type": "string",
                    "description": "Filter by specific court (Supreme Court, High Court, District Court, etc.)"
                },
                "date_range": {
                    "type": "object",
                    "description": "Date range filter",
                    "properties": {
                        "from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "to": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                    }
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of cases to return",
                    "default": 5
                }
            },
            required=["query"],
            func=search_court_cases
        )

        # 7. Compliance Checker
        self.register_tool(
            name="check_compliance",
            description="Validate compliance requirements for specific business activities, industries, and regulatory frameworks. Returns applicable requirements, filing deadlines, required documentation, penalty structures, and regulatory changes.",
            parameters={
                "business_type": {
                    "type": "string",
                    "enum": ["sole_proprietor", "private_limited_company", "llp", "partnership"],
                    "description": "Type of business entity"
                },
                "industry_sector": {
                    "type": "string",
                    "description": "Industry type (e.g., 'pharmaceuticals', 'food_business', 'finance_nbfc')"
                },
                "state": {
                    "type": "string",
                    "description": "Indian state for jurisdiction-specific regulations"
                },
                "specific_acts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific acts to query"
                }
            },
            required=["business_type"],
            func=check_compliance
        )

        # 8. Financial Ratio Calculator
        self.register_tool(
            name="calculate_financial_ratios",
            description="Compute standard financial ratios from financial statements. Calculate profitability, liquidity, leverage, and efficiency ratios with contextual interpretation of financial health.",
            parameters={
                "balance_sheet": {
                    "type": "object",
                    "description": "Balance sheet items {item_name: amount}. Include: current_assets, current_liabilities, inventory, total_assets, total_equity, total_debt, cash, accounts_receivable"
                },
                "income_statement": {
                    "type": "object",
                    "description": "P&L items {item_name: amount}. Include: revenue, gross_profit, operating_income, net_income, cost_of_goods_sold, ebit, interest_expense"
                },
                "cash_flow": {
                    "type": "object",
                    "description": "Cash flow items (optional)"
                },
                "ratio_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "enum": ["profitability", "liquidity", "leverage", "efficiency"],
                    "description": "Types of ratios to calculate"
                }
            },
            required=["balance_sheet", "income_statement"],
            func=calculate_financial_ratios
        )

        # ===== MEDIUM-PRIORITY TOOLS =====
        
        # 9. Amendment Tracker
        self.register_tool(
            name="track_amendments",
            description="Track recent amendments, notifications, and circulars related to tax laws and regulations. Shows amendment details, effective dates, impact analysis, and comparison between old and new provisions.",
            parameters={
                "act_name": {
                    "type": "string",
                    "description": "Specific act name (e.g., 'Income Tax Act, 1961')"
                },
                "date_range": {
                    "type": "object",
                    "description": "Date range for amendments",
                    "properties": {
                        "from": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                        "to": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                    }
                },
                "legal_domain": {
                    "type": "string",
                    "description": "Legal domain (income_tax, gst, nbfc_rbi, corporate_law, labor_law)"
                },
                "amendment_type": {
                    "type": "string",
                    "description": "Type of amendment (Finance Act, Circular, Regulatory Notification)"
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of amendments to return",
                    "default": 10
                }
            },
            required=[],
            func=track_amendments
        )

        # 10. Penalty and Interest Calculator
        self.register_tool(
            name="calculate_penalties_and_interest",
            description="Calculate penalties, interest, and late fees for various compliance violations including late tax filing, delayed payments, and missed regulatory deadlines. Computes exact penalty amounts, interest rates, and total liability.",
            parameters={
                "violation_type": {
                    "type": "string",
                    "description": "Type of violation (tax_filing, gst_payment, corporate_filing, tds_default, etc.)"
                },
                "violation_details": {
                    "type": "object",
                    "description": "Details of violation",
                    "properties": {
                        "principal_amount": {"type": "number", "description": "Amount at stake"},
                        "days_delayed": {"type": "integer", "description": "Number of days delayed"},
                        "applicable_law": {"type": "string", "description": "Applicable law or section"},
                        "entity_type": {"type": "string", "description": "Type of entity"}
                    }
                },
                "jurisdiction": {
                    "type": "string",
                    "enum": ["federal", "state"],
                    "description": "Jurisdiction level",
                    "default": "federal"
                }
            },
            required=["violation_type", "violation_details"],
            func=calculate_penalties_and_interest
        )

        # 11. Multi-Document Comparison
        self.register_tool(
            name="compare_documents",
            description="Perform comparative analysis across multiple legal or financial documents. Identify differences, highlight conflicts, find common elements, and generate side-by-side comparison reports.",
            parameters={
                "document_list": {
                    "type": "array",
                    "description": "List of documents to compare",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Document name"},
                            "content": {"type": "string", "description": "Document content/text"},
                            "version": {"type": "string", "description": "Document version"},
                            "date": {"type": "string", "description": "Document date (YYYY-MM-DD)"}
                        }
                    }
                },
                "comparison_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "enum": ["clauses", "provisions", "differences", "common_elements", "changes"],
                    "description": "Types of comparison to perform"
                }
            },
            required=["document_list"],
            func=compare_documents
        )

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns tool definitions in Groq API format."""
        return [tool["definition"] for tool in self._tools.values()]

    def get_tool_function(self, name: str) -> Callable:
        """Returns the implementation function for a tool name."""
        if name in self._tools:
            return self._tools[name]["function"]
        raise ValueError(f"Tool '{name}' not found in registry.")

    def list_tools(self) -> List[Dict[str, str]]:
        """Returns names and descriptions of all registered tools."""
        return [
            {
                "name": name,
                "description": tool["definition"]["function"]["description"]
            }
            for name, tool in self._tools.items()
        ]
