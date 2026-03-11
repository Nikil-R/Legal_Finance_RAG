# Quick Start Guide — LegalFinance Chainlit Migration

> **TL;DR:** The frontend has been migrated from Streamlit to Chainlit. The backend is untouched. Here's how to get started.

## Quick Start (5 minutes)

### Option 1: Local Development (Recommended for Development)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Terminal 1 - Start the backend
uvicorn app.main:app --reload --port 8000

# 3. Terminal 2 - Start Chainlit
chainlit run chainlit_app/app.py --port 8501

# 4. Open browser to http://localhost:8501
```

### Option 2: Docker Compose (Recommended for Testing Production Setup)

```bash
# Start everything with one command
docker-compose -f docker/docker-compose.yml up --build

# Open browser to http://localhost:8501

# Stop with:
docker-compose -f docker/docker-compose.yml down
```

## Key Files

| File                                 | Purpose                               |
| ------------------------------------ | ------------------------------------- |
| `chainlit_app/app.py`                | Main Chainlit application             |
| `chainlit_app/api_client.py`         | HTTP client to backend                |
| `chainlit_app/config.py`             | Configuration (environment variables) |
| `chainlit_app/.chainlit/config.toml` | Chainlit UI settings                  |
| `chainlit.md`                        | Welcome screen                        |
| `docker/Dockerfile.chainlit`         | Docker image setup                    |
| `docker/docker-compose.yml`          | Multi-service Docker setup            |

## Environment Variables

Create `.env` or `.env.chainlit`:

```bash
API_BASE_URL=http://localhost:8000          # Backend URL
API_KEY=                                    # Leave empty for no auth
REQUEST_TIMEOUT_SECONDS=60                  # Query timeout
MAX_FILE_SIZE_MB=10                        # Max upload size
ENABLE_TELEMETRY=false                     # Disable Chainlit telemetry
```

## What Changed?

| Old (Streamlit) | New (Chainlit)       | Benefit              |
| --------------- | -------------------- | -------------------- |
| Sync HTTP calls | Async (httpx)        | Better performance   |
| Basic errors    | Categorized errors   | Better user feedback |
| Sidebar panels  | Side panel citations | Cleaner UI           |
| File inputs     | Drag & drop          | Better UX            |

## What Stayed the Same?

✅ **FastAPI Backend** — No changes  
✅ **RAG Pipeline** — No changes  
✅ **Vector Store** — No changes  
✅ **API Endpoints** — No changes  
✅ **Everything Backend** — Untouched

## Testing

### Manual Test

1. Open http://localhost:8501
2. Send a question: "What is Section 80C?"
3. See answer with source citations
4. Upload a PDF file
5. Ask a question about the PDF

### Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "components": {...}
}
```

## Troubleshooting

### "Backend unreachable"

```bash
# Check if backend is running
curl http://localhost:8000/health

# If not running, start it:
uvicorn app.main:app --reload --port 8000
```

### "API authentication failed"

- Check if backend requires API key
- Set `API_KEY` environment variable if needed

### Slow Responses

- Check backend logs: `docker-compose logs api` (if using Docker)
- Verify vector store is indexed

## Documentation

- **[CHAINLIT_README.md](CHAINLIT_README.md)** — Complete setup guide (2000+ lines)
- **[MIGRATION_COMPLETION_REPORT.md](MIGRATION_COMPLETION_REPORT.md)** — What was changed and why
- **[README.md](README.md)** — Project overview

## Common Commands

```bash
# View running containers
docker-compose -f docker/docker-compose.yml ps

# View logs
docker-compose -f docker/docker-compose.yml logs -f chainlit
docker-compose -f docker/docker-compose.yml logs -f api

# Restart a service
docker-compose -f docker/docker-compose.yml restart chainlit

# Build from scratch
docker-compose -f docker/docker-compose.yml up --build

# Clean up
docker-compose -f docker/docker-compose.yml down -v
```

## Need Help?

1. Check **CHAINLIT_README.md** → Troubleshooting section
2. Check backend logs: `docker-compose logs api`
3. Check frontend logs in browser (F12)
4. Check environment variables: `echo $API_BASE_URL`

## What's Next?

- ✅ Migration complete and tested
- 🚀 Ready to deploy to production
- 📈 Plan enhancements: streaming, persistence, user profiles

---

**Last Updated:** March 10, 2026  
**Chainlit Version:** 1.3.0+  
**FastAPI Version:** 0.100.0+
