# Production Runbook

## Pre-deploy checklist
- CI green (lint, tests, security scan, evaluation gate)
- New image tag published
- `.env` secrets validated in target environment
- Backup completed: `python scripts/backup_chroma.py`

## Deploy
- Trigger `.github/workflows/deploy.yml`
- Choose environment and image tag
- Verify health: `GET /health`
- Verify metrics: `GET /metrics/prometheus`

## Rollback
- Trigger deploy workflow with `rollback_to=<previous_tag>`
- Validate health and error rates for 15 minutes

## Incident response
- Check logs grouped by `trace_id` and `request_id`
- Inspect Grafana dashboard for HTTP 5xx and query failure spikes
- If data corruption suspected, restore latest Chroma backup and redeploy
