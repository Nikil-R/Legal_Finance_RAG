"""
Legal Disclaimers Module

Add disclaimers and legal protection to all system responses.
Protects the student project legally while being transparent about limitations.
"""

from datetime import datetime
from typing import Dict, Any

class LegalDisclaimers:
    """Generate context-appropriate disclaimers"""
    
    GENERAL_DISCLAIMER = """
⚠️  EDUCATIONAL PROJECT DISCLAIMER
═══════════════════════════════════════════════════════════════
This is a student-built educational demonstration project, NOT professional advice.

Project: Legal Finance RAG System
Developer: [Your Name]
Institution: [Your College/University]
Last Updated: {date}

✓ FOR EDUCATIONAL PURPOSES ONLY
✓ NOT A SUBSTITUTE FOR PROFESSIONAL ADVICE
✓ DATA MAY NOT BE CURRENT OR ACCURATE FOR REAL DECISIONS

For actual legal, tax, or compliance matters, consult:
• Qualified Lawyers / Legal Professionals
• Chartered Accountants / Tax Advisors  
• Registered Compliance Officers
• Official Government Portals

This system is a demonstration of AI/RAG technology.
Results should be independently verified before any real use.
═══════════════════════════════════════════════════════════════
"""

    TAX_CALCULATION_DISCLAIMER = """
⚠️  TAX CALCULATION DISCLAIMER
───────────────────────────────────────────────────────
This calculation is an ESTIMATE ONLY.

Actual tax liability depends on:
• Complete income picture (salaries, investments, savings)
• All applicable deductions and exemptions
• Specific circumstances and jurisdiction
• Current tax year rules

IMPORTANT:
• Verify results with official Income Tax India portal
• Consult a Chartered Accountant for your actual tax filing
• This is educational demonstration, not professional advice
• Use at your own risk

Official Tax Portal: https://www.incometaxindia.gov.in
───────────────────────────────────────────────────────
"""

    COURT_CASE_DISCLAIMER = """
⚠️  COURT CASE INFORMATION DISCLAIMER
───────────────────────────────────────────────────────
This is a SUMMARY for educational purposes only.

Case summaries are NOT:
• Complete legal analysis
• A substitute for reading full judgment
• Applicable to your specific situation
• Professional legal advice

FOR LEGAL RESEARCH:
1. Read the complete judgment on Indian Kanoon
2. Consult a qualified lawyer for your specific case
3. Do not rely solely on this summary for legal decisions

This is educational demonstration of legal information retrieval.
───────────────────────────────────────────────────────
"""

    GST_RATE_DISCLAIMER = """
⚠️  GST RATE INFORMATION DISCLAIMER
───────────────────────────────────────────────────────
GST rates shown are based on data collected on {date}.

IMPORTANT:
• GST rates can change - verify current rates on official portal
• Rates may vary based on specific product classification
• Service tax implications may differ
• Exemptions and conditions apply

For authoritative information:
→ GST Portal: https://www.gst.gov.in
→ CBIC Portal: https://cbic-gst.gov.in

Always verify with official sources before compliance actions.
───────────────────────────────────────────────────────
"""

    COMPLIANCE_DISCLAIMER = """
⚠️  COMPLIANCE INFORMATION DISCLAIMER
───────────────────────────────────────────────────────
Compliance requirements shown are for GENERAL INFORMATION.

This information:
• May not cover your specific situation
• Cannot replace professional compliance advice
• Requires verification with current regulations
• Should be reviewed by compliance professional

For authoritative guidance:
→ Ministry of Corporate Affairs: https://www.mca.gov.in
→ Consult Company Secretary or Compliance Professional

Do not rely solely on this for compliance decisions.
───────────────────────────────────────────────────────
"""

    @staticmethod
    def get_general_disclaimer() -> str:
        """Get general project disclaimer"""
        return LegalDisclaimers.GENERAL_DISCLAIMER.format(
            date=datetime.now().strftime("%B %d, %Y")
        )
    
    @staticmethod
    def get_tax_disclaimer() -> str:
        """Get tax calculation specific disclaimer"""
        return LegalDisclaimers.TAX_CALCULATION_DISCLAIMER
    
    @staticmethod
    def get_court_case_disclaimer() -> str:
        """Get court case information disclaimer"""
        return LegalDisclaimers.COURT_CASE_DISCLAIMER
    
    @staticmethod
    def get_gst_disclaimer() -> str:
        """Get GST rate specific disclaimer"""
        return LegalDisclaimers.GST_RATE_DISCLAIMER.format(
            date=datetime.now().strftime("%B %d, %Y")
        )
    
    @staticmethod
    def get_compliance_disclaimer() -> str:
        """Get compliance information disclaimer"""
        return LegalDisclaimers.COMPLIANCE_DISCLAIMER
    
    @staticmethod
    def add_disclaimer_to_response(response: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """Add appropriate disclaimer based on tool used"""
        
        disclaimer_map = {
            "calculate_taxes": LegalDisclaimers.get_tax_disclaimer(),
            "search_court_cases": LegalDisclaimers.get_court_case_disclaimer(),
            "lookup_gst_rates": LegalDisclaimers.get_gst_disclaimer(),
            "check_compliance": LegalDisclaimers.get_compliance_disclaimer(),
        }
        
        # Add disclaimer if tool-specific
        if tool_name in disclaimer_map:
            response["disclaimer"] = disclaimer_map[tool_name]
        
        # Always add general note
        response["legal_note"] = "This is educational information only. Not professional advice."
        response["generated_at"] = datetime.now().isoformat()
        
        return response


class TermsOfService:
    """Generate Terms of Service page content"""
    
    TERMS_CONTENT = """
# Legal Finance RAG System - Terms of Service

**Last Updated:** March 12, 2026

## 1. Purpose & Scope

This system is a **student educational project** demonstrating Retrieval Augmented Generation (RAG) technology applied to legal and financial information.

**What This Is:**
- An AI demonstration project
- Educational tool for learning purposes
- Proof of concept for RAG systems
- Portfolio project by [Student Name]

**What This Is NOT:**
- Professional legal advice
- Professional tax/financial advice
- A business service
- Guaranteed accurate or current information
- A replacement for qualified professionals

## 2. Limitations

### Information Accuracy
- Data is collected from official government sources
- Collection date is noted for each data point
- Users must independently verify all information
- Information may become outdated

### No Professional Relationship
- No attorney-client relationship exists
- No accountant-client relationship exists
- No compliance advisor relationship exists
- No liability for decisions based on this information

### No Liability
- System provided "as-is" without warranty
- No guarantee of accuracy, completeness, or timeliness
- User assumes all risk for using this information
- Creator not liable for any damages or losses

## 3. Proper Use

### Permitted Uses
✓ Educational exploration of legal/financial information
✓ Learning about RAG and AI systems
✓ Academic research and demonstration

### Prohibited Uses
✗ Making actual legal decisions
✗ Making actual tax/financial decisions
✗ Business compliance without professional review
✗ Representing this as professional advice
✗ Using for client advisory services

## 4. Data & Privacy

- No personal information is stored
- No analytics tracking users
- Queries are not retained
- No data sharing with third parties

## 5. Required Consultations

Before any real use of information provided, consult:

**For Legal Questions:**
- Qualified lawyer licensed in your jurisdiction
- Law firm specializing in relevant area

**For Tax Questions:**
- Chartered Accountant (India)
- Tax professional in your jurisdiction

**For Compliance:**
- Company Secretary
- Compliance professional
- Relevant government agency

**For Official Information:**
- Government portals (mca.gov.in, incometaxindia.gov.in, gst.gov.in)
- Official notifications and rules

## 6. Intellectual Property

This project is open source under MIT License.

- Source code: Available on GitHub
- Documentation: Available for reference
- Data: From public domain government sources

## 7. Modifications

This system may be updated or modified without notice.

## 8. Acceptance

By using this system, you acknowledge:
- You have read and understood these terms
- You will not rely solely on this system for real decisions
- You will consult professionals before any action
- You accept all risks of using this information

## 9. Contact

For questions about this project:
- Email: [Your Email]
- GitHub: [Your Repo]
- Institution: [Your College]

---

**This is a student project. Use responsibly and verify independently before any real-world application.**
"""
    
    @staticmethod
    def get_terms() -> str:
        """Get full terms of service"""
        return TermsOfService.TERMS_CONTENT


class AttributionsPage:
    """Generate attributions and credits page"""
    
    ATTRIBUTIONS_CONTENT = """
# Attributions & Data Sources

This student project uses data from official Indian government sources.

## Primary Data Sources

### 1. Supreme Court Cases
**Source:** [Indian Kanoon](https://indiankanoon.org)
**License:** Public Domain
**Data:** Supreme Court of India judgments
**Attribution:** Indian Kanoon repository of Indian legal judgments
**URL:** indiankanoon.org

### 2. Tax Rules & Rates
**Source:** [Income Tax India](https://www.incometaxindia.gov.in)
**License:** Public Domain (Government of India)
**Data:** Tax slabs, deductions, rates, penalties
**Attribution:** Ministry of Finance, Department of Revenue
**URL:** incometaxindia.gov.in

### 3. GST Information
**Source:** [Goods and Services Tax Network](https://www.gst.gov.in)
**License:** Public Domain (Government of India)
**Data:** GST rates, classifications, HSN/SAC codes
**Attribution:** Central Board of Indirect Taxes and Customs (CBIC)
**URL:** gst.gov.in

### 4. Company Compliance
**Source:** [Ministry of Corporate Affairs](https://www.mca.gov.in)
**License:** Public Domain (Government of India)
**Data:** Company law compliance requirements, filing procedures
**Attribution:** Ministry of Corporate Affairs
**URL:** mca.gov.in

## Technology Stack

### Open Source Libraries
- **LangChain** - LLM orchestration framework
- **FastAPI** - Web framework
- **ChromaDB** - Vector database
- **GROQ** - LLM API

### Hosting
- **Render.com** - Cloud deployment platform

## Project Credits

**Student Developer:** [Your Name]
**Institution:** [Your College/University]
**Project:** Legal Finance RAG System
**Created:** March 12, 2026
**GitHub:** [Your Repository Link]

## Legal Compliance

All data used is from:
- Official government websites
- Public domain sources
- Properly attributed
- No copyright infringement

## Data Verification

All information has been:
- ✓ Sourced from official government portals
- ✓ Properly attributed and linked
- ✓ Verified as current (as of collection date)
- ✓ Documented with collection methodology

Users are advised to:
1. Review original sources directly
2. Verify with current official portals
3. Consult professionals for real use
4. Check for updates regularly

---

**This is an educational student project. Data is from official government sources for demonstration purposes only.**

Thank you to all the open source projects and government agencies that made this possible!
"""
    
    @staticmethod
    def get_attributions() -> str:
        """Get full attributions page"""
        return AttributionsPage.ATTRIBUTIONS_CONTENT


def demo_disclaimers():
    """Demonstrate disclaimer functionality"""
    
    print("\n" + "="*70)
    print("GENERAL PROJECT DISCLAIMER")
    print("="*70)
    print(LegalDisclaimers.get_general_disclaimer())
    
    print("\n" + "="*70)
    print("TAX CALCULATION DISCLAIMER")
    print("="*70)
    print(LegalDisclaimers.get_tax_disclaimer())
    
    print("\n" + "="*70)
    print("COURT CASE DISCLAIMER")
    print("="*70)
    print(LegalDisclaimers.get_court_case_disclaimer())
    
    print("\n" + "="*70)
    print("GST RATE DISCLAIMER")
    print("="*70)
    print(LegalDisclaimers.get_gst_disclaimer())
    
    print("\n" + "="*70)
    print("TERMS OF SERVICE (First 500 chars)")
    print("="*70)
    print(TermsOfService.get_terms()[:500] + "...")
    
    print("\n" + "="*70)
    print("ATTRIBUTIONS (First 500 chars)")
    print("="*70)
    print(AttributionsPage.get_attributions()[:500] + "...")
    
    print("\n✅ All legal disclaimers and pages generated successfully")


if __name__ == "__main__":
    demo_disclaimers()
