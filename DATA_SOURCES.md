# Data Sources & Attribution

**Legal Finance RAG System - Data Attribution & Licensing**

This document provides complete attribution for all data sources integrated into the system. Maintaining proper attribution protects this project legally and ethically.

---

## Official Government Sources

### 1. Indian Kanoon - Supreme Court Cases

**Source URL:** https://indiankanoon.org  
**Data Type:** Supreme Court judgments and legal precedents  
**Collection Method:** Manual extraction of case summaries  
**License:** Public domain (Indian court judgments)  
**Collection Date:** March 12, 2026  
**Last Verified:** March 12, 2026  
**Update Frequency:** Monthly (new judgments)

**Cases Collected:**

- (To be updated as cases are added)

**Usage in System:**

- Court case search tool
- Legal precedent retrieval
- RAG context for compliance queries

**Legal Note:** Indian court judgments are public domain. Attribution to Indian Kanoon as repository is good practice.

---

### 2. Income Tax India Portal

**Source URL:** https://www.incometaxindia.gov.in  
**Data Type:** Tax slabs, deductions, rules, penalties  
**Collection Method:** Direct extraction from official portal  
**License:** Public domain (Government of India)  
**Collection Date:** March 12, 2026  
**Applicable Year:** FY 2024-25 (April 2024 - March 2025)  
**Last Verified:** March 12, 2026  
**Update Frequency:** Annual (with budget typically in February)

**Data Categories:**

- Tax slabs (old & new regime)
- Deductions (Section 80C, 80D, 80E, 24)
- HRA, LTA, standard deduction
- Rebates (Section 87A)
- Standard deduction limits
- Tax computation rules

**Usage in System:**

- Tax calculation tool
- Deduction guidance
- Penalty calculation

**Critical Note:** Tax rules change yearly. Must update every April when new FY begins. Current data is valid through March 31, 2025.

---

### 3. GST Portal

**Source URL:** https://www.gst.gov.in  
**Backup URLs:**

- https://cbic-gst.gov.in
- https://www.cbic.gov.in

**Data Type:** GST rates and classifications (HSN/SAC codes)  
**Collection Method:** Rate schedules from official portal  
**License:** Public domain (Government of India)  
**Collection Date:** March 12, 2026  
**Last Verified:** March 12, 2026  
**Update Frequency:** Quarterly (rates updated as notified)

**Data Categories:**

- 5% rate items (food, medicines)
- 12% rate items (electronics, tools)
- 18% rate items (general goods, services)
- 28% rate items (luxury goods, automobiles)
- Exemptions (education, healthcare)
- HSN/SAC codes and classifications

**Usage in System:**

- GST rate lookup tool
- Invoice calculation assistance
- Compliance checking for business

**Critical Note:** GST rates can change. System should prompt users to verify on gst.gov.in for actual compliance.

---

### 4. Ministry of Corporate Affairs (MCA)

**Source URL:** https://www.mca.gov.in  
**Alternate URL:** https://ebiz.mca.gov.in

**Data Type:** Company compliance requirements, filing deadlines, penalties  
**Collection Method:** Official MCA compliance matrices  
**License:** Public domain (Government of India)  
**Collection Date:** March 12, 2026  
**Last Verified:** March 12, 2026  
**Update Frequency:** As regulations update (quarterly review)

**Entity Types Covered:**

- Private Limited Companies
- Limited Liability Partnerships (LLPs)
- Proprietorships
- Partnership Firms

**Data Categories:**

- Annual filing requirements (forms needed)
- Filing deadlines
- Penalties for late/non-filing
- Applicable legal sections
- Director responsibilities
- Audit requirements

**Usage in System:**

- Compliance checker tool
- Deadline reminder (if enabled)
- Regulatory requirement lookup

**Critical Note:** Company law updates regularly. Data should be reviewed quarterly for new rules or amendments.

---

## Data Attribution Requirements

### In-App Display

Every response containing government data should include:

```
Data Sources:
• Tax rates: Income Tax India (incometaxindia.gov.in) - Valid through March 31, 2025
• GST rates: GST Portal (gst.gov.in) - Last updated March 12, 2026
• Compliance: Ministry of Corporate Affairs (mca.gov.in)
• Court cases: Indian Kanoon (indiankanoon.org)

Disclaimer: This is educational information only, not professional advice.
For authoritative information, verify on official government portals.
```

### API Response Headers

```json
{
  "data_sources": [
    "incometaxindia.gov.in",
    "gst.gov.in",
    "mca.gov.in",
    "indiankanoon.org"
  ],
  "generated_date": "2026-03-12",
  "accuracy_note": "Information is current as of March 12, 2026. Verify with official sources for up-to-date information."
}
```

---

## Legal Compliance

### Government Data Protection

- ✅ All data from official government websites (public domain)
- ✅ No copyright infringement (not using proprietary databases)
- ✅ Proper attribution to all sources
- ✅ Clear disclaimers about educational use
- ✅ Explicit warnings about verification with official sources

### What We Don't Do

- ❌ Claim original authorship of government data
- ❌ Claim data is always current (we state collection dates)
- ❌ Provide data as professional legal/tax advice
- ❌ Hide sources or misattribute information
- ❌ Use copyrighted commercial databases

### Ongoing Responsibilities

1. **Monthly Review:** Check primary sources for major updates
2. **Quarterly Audit:** Verify data accuracy against official portals
3. **Annual Refresh:** Update all tax and compliance data with FY changes
4. **Changelog Maintenance:** Document every data update with dates
5. **Source Verification:** Keep links to sources functional and documented

---

## Data Format

### Court Cases JSON Template

```json
{
  "case_id": "kesavananda_bharati_1973",
  "title": "Kesavananda Bharati v. State of Kerala",
  "citation": "AIR 1973 SC 1461",
  "decision_date": "1973-04-24",
  "judges": ["Chief Justice S.M. Sikri", "Justices..."],
  "court": "Supreme Court of India",
  "category": "Constitutional Law",
  "legal_principles": [
    "Basic structure doctrine",
    "Limits of constitutional amendment power"
  ],
  "relevant_acts": ["Indian Constitution Article 368"],
  "summary": "Full case summary here...",
  "outcome": "Amendment power is not absolute; basic structure cannot be amended",
  "key_quotes": ["Quote 1...", "Quote 2..."],
  "source": "https://indiankanoon.org/doc/...",
  "collection_date": "2026-03-12",
  "verified": true
}
```

### Tax Rules JSON Template

```json
{
  "type": "tax_slab",
  "financial_year": "2024-25",
  "regime": "new",
  "brackets": [
    {
      "income_range": "0-300000",
      "rate": "0%",
      "description": "No tax"
    },
    {
      "income_range": "300000-700000",
      "rate": "5%",
      "description": "5% standard rate"
    }
  ],
  "source": "https://www.incometaxindia.gov.in",
  "collection_date": "2026-03-12",
  "valid_through": "2025-03-31",
  "last_verified": "2026-03-12"
}
```

---

## Maintenance Schedule

- **Weekly:** Monitor for breaking news about regulatory changes
- **Monthly:** Audit top 10 most-used queries for accuracy
- **Quarterly:** Formal review of all data sources for updates
- **Annually:** Complete refresh cycle before new financial year (April)
- **On-Demand:** Update immediately if official source issues correction

---

## Contact & Attribution

**Project:** Legal Finance RAG System  
**Created by:** [Your Name]  
**Institution:** [Your College/University]  
**Repository:** [GitHub link]  
**Contact:** [Your email]

**Data maintained with integrity and proper attribution to:**

- Ministry of Corporate Affairs (mca.gov.in)
- Income Tax India (incometaxindia.gov.in)
- Central Board of Indirect Taxes (cbic-gst.gov.in)
- Indian Kanoon (indiankanoon.org)

---

**Last Updated:** March 12, 2026  
**Next Review:** April 12, 2026 (monthly cycle)
