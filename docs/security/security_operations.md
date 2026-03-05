# Security Operations

## Secrets
- Never commit `.env`.
- Store production secrets in your platform secret manager.
- Use `API_KEYS_HASHED` in production (SHA-256 hashes).

## API key rotation
1. Add new key hash to `API_KEYS_HASHED`.
2. Deploy and validate clients.
3. Remove old key hash in next deploy.
4. Enable `API_REQUIRE_KEY_ID=true` if using key ids.

## CI scans
- Dependency vulnerabilities: `pip-audit`
- Static checks: `bandit`
- Secret scan: `gitleaks`

## Hardening defaults
- Keep `API_AUTH_ENABLED=true`
- Keep `REJECT_DEFAULT_API_KEYS=true`
- Keep minimum key length >= 24
