# Security Policy

Agent Memory Wiki is a note-writing workflow. Its biggest practical risk is accidentally writing sensitive information into a durable vault.

## Never store secret values in notes

Do not write:

- API keys
- OAuth refresh/access tokens
- private keys
- webhook secrets
- passwords
- credential-bearing connection strings
- raw `.env` contents

Safe examples:

```text
Token presence verified in profile-local .env; value intentionally omitted.
Credential reference: see deployment secret manager.
```

## Reporting issues

Please open a GitHub issue for non-sensitive bugs. If a report needs sensitive details, remove the secret values first and describe only the shape of the issue.
