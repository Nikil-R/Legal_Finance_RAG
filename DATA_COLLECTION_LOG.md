# Real Data Collection Progress Log

**Project:** Legal Finance RAG System - Portfolio Showcase  
**Status:** In Progress  
**Last Updated:** March 12, 2026  
**Target:** Quality over quantity - curated real data for impressiveness

---

## Collection Status Overview

| Data Type       | Source           | Target              | Collected | Status      |
| --------------- | ---------------- | ------------------- | --------- | ----------- |
| **Court Cases** | indiankanoon.org | 30 cases            | 0/30      | ⏳ Starting |
| **Tax Rules**   | incometax.gov.in | Complete current FY | 0         | ⏳ Next     |
| **GST Rates**   | gst.gov.in       | 50 common items     | 0/50      | ⏳ Next     |
| **Compliance**  | mca.gov.in       | 4 entity types      | 0/4       | ⏳ Later    |

---

## Court Cases Collection (Target: 30)

### Instructions

- Visit: https://indiankanoon.org
- Search for landmark cases
- Extract: citation, judges, date, principles, summary, sections, outcome
- Save as JSON in `data/real/court_cases/`
- Quality > Quantity - choose well-known, important cases

### Priority Cases to Collect

#### Constitutional & Rights (5 cases)

- [ ] **Kesavananda Bharati v. State of Kerala** (1973) - Basic structure doctrine
  - Citation: AIR 1973 SC 1461
  - Key Principle: Constitution has basic structure that cannot be amended
  - Status: Not collected

- [ ] **Maneka Gandhi v. Union of India** (1978) - Article 21 interpretation
  - Citation: AIR 1978 SC 597
  - Key Principle: Right to life includes personal liberty and procedure must be reasonable
  - Status: Not collected

- [ ] **Puttaswamy v. Union of India** (2017) - Right to Privacy
  - Citation: (2017) 10 SCC 1
  - Key Principle: Privacy is fundamental right under Article 21
  - Status: Not collected

- [ ] **Shreya Singhal v. Union of India** (2015) - Cyber crime and free speech
  - Citation: (2015) 5 SCC 1
  - Key Principle: Section 66A IPC struck down as unconstitutional
  - Status: Not collected

- [ ] **Vishaka v. State of Rajasthan** (1997) - Sexual harassment
  - Citation: AIR 1997 SC 3011
  - Key Principle: Guidelines for workplace sexual harassment prevention
  - Status: Not collected

#### Tax & Finance (5 cases)

- [ ] **Goodyear India Ltd. v. State of Haryana** - GST valuation
  - Target: Tax + GST calculation concepts
  - Status: Not collected

- [ ] **Union of India v. Gopal Das** - Income tax assessment
  - Target: Tax assessment procedures
  - Status: Not collected

- [ ] Cases on TDS, tax deductions, corporate taxation
  - Target: 3 major tax dispute cases
  - Status: Not collected

#### Corporate & Regulatory (5 cases)

- [ ] Company law landmark cases
  - Status: Not collected

- [ ] Stock market and securities cases
  - Status: Not collected

#### Consumer Protection (3 cases)

- [ ] Consumer complaint procedures
  - Status: Not collected

#### Recent Important Judgments (7 cases)

- [ ] Cases from 2023-2026
  - Status: Not collected

---

## Tax Rules Collection

### Current FY Data to Extract

- [ ] **Tax Slabs** (Old & New Regime)
  - Income brackets
  - Tax rates
  - Surcharges
  - Cess

- [ ] **Major Deductions**
  - [ ] Section 80C (PPF, ELSS, LIC, Tuition)
  - [ ] Section 80D (Medical Insurance)
  - [ ] Section 80E (Education Loan Interest)
  - [ ] Section 24 (Home Loan Interest)
  - [ ] HRA, LTA, Standard Deduction

- [ ] **Special Categories**
  - [ ] Senior Citizen benefits
  - [ ] NRI taxation
  - [ ] Corporate tax rates

---

## GST Rates Collection (50 items minimum)

### Categories to Cover

- [ ] **Food & Beverages** (10 items)
  - Rice, packaged foods, restaurant services, dairy

- [ ] **Electronics** (8 items)
  - Mobile phones, laptops, accessories

- [ ] **Services** (12 items)
  - Consulting, hotels, transport, education, healthcare

- [ ] **Daily Use** (8 items)
  - Clothing, footwear, cosmetics

- [ ] **Vehicles & Real Estate** (7 items)
  - Cars, motorcycles, property related

- [ ] **Agriculture & Luxury** (5 items)
  - Equipment, premium goods

---

## Compliance Requirements

### Entity Types to Cover

- [ ] Private Limited Company
- [ ] LLP (Limited Liability Partnership)
- [ ] Proprietorship
- [ ] Partnership Firm

### For Each: Annual filings, deadlines, penalties, sections

---

## Data Quality Checklist

For each piece of data collected:

- [ ] Source URL recorded
- [ ] Collection date documented
- [ ] Licensing terms verified
- [ ] Data accuracy confirmed against official source
- [ ] Properly formatted (JSON/CSV/MD)
- [ ] Location: `data/real/[category]/` directory

---

## Success Metrics

- ✅ 30 Supreme Court cases: Quality selection, diverse categories
- ✅ Complete tax rules for current financial year
- ✅ 50 GST classifications with accurate rates
- ✅ Complete compliance matrix
- ✅ All data from official government sources
- ✅ Zero placeholder or synthetic data
- ✅ Full attribution and source documentation

---

## Collection Tips

1. **Work smarter**: Copy-paste from sources when possible
2. **Quality focus**: One excellent case beats ten rushed ones
3. **Organize as you go**: Save immediately to proper directory
4. **Track progress**: Update this log daily
5. **Verify accuracy**: Double-check against source before saving
6. **Document everything**: Note sources, dates, any issues

---

**Next Step:** Start with Kesavananda Bharati case today. Target: 5 cases by end of this week.
