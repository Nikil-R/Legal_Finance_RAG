# Render.com Deployment Guide

**Get your Legal Finance RAG system live in 15 minutes**

---

## Why Render.com?

- ✅ **Free tier** - No credit card required for starter account
- ✅ **Permanent free tier** - Doesn't require paid upgrade after trial
- ✅ **GitHub integration** - Auto-deploys when you push code
- ✅ **Auto HTTPS** - Free SSL certificates included
- ✅ **Custom domain** - Free subdomain provided
- ✅ **Student-friendly** - Perfect for portfolio projects

---

## Prerequisites

Have these ready before starting:

- [ ] GitHub repository with your code (public or private)
- [ ] `requirements.txt` file with all Python dependencies
- [ ] `app/main.py` with FastAPI application
- [ ] GROQ API key (get free at https://console.groq.com)
- [ ] Render.com account (create with GitHub)

---

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. Ensure `requirements.txt` exists and has all dependencies:

```bash
# Generate requirements if missing
pip freeze > requirements.txt
```

2. Add this file `render.yaml` to your repository root:

```yaml
# render.yaml
services:
  - type: web
    name: legal-finance-rag
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

3. Verify `app/main.py` has health endpoint:

```python
@app.get("/health")
async def health():
    return {"status": "alive"}
```

4. Commit and push to GitHub:

```bash
git add render.yaml requirements.txt
git commit -m "Add Render.com deployment configuration"
git push origin main
```

### Step 2: Create Render.com Account

1. Go to [Render.com](https://render.com)
2. Click "Sign up"
3. Select "Sign up with GitHub"
4. Authorize Render to access your GitHub account
5. Complete signup

### Step 3: Create Web Service

1. After logging in, click "New +" → "Web Service"
2. Select your GitHub repository
3. Render asks for configuration:
   - **Name:** `legal-finance-rag` (or your choice)
   - **Environment:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

### Step 4: Add Environment Variables

1. In Render dashboard, find your service
2. Click "Environment" tab
3. Add these environment variables:
   - `GROQ_API_KEY`: Your API key from console.groq.com
   - Any other API keys your app needs
4. Click "Save"

### Step 5: Deploy

1. Click "Create Web Service"
2. Render shows build logs in real-time
3. Wait for "✓ Deploy successful" message (usually 3-5 minutes)
4. You get a public URL like: `https://legal-finance-rag.onrender.com`

---

## Verify Deployment

### Test Health Endpoint

```bash
curl https://legal-finance-rag.onrender.com/health
```

Expected response:

```json
{ "status": "alive" }
```

### Test Full System

Open in browser or use curl:

```bash
curl "https://legal-finance-rag.onrender.com/query?question=What%20is%20GST%20rate%20for%20pizza"
```

---

## Performance Notes

### Cold Start

First request after inactivity takes 30-45 seconds (free tier limitation).

- Document this in README
- Consider mentioning to recruiters: "Free tier with cold start behavior"
- After first request, responses are fast

### Keeping Warm

Optional: Use UptimeRobot (free) to hit `/health` every 5 minutes to keep it warm

### Optimization

For portfolio purposes:

- Use lightweight responses for demos
- Cache common queries
- Show performance metrics from actual cloud deployment

---

## Auto-Deployment from GitHub

Every time you push to main branch:

1. Render detects changes
2. Automatically rebuilds and redeploys
3. Zero manual intervention needed
4. Deployed within 2-3 minutes

```bash
# Make changes locally
git add .
git commit -m "Add better error handling"
git push origin main  # <- Automatically deploys!
```

---

## Shared Public URL Format

Once deployed, your system is at:

```
https://legal-finance-rag.onrender.com
```

Perfect for:

- Adding to resume
- Sharing with recruiters
- Portfolio website link
- GitHub README demo link

---

## Common Issues & Fixes

### Issue: "Build failed"

**Fix:** Check build logs for errors, usually missing dependencies

```bash
# Make sure requirements.txt has everything
pip install -r requirements.txt  # Test locally
```

### Issue: "Application failed to start"

**Fix:** Verify FastAPI app starts locally:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue: "502 Bad Gateway"

**Fix:** Usually cold start or app crashed. Wait 30 seconds and try again.

### Issue: "Port already in use" in logs

**Fix:** Environment variable issue. Ensure `--port $PORT` in start command.

---

## Next Steps After Deployment

1. ✅ Test public URL in browser
2. ✅ Add live URL to GitHub README
3. ✅ Add to resume and LinkedIn
4. ✅ Share in portfolio
5. ✅ Monitor logs and uptime
6. ✅ Continue improving based on real access

---

## Advanced: Custom Domain (Optional)

If you want your own domain:

1. Use free domain from Freenom or similar
2. In Render dashboard: Custom Domain
3. Add DNS records as shown
4. Wait 5-10 minutes for DNS propagation

Not required for portfolio - free Render subdomain is perfectly fine!

---

## Monitoring Your Deployment

Once live, monitor these:

- **Uptime:** Check via UptimeRobot (free)
- **Logs:** View in Render dashboard
- **Performance:** Note response times
- **Errors:** Set up simple monitoring

Add these metrics to your portfolio:

- "99% uptime on free tier"
- "Sub-2 second response time"
- "[X] beta testers"

---

**You're now ready to deploy! Your system will be live at a public URL ready to show recruiters. 🚀**
