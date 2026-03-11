# 🚀 LegalFinance AI Frontend - Complete Setup Guide

This guide will walk you through setting up and running the LegalFinance AI frontend with your FastAPI backend.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Backend Configuration](#backend-configuration)
4. [Frontend Configuration](#frontend-configuration)
5. [Running the Application](#running-the-application)
6. [Docker Deployment](#docker-deployment)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Testing Checklist](#testing-checklist)

---

## Prerequisites

- **Node.js 18+** - Download from https://nodejs.org/
- **npm** (comes with Node.js)
- **FastAPI Backend** - Running on http://localhost:8000
- **Git** (optional, for version control)
- **Docker** (optional, for containerized deployment)

### Verify Prerequisites

```bash
node --version      # Should be v18.0.0 or higher
npm --version       # Should be 9.0.0 or higher
```

---

## Local Development Setup

### Step 1: Install Frontend Dependencies

```bash
cd frontend-nextjs
npm install
```

This installs all required packages:

- Next.js, React, TypeScript
- Tailwind CSS for styling
- React Markdown for rendering LLM responses
- React Dropzone for file uploads
- Lucide icons
- UUID for session management
- And more...

**Expected time**: 2-5 minutes

### Step 2: Create Environment Configuration

```bash
cp .env.example .env.local
```

Edit `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: All variables starting with `NEXT_PUBLIC_` are exposed to the browser. Keep sensitive data out of these variables.

### Step 3: Verify Backend Connectivity

Before starting the frontend, ensure your FastAPI backend is running:

```bash
# In a new terminal, check if backend is running
curl -s http://localhost:8000/health | jq .
```

Expected response:

```json
{
  "success": true,
  "checks": {
    "database": "healthy",
    "vector_store": "healthy"
  }
}
```

If you get a connection error, start your FastAPI backend first:

```bash
cd ../  # Go back to root
python -m uvicorn app.main:app --reload --port 8000
```

---

## Backend Configuration

### CORS Configuration (CRITICAL)

Your FastAPI backend MUST allow requests from the frontend. Add this to `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

# Add after creating the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Development
        "http://127.0.0.1:3000",
        # "https://yourdomain.com",   # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Required Backend Endpoints

The frontend expects these endpoints:

| Endpoint  | Method | Purpose                            |
| --------- | ------ | ---------------------------------- |
| `/health` | GET    | Check backend health               |
| `/query`  | POST   | Send question and get RAG response |
| `/upload` | POST   | Upload PDF/TXT/DOCX files          |

#### GET /health

**Response**:

```json
{
  "success": true,
  "checks": {
    "database": "healthy",
    "vector_store": "healthy",
    "llm": "healthy"
  }
}
```

#### POST /query

**Request**:

```json
{
  "question": "What is Section 80C of the Income Tax Act?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**:

```json
{
  "answer": "Section 80C provides deduction for life insurance premiums... [markdown content]",
  "sources": [
    {
      "filename": "Income_Tax_Act_2023.pdf",
      "snippet": "Section 80C permits deduction of...",
      "page_number": 42
    }
  ],
  "metadata": {
    "model": "mistral-7b",
    "timestamp": "2026-03-10T10:30:00Z"
  }
}
```

#### POST /upload

**Request**: Multipart form data with file

**Response**:

```json
{
  "success": true,
  "filename": "Income_Tax_Act_2023.pdf",
  "message": "File uploaded successfully and indexed"
}
```

---

## Frontend Configuration

### Environment Variables

Create or edit `.env.local` in `frontend-nextjs/`:

```env
# ============ REQUIRED ============
NEXT_PUBLIC_API_URL=http://localhost:8000

# ============ OPTIONAL ============
NEXT_PUBLIC_APP_NAME=LegalFinance AI
NEXT_PUBLIC_APP_DESCRIPTION=Indian Legal & Finance AI Research Assistant
```

### TypeScript Types (Optional Customization)

If your backend returns different field names, update `lib/api-client.ts`:

```typescript
// Update interfaces to match your backend response
interface QueryResponse {
  answer: string; // Main LLM response
  sources: Source[]; // Document sources
  metadata: Record<string, unknown>;
}

interface Source {
  filename: string; // Document filename
  snippet: string; // Relevant text excerpt
  page_number?: number; // Page where found (optional)
  score?: number; // Relevance score (optional)
}
```

---

## Running the Application

### Terminal 1: Start FastAPI Backend

```bash
cd ~/legal_finance_rag
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

Wait for output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Start Next.js Frontend

```bash
cd ~/legal_finance_rag/frontend-nextjs
npm run dev
```

Wait for output:

```
▲ Next.js 14.1.0
- Local:        http://localhost:3000
- Environments: .env.local
```

### Open in Browser

1. Backend Swagger UI: http://localhost:8000/docs
2. **Frontend** (Main): **http://localhost:3000** ← Start here
3. API Health: http://localhost:8000/health

---

## Docker Deployment

### Build Docker Image

```bash
cd frontend-nextjs
docker build -t legal-finance-frontend:latest .
```

### Run with Docker Compose (Full Stack)

From the root directory:

```bash
docker-compose -f docker/docker-compose.yml \
               -f frontend-nextjs/docker-compose.override.yml \
               up -d
```

This starts:

- **Backend** on http://localhost:8000
- **Frontend** on http://localhost:3000
- **Chroma** (Vector DB) on http://localhost:8001

### View Logs

```bash
# Frontend logs
docker logs legal-finance-frontend

# Backend logs
docker logs legal-finance-api

# All logs
docker-compose logs -f
```

### Stop Containers

```bash
docker-compose down
```

### Clean Up

```bash
# Remove images
docker-compose down --rmi all

# Remove volumes
docker-compose down -v
```

---

## Production Deployment

### Option 1: Vercel (Recommended for SaaS)

Vercel provides the easiest deployment for Next.js applications.

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend-nextjs
vercel

# Follow prompts to connect GitHub and configure
```

**Set Environment Variable in Vercel**:

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
3. Redeploy

### Option 2: Docker + Cloud Platform (AWS, GCP, etc.)

```bash
# Build production image
docker build -t legal-finance-frontend:prod .

# Tag for registry
docker tag legal-finance-frontend:prod my-registry/legal-finance-frontend:latest

# Push to registry
docker push my-registry/legal-finance-frontend:latest
```

### Option 3: Self-Hosted (Linux Server)

```bash
# SSH into your server
ssh user@your-server.com

# Clone repository
git clone <your-repo>
cd legal_finance_rag/frontend-nextjs

# Install dependencies
npm install

# Create .env.local with production URL
echo "NEXT_PUBLIC_API_URL=https://api.yourdomain.com" > .env.local

# Build production version
npm run build

# Install PM2 for process management
npm install -g pm2

# Start application
pm2 start "npm start" --name legal-finance-frontend

# Enable auto-restart on reboot
pm2 startup
pm2 save
```

### Option 4: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/legal-finance

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/legal-finance /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## Troubleshooting

### Issue: "Cannot GET /"

**Cause**: Frontend not running  
**Solution**:

```bash
cd frontend-nextjs
npm run dev
```

### Issue: Backend connection error in chat

**Cause**: Backend down or CORS not configured  
**Solution**:

1. Check backend: `curl http://localhost:8000/health`
2. Verify CORS config in `app/main.py`
3. Check `NEXT_PUBLIC_API_URL` environment variable

### Issue: "Module not found" errors

**Cause**: Dependencies not installed  
**Solution**:

```bash
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: Port 3000 already in use

**Cause**: Another process using port 3000  
**Solution**:

```bash
# Find and kill process (macOS/Linux)
lsof -i :3000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

### Issue: Styling looks broken

**Cause**: Tailwind CSS not compiling  
**Solution**:

```bash
npm install
npm run dev
# Clear browser cache: Ctrl+Shift+Delete
```

### Issue: Files won't upload

**Cause**: File too large or unsupported type  
**Solution**:

- Max file size: 200MB
- Supported types: PDF, TXT, DOCX
- Check backend `/upload` endpoint is working

---

## Testing Checklist

### Before Going to Production

#### Functional Tests

- [ ] App loads on http://localhost:3000
- [ ] Welcome screen displays with 4 starter questions
- [ ] Health badge shows green (backend healthy)
- [ ] Can type a message and send it
- [ ] Response appears in chat
- [ ] Response markdown renders correctly (headings, bold, lists, tables)
- [ ] Citation markers [1], [2] appear in response
- [ ] Right panel shows sources
- [ ] File upload works via drag & drop
- [ ] File upload works via click
- [ ] Uploaded file appears in sidebar
- [ ] Copy button works on messages
- [ ] "New Chat" button clears conversation

#### Error Handling Tests

- [ ] Stop backend, health badge turns red
- [ ] Stop backend, error banner appears
- [ ] Upload invalid file type shows error
- [ ] Upload file > 200MB shows error
- [ ] Backend timeout shows error message
- [ ] Safety-blocked query shows warning

#### Performance Tests

- [ ] Page loads in < 2 seconds
- [ ] Chat scrolls smoothly
- [ ] File upload shows progress
- [ ] No console errors (F12)

#### Browser Compatibility

- [ ] Chrome/Edge latest version
- [ ] Firefox latest version
- [ ] Safari latest version
- [ ] Mobile Chrome
- [ ] Mobile Safari (iOS)

#### Responsive Design

- [ ] Desktop: 3-panel layout works
- [ ] Tablet: Layout adapts properly
- [ ] Mobile: Sidebar accessible, chat visible

### Smoke Tests (Production)

```bash
# Test health check
curl -s https://api.yourdomain.com/health | jq .

# Test query
curl -X POST https://api.yourdomain.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Test question",
    "session_id": "test-session"
  }' | jq .

# Test upload
curl -X POST https://api.yourdomain.com/upload \
  -F "file=@test.pdf"
```

---

## Next Steps

1. **Customize the Theme** - Edit `tailwind.config.ts`
2. **Add Analytics** - Integrate with Mixpanel, Segment, etc.
3. **Implement Features** - Conversation history, export chat, settings page
4. **Set Up Monitoring** - Use Sentry, LogRocket for error tracking
5. **Performance Tuning** - Use Lighthouse to optimize

---

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [React Documentation](https://react.dev/)

---

**Need help?** Check the main README.md or review the codebase comments.

**Ready to deploy?** Follow the Docker or Production sections above.

**Happy coding! 🚀**
