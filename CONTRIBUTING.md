# Contributing

Thanks for improving Agent Memory Wiki.

## Local checks

```bash
python3 -m pip install -r requirements-dev.txt
python3 tools/validate.py
python3 -m unittest discover -s tests -v
bash -n scripts/install-hermes.sh
bash -n scripts/wiki-janitor-cron-wrapper.sh.example
shellcheck scripts/install-hermes.sh scripts/wiki-janitor-cron-wrapper.sh.example
```

Run installer and wrapper tests only against disposable homes and vaults. Never use an active Hermes profile or production vault for fixture data.

## Skill architecture

- `obsidian-memory-wiki` is the sole behavioral source of truth.
- Compatibility aliases must stay concise and retain only a minimal safe fallback.
- Put branch-specific detail in the parent’s `references/` or `templates/` directories.
- Do not reintroduce duplicated reset, vault, or janitor implementations.

## Safety and portability

- Do not add private hostnames, tokens, vault paths, delivery IDs, or incident-specific topology.
- Support both Ubuntu and stock macOS; syntax-only checks are not runtime proof.
- Keep unmarked agent output suppressed in scheduled wrappers.
- Preserve explicit profile targeting, path containment, unique backups, and non-destructive vault initialization.
- Add behavioral regression coverage for every installer or wrapper fix.

## Pull requests

Describe the user-visible change, compatibility impact, tests run, and any remaining manual verification. Keep unrelated changes out of the branch.
