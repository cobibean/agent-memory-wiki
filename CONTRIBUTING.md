# Contributing

Thanks for improving Agent Memory Wiki.

## Local checks

```bash
python3 tools/validate.py
```

## Skill style

- Keep each `SKILL.md` focused on reusable agent behavior.
- Put long setup explanations in `docs/` instead of bloating the skill.
- Do not add private hostnames, tokens, vault paths, or incident-specific operational history.
- Prefer examples with placeholders like `/path/to/Obsidian Vault`.
- Keep secret handling conservative: locations are OK, values are not.

## Commit style

Use conventional-style subjects when practical:

```text
docs: clarify slash command setup
fix: tighten janitor secret scan guidance
feat: add generic agent install notes
```
