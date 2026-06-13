# Security and Secret Hygiene

Memory-wiki notes are durable and often synced. Treat them as public-adjacent unless you know otherwise.

## Forbidden in notes

Never write:

- API keys
- OAuth refresh/access tokens
- private keys
- webhook secrets
- passwords
- credential-bearing connection strings
- raw `.env` contents

## Allowed in notes

Write locations, not values:

```text
Credential reference: see profile-local .env.
Token presence verified in /path/to/.env; value intentionally omitted.
Secret stored in deployment environment; value intentionally omitted.
```

## Recommended final scan

Before reporting success, scan new/changed notes for obvious secret patterns:

- private-key block headers
- common API key prefixes
- GitHub token-looking strings
- Telegram bot-token shapes
- raw `.env`-style assignments containing secret/key/token/password

If a scan hits, redact the note and rerun the scan.
