# Data Safety and Compliance

## PII handling
- `PII_REDACTION_ENABLED=true` redacts common PII in user queries before pipeline execution.
- Redaction covers email, phone, PAN, and Aadhaar patterns.

## Retention
- User document retention policy: `USER_DOC_RETENTION_DAYS` (default 30).
- Enforce periodic deletion in storage lifecycle jobs.

## Access control
- Protect all write/query routes with API key authentication.
- Scope API keys by environment and rotate regularly.

## Logging
- Logs include request and trace IDs, not raw secret values.
- Avoid logging full user payloads in production.
