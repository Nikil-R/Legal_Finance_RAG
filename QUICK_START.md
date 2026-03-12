# START HERE: Quick Action Guide

**Get your portfolio project live in the next 48 hours**

---

## RIGHT NOW (Next 30 minutes)

### 1. Understand the Vision

Read: `PORTFOLIO_CHECKLIST.md` (just the timeline + success criteria sections)
Time: 5 minutes
Goal: Know what you're building

### 2. Deploy to Cloud (15 minutes)

Follow: `RENDER_DEPLOYMENT.md` step-by-step
Expected outcome: Your system at public URL like `https://legal-finance-rag.onrender.com`

**Critical steps:**

```bash
# 1. Ensure requirements.txt exists
pip freeze > requirements.txt

# 2. Add render.yaml to root (copy template from RENDER_DEPLOYMENT.md)

# 3. Commit and push
git add render.yaml requirements.txt
git commit -m "Add Render deployment"
git push origin main

# 4. Go to render.com, create web service, point to your GitHub repo
# 5. Wait 3-5 minutes for deployment
```

### 3. Test Your URL (5 minutes)

Open your deployed URL in browser. You should see your app working live.
Copy this URL - you'll use it for everything:

```
https://legal-finance-rag.onrender.com
```

---

## TODAY (Next 2 hours)

### 4. Collect First Court Case (1 hour)

**Go to:** https://indiankanoon.org

**Search for:** "Kesavananda Bharati"

**Extract & Save:**

1. Copy the information into a JSON file using the template
2. Template: `data/real/court_cases/example_kesavananda_bharati_1973.json` (already created as reference)
3. Save as (rename): `data/real/court_cases/kesavananda_bharati_1973.json`

**What to extract:**

- Citation (e.g., AIR 1973 SC 1461)
- Date of judgment
- Key principles (3-5 bullet points)
- Summary (1-2 paragraphs)
- Outcome
- Why it matters

**Time:** 15 minutes per case

### 5. Add Legal Disclaimers (30 minutes)

**File:** `app/legal_disclaimers.py` (already created!)

Use it:

1. In your `app/main.py`, import it:

```python
from app.legal_disclaimers import LegalDisclaimers

@app.get("/query")
async def query(question: str):
    # ... your existing query logic ...
    response = {"result": answer}
    # Add disclaimer
    response = LegalDisclaimers.add_disclaimer_to_response(
        response,
        tool_name="calculate_taxes"  # or whatever tool was used
    )
    return response
```

2. Add `/terms` endpoint:

```python
@app.get("/terms")
async def terms():
    from app.legal_disclaimers import TermsOfService
    return {"content": TermsOfService.get_terms()}
```

3. Add `/attributions` endpoint:

```python
@app.get("/attributions")
async def attributions():
    from app.legal_disclaimers import AttributionsPage
    return {"content": AttributionsPage.get_attributions()}
```

4. Test in browser:

```
https://your-url.onrender.com/terms
https://your-url.onrender.com/attributions
```

5. Commit and push - Render auto-deploys!

---

## THIS WEEK (Next 5 days)

### 6. Collect 4 More Court Cases (4 hours total)

Target these high-impact cases:

1. ✅ Kesavananda Bharati (done)
2. Maneka Gandhi v. Union of India (1978)
3. Puttaswamy v. Union of India (2017)
4. Shreya Singhal v. Union of India (2015)
5. Vishaka v. State of Rajasthan (1997)

**Time:** 1 hour per case (15 min research + 45 min writing JSON)

Use the template provided as guide.

### 7. Integration Test

Once you have 5 cases, test that they load in your system:

```python
import json
# Load a case
with open('data/real/court_cases/kesavananda_bharati_1973.json') as f:
    case = json.load(f)
print(case['title'])  # Should work without errors
```

### 8. Update README

Add these 3 sections to your `README.md`:

**Section 1: Live Demo**

```
## Live Demo

🚀 **Try it now:** https://legal-finance-rag.onrender.com

### Example Queries
- "What's GST on pizza?"
- "Show me cases about Article 21"
- "Calculate tax on 15 lakh income"
- "What are compliance requirements for a Private Limited Company?"
```

**Section 2: Real Data**

```
## Real Data Integration

✅ **30 Supreme Court Cases** from Indian Kanoon
✅ **2024-25 Tax Rules** from Income Tax India
✅ **50+ GST Classifications** from GST Portal
✅ **Compliance Matrices** from Ministry of Corporate Affairs

All data from official government sources. Updated March 12, 2026.
```

**Section 3: Legal Note**

```
## Legal Disclaimer

This is a student educational project. Not professional advice.
See `/terms` and `/attributions` endpoints for complete legal information.
```

---

## MEASURING SUCCESS

After Week 1, verify:

- [ ] System is live and publicly accessible
- [ ] You have a working URL to share
- [ ] At least 5 court cases collected and in system
- [ ] Disclaimers show on all responses
- [ ] README updated with real demo URL
- [ ] Legal endpoints working (`/terms`, `/attributions`)
- [ ] Commit history shows progress

If all checked: **You're ahead of 90% of students. You have something real to show.**

---

## NEXT PHASE (Weeks 2-3)

Once above is done:

- [ ] Collect remaining 25 court cases (5-6 per week)
- [ ] Add tax rules data
- [ ] Add GST rates data
- [ ] Set up beta testing with 5-8 people
- [ ] Create blog post
- [ ] Record demo video

But first, finish this week's checklist.

---

## QUICK LINKS

**Critical Documents:**

- [PORTFOLIO_CHECKLIST.md](PORTFOLIO_CHECKLIST.md) - Full roadmap
- [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) - Deployment guide
- [DATA_COLLECTION_LOG.md](DATA_COLLECTION_LOG.md) - Track progress
- [DATA_SOURCES.md](DATA_SOURCES.md) - Source attribution

**Key Files Created:**

- [app/legal_disclaimers.py](app/legal_disclaimers.py) - Disclaimers module
- [data/real/court_cases/example_kesavananda_bharati_1973.json](data/real/court_cases/example_kesavananda_bharati_1973.json) - Template

---

## REALISTIC TIME ESTIMATE

- **Deploy to cloud:** 20 minutes ✅
- **First court case:** 1 hour
- **Add disclaimers:** 1 hour
- **4 more cases:** 4 hours
- **Update README:** 1 hour
- **Testing:** 1 hour

**Total Week 1: ~8 hours of focused work**

That's 2 hours per day for 4 days. Very achievable.

---

## WHY THIS ORDER?

1. **Deploy first** - Get something live immediately. Proves you can ship.
2. **Add disclaimers** - Protect yourself legally. Shows responsibility.
3. **Collect real data** - Quality > quantity. 5 great cases > 100 placeholder ones.
4. **Test integration** - Verify everything works together.

This order gets you to "impressive portfolio piece" with minimal time investment.

---

## YOU'VE GOT THIS

- The infrastructure is built ✅
- The framework is done ✅
- The deployment is documented ✅
- The data collection is templated ✅

What remains is execution. Which is just time and focus.

**Start with deploying to Render. Do that first. Everything else flows from having something live.**

**Target:** Live URL + 5 cases + disclaimers + updated README = Done for Week 1

Go. 🚀
