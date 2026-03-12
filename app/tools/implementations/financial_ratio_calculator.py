import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

def calculate_financial_ratios(
    balance_sheet: Dict[str, float],
    income_statement: Dict[str, float],
    cash_flow: Optional[Dict[str, float]] = None,
    ratio_types: Optional[list] = None
) -> Dict[str, Any]:
    """
    Calculate comprehensive financial ratios from financial statements.
    
    Args:
        balance_sheet: Balance sheet items {item_name: amount}
        income_statement: P&L items {item_name: amount}
        cash_flow: Cash flow items (optional)
        ratio_types: Types of ratios to calculate (profitability, liquidity, leverage, efficiency)
    
    Returns:
        Calculated ratios with interpretations and health assessment
    """
    try:
        data_path = Path(__file__).parent.parent / "data" / "financial_ratios.json"
        with open(data_path, "r") as f:
            data = json.load(f)
        
        if not ratio_types:
            ratio_types = ["profitability", "liquidity", "leverage", "efficiency"]
        
        calculated_ratios = {}
        interpretations = {}
        flags = []
        health_score = 0
        
        # Extract balance sheet items
        current_assets = balance_sheet.get("current_assets", 0)
        current_liabilities = balance_sheet.get("current_liabilities", 0)
        inventory = balance_sheet.get("inventory", 0)
        total_assets = balance_sheet.get("total_assets", 0)
        total_equity = balance_sheet.get("total_equity", 0)
        total_debt = balance_sheet.get("total_debt", 0)
        cash = balance_sheet.get("cash", 0)
        accounts_receivable = balance_sheet.get("accounts_receivable", 0)
        
        # Extract income statement items
        revenue = income_statement.get("revenue", 0)
        gross_profit = income_statement.get("gross_profit", 0)
        operating_income = income_statement.get("operating_income", 0)
        net_income = income_statement.get("net_income", 0)
        cogs = income_statement.get("cost_of_goods_sold", 0)
        ebit = income_statement.get("ebit", operating_income)
        interest_expense = income_statement.get("interest_expense", 0)
        
        # Extract cash flow items
        if cash_flow:
            operating_cash_flow = cash_flow.get("operating_cash_flow", 0)
        else:
            operating_cash_flow = 0
        
        calculated_ratios["basic_inputs"] = {
            "revenue": revenue,
            "net_income": net_income,
            "total_assets": total_assets,
            "shareholders_equity": total_equity
        }
        
        # PROFITABILITY RATIOS
        if "profitability" in ratio_types:
            profitability = {}
            
            if revenue > 0:
                gp_margin = (gross_profit / revenue) * 100 if gross_profit > 0 else 0
                profitability["gross_profit_margin"] = {
                    "value": round(gp_margin, 2),
                    "unit": "%",
                    "interpretation": data["ratio_categories"]["profitability_ratios"]["gross_profit_margin"]["interpretation"],
                    "benchmark": data["ratio_categories"]["profitability_ratios"]["gross_profit_margin"]["benchmark"],
                    "health": "excellent" if 20 < gp_margin < 50 else "good" if gp_margin > 15 else "concerning"
                }
                
                op_margin = (ebit / revenue) * 100 if ebit > 0 else 0
                profitability["operating_profit_margin"] = {
                    "value": round(op_margin, 2),
                    "unit": "%",
                    "interpretation": data["ratio_categories"]["profitability_ratios"]["operating_profit_margin"]["interpretation"],
                    "benchmark": "Typically 5-15%",
                    "health": "excellent" if 8 < op_margin < 15 else "good" if op_margin > 5 else "concerning"
                }
                
                np_margin = (net_income / revenue) * 100
                profitability["net_profit_margin"] = {
                    "value": round(np_margin, 2),
                    "unit": "%",
                    "interpretation": "Shows percentage of revenue becoming profit",
                    "benchmark": "2-10% across industries",
                    "health": "excellent" if 5 < np_margin < 15 else "good" if np_margin > 2 else "concerning" if np_margin < 0 else "average"
                }
            
            if total_equity > 0:
                roe = (net_income / total_equity) * 100
                profitability["return_on_equity"] = {
                    "value": round(roe, 2),
                    "unit": "%",
                    "interpretation": "How efficiently company uses shareholder capital",
                    "benchmark": "15-20% is good",
                    "health": "excellent" if roe > 20 else "good" if roe > 15 else "average" if roe > 0 else "concerning"
                }
                health_score += 1 if roe > 15 else 0
            
            if total_assets > 0:
                roa = (net_income / total_assets) * 100
                profitability["return_on_assets"] = {
                    "value": round(roa, 2),
                    "unit": "%",
                    "interpretation": "Efficiency of asset utilization",
                    "benchmark": "5-10% is reasonable",
                    "health": "excellent" if roa > 10 else "good" if roa > 5 else "average" if roa > 0 else "concerning"
                }
                health_score += 1 if roa > 5 else 0
            
            calculated_ratios["profitability_ratios"] = profitability
            interpretations["profitability"] = "Company generates profit efficiently from operations"
        
        # LIQUIDITY RATIOS
        if "liquidity" in ratio_types:
            liquidity = {}
            
            if current_liabilities > 0:
                current_ratio = current_assets / current_liabilities
                liquidity["current_ratio"] = {
                    "value": round(current_ratio, 2),
                    "interpretation": "Ability to pay short-term obligations",
                    "benchmark": "1.5 to 2.0 is healthy",
                    "health": "excellent" if 1.5 < current_ratio < 3 else "good" if current_ratio > 1.2 else "concerning" if current_ratio < 1 else "average"
                }
                if current_ratio < 1:
                    flags.append("WARNING: Current ratio below 1.0 - potential liquidity crisis")
                
                quick_assets = current_assets - inventory
                quick_ratio = quick_assets / current_liabilities
                liquidity["quick_ratio"] = {
                    "value": round(quick_ratio, 2),
                    "interpretation": "Most liquid assets available for immediate needs",
                    "benchmark": "1.0 or higher",
                    "health": "good" if quick_ratio >= 1 else "concerning"
                }
                
                cash_ratio = cash / current_liabilities if current_liabilities > 0 else 0
                liquidity["cash_ratio"] = {
                    "value": round(cash_ratio, 2),
                    "interpretation": "Cash directly available to pay obligations",
                    "benchmark": "0.2-0.5",
                    "health": "good" if 0.2 < cash_ratio < 0.5 else "average"
                }
                
                health_score += 1 if 1.5 < current_ratio < 2.5 else 0
            
            working_capital = current_assets - current_liabilities
            liquidity["working_capital"] = {
                "value": round(working_capital, 2),
                "unit": "Currency units",
                "interpretation": "Capital available for daily operations",
                "health": "good" if working_capital > 0 else "concerning"
            }
            if working_capital < 0:
                flags.append("ALERT: Negative working capital - immediate action needed")
            
            calculated_ratios["liquidity_ratios"] = liquidity
        
        # LEVERAGE RATIOS
        if "leverage" in ratio_types:
            leverage = {}
            
            if total_equity > 0:
                debt_to_equity = total_debt / total_equity
                leverage["debt_to_equity"] = {
                    "value": round(debt_to_equity, 2),
                    "interpretation": "Proportion of debt vs equity financing",
                    "benchmark": "Less than 2.0 is generally safe",
                    "health": "good" if debt_to_equity < 2 else "concerning" if debt_to_equity > 2.5 else "average"
                }
                health_score += 1 if debt_to_equity < 2 else 0
            
            if total_assets > 0:
                debt_to_assets = total_debt / total_assets
                leverage["debt_to_assets"] = {
                    "value": round(debt_to_assets, 2),
                    "interpretation": "Percentage of assets financed by debt",
                    "benchmark": "Less than 0.6 (60%) is healthy",
                    "health": "good" if debt_to_assets < 0.6 else "concerning"
                }
            
            if total_equity > 0:
                equity_multiplier = total_assets / total_equity
                leverage["equity_multiplier"] = {
                    "value": round(equity_multiplier, 2),
                    "interpretation": "Leverage effect of debt financing",
                    "benchmark": "2.0 to 3.0 is typical"
                }
            
            if interest_expense > 0 and ebit > 0:
                interest_coverage = ebit / interest_expense
                leverage["interest_coverage"] = {
                    "value": round(interest_coverage, 2),
                    "interpretation": "Ability to pay interest from operating income",
                    "benchmark": "Greater than 2.5 is safe",
                    "health": "good" if interest_coverage > 2.5 else "concerning" if interest_coverage < 1.5 else "average"
                }
                if interest_coverage < 1.5:
                    flags.append("WARNING: Low interest coverage - difficulty meeting interest obligations")
            
            calculated_ratios["leverage_ratios"] = leverage
        
        # EFFICIENCY RATIOS
        if "efficiency" in ratio_types:
            efficiency = {}
            
            if total_assets > 0:
                asset_turnover = revenue / total_assets
                efficiency["asset_turnover"] = {
                    "value": round(asset_turnover, 2),
                    "interpretation": "Revenue generated per rupee of assets",
                    "benchmark": "Industry dependent",
                    "health": "good" if asset_turnover > 1 else "average"
                }
            
            if cogs > 0 and inventory > 0:
                inventory_turnover = cogs / inventory
                efficiency["inventory_turnover"] = {
                    "value": round(inventory_turnover, 2),
                    "interpretation": "Times inventory is sold and replenished",
                    "benchmark": "Higher is better"
                }
            
            avg_receivables = accounts_receivable
            if avg_receivables > 0 and revenue > 0:
                receivables_turnover = revenue / avg_receivables
                dso = 365 / receivables_turnover
                efficiency["receivables_turnover"] = {
                    "value": round(receivables_turnover, 2),
                    "interpretation": "How quickly receivables are converted to cash"
                }
                efficiency["days_sales_outstanding"] = {
                    "value": round(dso, 0),
                    "unit": "days",
                    "interpretation": "Average days to collect payment",
                    "benchmark": "30-60 days is typical",
                    "health": "good" if 30 < dso < 60 else "concerning" if dso > 90 else "average"
                }
            
            calculated_ratios["efficiency_ratios"] = efficiency
        
        # Overall Health Assessment
        health_levels = ["critical", "concerning", "average", "good", "excellent"]
        health_index = min(4, health_score // 2)  # Normalize to 0-4
        overall_health = health_levels[health_index]
        
        return {
            "success": True,
            "calculated_ratios": calculated_ratios,
            "interpretations": interpretations,
            "overall_financial_health": overall_health,
            "health_score_details": f"{health_score} positive indicators identified",
            "critical_flags": flags,
            "summary": _generate_ratio_summary(calculated_ratios, overall_health),
            "recommendations": _generate_ratio_recommendations(calculated_ratios, flags)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def _generate_ratio_summary(ratios: Dict, health: str) -> str:
    """Generate a summary of financial health"""
    return f"Financial analysis complete. Overall financial health: {health.upper()}. Review calculated ratios and recommendations for detailed insight."

def _generate_ratio_recommendations(ratios: Dict, flags: list) -> list:
    """Generate specific recommendations based on financial ratios"""
    recommendations = []
    
    if flags:
        recommendations.append(f"ADDRESS IMMEDIATELY: {flags[0]}")
    
    if "liquidity_ratios" in ratios:
        current_ratio = ratios["liquidity_ratios"].get("current_ratio", {}).get("value", 0)
        if current_ratio < 1.5:
            recommendations.append("Improve liquidity: Consider reducing current liabilities or increasing current assets")
    
    if "profitability_ratios" in ratios:
        npm = ratios["profitability_ratios"].get("net_profit_margin", {}).get("value", 0)
        if npm < 2:
            recommendations.append("Reduce operating costs or increase pricing to improve profitability")
    
    if "leverage_ratios" in ratios:
        dte = ratios["leverage_ratios"].get("debt_to_equity", {}).get("value", 0)
        if dte > 2.5:
            recommendations.append("High leverage: Consider debt repayment or equity infusion to reduce leverage")
    
    recommendations.append("Conduct periodic financial reviews and comparisons with industry benchmarks")
    
    return recommendations
