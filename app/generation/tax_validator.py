
"""
Tax Validator — validates LLM tax calculations against programmatic results.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from app.tools.implementations.tax_calculator import calculate_income_tax

logger = logging.getLogger(__name__)

class TaxValidator:
    """Validates tax calculations in LLM responses with focus on slabs and surcharge."""

    def validate(self, answer: str, question: str) -> Dict[str, Any]:
        """
        Attempts to extract income and regime from the question/answer 
        and validates the tax amount stated by the LLM.
        """
        # 1. Try to find income in question or answer
        # Look for numbers with currency symbols or commas
        # Matches: ₹25,00,000, 2500000, 25,00,000.00
        income_match = re.search(r'(?:₹|INR|Rs\.?)\s?([\d,]+(?:\.\d{1,2})?)', question + " " + answer)
        if not income_match:
            income_match = re.search(r'(?:income\s+(?:of|is|at)\s+)(?:₹|INR|Rs\.?)\s?([\d,]+)', question + " " + answer, re.IGNORECASE)
            
        if not income_match:
            # Fallback to large numbers
            income_match = re.search(r'(\d{5,}(?:,\d{2,})*)', question)
            
        if not income_match:
            return {"valid": True, "reason": "No income found to validate"}

        try:
            income_str = income_match.group(1).replace(",", "")
            income = float(income_str)
        except (ValueError, TypeError):
            return {"valid": True, "reason": "Could not parse income"}

        # 2. Determine regime
        regime = "new"
        full_text = (question + " " + answer).lower()
        if "old regime" in full_text:
            regime = "old"
        elif "new regime" in full_text:
            regime = "new"

        # 3. Extract LLM's stated total tax and surcharge
        llm_tax = self._extract_amount(answer, [
            r'(?:Total|Final)\s+tax[:\s]+(?:₹|INR|Rs\.?)\s?([\d,]+(?:\.\d{2})?)',
            r'(?:Tax\s+liability)[:\s]+(?:₹|INR|Rs\.?)\s?([\d,]+(?:\.\d{2})?)',
            r'payable\s+is\s+(?:₹|INR|Rs\.?)\s?([\d,]+(?:\.\d{2})?)'
        ])
        
        llm_surcharge = self._extract_amount(answer, [
            r'Surcharge[:\s]+(?:₹|INR|Rs\.?)\s?([\d,]+(?:\.\d{2})?)',
            r'surcharge\s+of\s+(?:₹|INR|Rs\.?)\s?([\d,]+(?:\.\d{2})?)'
        ])

        if llm_tax is None:
            return {"valid": True, "reason": "No stated tax amount found in answer to validate"}

        # 4. Programmatic calculation
        calc_result = calculate_income_tax(income=income, regime=regime)
        if not calc_result.get("success"):
            return {"valid": True, "reason": f"Programmatic calc failed: {calc_result.get('error')}"}
        
        correct_tax = calc_result["total_tax"]
        correct_surcharge = calc_result.get("surcharge", 0.0)
        
        # 5. Validation Logic
        issues = []
        
        # Check Surcharge specifically (Critical for income < 50L)
        if llm_surcharge is not None:
             if abs(llm_surcharge - correct_surcharge) > 10.0: # allow minor rounding
                 if correct_surcharge == 0 and llm_surcharge > 0:
                     issues.append(f"Incorrectly applied a surcharge of ₹{llm_surcharge:,.2f} (Threshold is ₹50L income).")
                 else:
                     issues.append(f"Surcharge discrepancy: LLM said ₹{llm_surcharge:,.2f}, should be ₹{correct_surcharge:,.2f}.")

        # Check Total Tax
        error_margin = abs(llm_tax - correct_tax)
        tolerance = max(100.0, correct_tax * 0.02) # 2% or ₹100
        
        if error_margin > tolerance:
            issues.append(f"Total tax discrepancy: LLM stated ₹{llm_tax:,.2f} but correct result is ₹{correct_tax:,.2f}.")

        if issues:
            warning = "⚠️ Tax Validation Details:\n- " + "\n- ".join(issues)
            logger.warning("Tax validation FAILED: %s", warning)
            return {
                "valid": False,
                "stated_tax": llm_tax,
                "correct_tax": correct_tax,
                "income": income,
                "regime": regime,
                "warning": warning,
                "breakdown": calc_result.get("slab_breakdown", [])
            }

        return {"valid": True, "correct_tax": correct_tax}

    def _extract_amount(self, text: str, patterns: List[str]) -> Optional[float]:
        """Helper to extract currency amounts from text."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(",", ""))
                except (ValueError, TypeError):
                    continue
        return None
