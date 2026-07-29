# Agent Memory Wiki

**Portable Obsidian-backed operating memory for AI agents.**

[![Validate](https://github.com/cobibean/agent-memory-wiki/actions/workflows/validate.yml/badge.svg)](https://github.com/cobibean/agent-memory-wiki/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Agent Memory Wiki gives an agent three coordinated workflows:

- safe Markdown/Obsidian vault operations;
- `/prepforreset` daily and session capture with a lean handoff;
- an optional scheduled janitor that reconciles missed or incomplete capture.

Bundle version 2.0.0 uses one canonical skill, `obsidian-memory-wiki`. The familiar `obsidian`, `prepforreset`, and `wikijanitor` skills are small compatibility aliases so existing slash commands keep working without maintaining three competing implementations.

## What it is—and is not

The wiki is curated operating memory. It should preserve decisions, verified outcomes, artifacts, blockers, and next actions without dumping transcripts.

It is **not** a universal source of truth. Project repositories, manifests, issue trackers, and domain systems remain authoritative for their own artifacts. The wiki points back to them.

It is also not a secret store. Never write tokens, passwords, private keys, raw `.env` contents, or credential-bearing URLs into notes.

## Quick start for Hermes

Prerequisites:

- Bash and Python 3;
- Hermes Agent;
- an existing Markdown/Obsidian vault, or permission to initialize one.

```bash
git clone https://github.com/cobibean/agent-memory-wiki.git
cd agent-memory-wiki

# Existing vault, named profile
bash scripts/install-hermes.sh \
  --profile my-agent \
  --vault "$HOME/Documents/Obsidian/agent-wikis/my-agent-wiki"

# Or create a starter vault safely
bash scripts/install-hermes.sh \
  --profile my-agent \
  --vault "$HOME/Documents/Obsidian/agent-wikis/my-agent-wiki" \
  --init-vault
```

`--profile` is authoritative and overrides an inherited `HERMES_HOME`. Use `--hermes-home PATH` when you intentionally want an exact destination. Use `--dry-run` to inspect resolved destinations first.

The installer writes the vault path to `skills.config.obsidian_memory_wiki.vault_path` in the target profile `config.yaml`; `.env` remains reserved for secrets.

The default install includes the canonical parent and all three compatibility aliases. Use `--no-aliases` for parent-only installations.

Then start a new session or run `/reload-skills` where available and try:

```text
/prepforreset
```

See [Installation](docs/installation.md) for upgrade, rollback, generic-agent, and readiness details.

## Recommended vault shape

Use one isolated vault per persistent agent:

```text
<agent>-wiki/
├── Home.md
├── Vault Guide.md
├── Daily Logs/
├── Session Logs/
├── Janitor Reports/
├── Templates/
└── .obsidian/
```

Do not point every agent at one shared vault. Do not automatically use an entire code repository as a vault merely because it contains Markdown.

`--init-vault` creates this starter structure without overwriting existing files. Open it in Obsidian and enable the built-in Daily Notes and Templates plugins.

## Canonical skill and commands

| Surface | Purpose |
|---|---|
| `obsidian-memory-wiki` | Canonical behavior and source of truth |
| `/obsidian` | Compatibility alias for vault operations |
| `/prepforreset` | Compatibility alias for reset capture |
| `/wikijanitor` | Compatibility alias for manual reconciliation |

New cron jobs and automation must load only:

```text
--skills obsidian-memory-wiki
```

## Optional scheduled janitor

A recurring janitor is opt-in. Manual reset capture is useful for most persistent agents; a daily model-powered reconciliation is justified only when activity and missed-capture risk warrant it.

The included wrapper:

- runs on Linux and stock macOS;
- uses a portable atomic-directory lock;
- uses a Python process-group timeout, with `timeout`/`gtimeout` fallback when Python is unavailable;
- preserves the selected profile;
- validates an exact marker envelope but emits only a constant wrapper-authored notification;
- suppresses all unmarked raw output.

Follow [Scheduling Wiki Janitor](docs/scheduling-wikijanitor.md) and verify a real created report and delivery—not only scheduler status.

## Updating and rollback

To update:

```bash
git pull --ff-only
bash scripts/install-hermes.sh --profile my-agent --vault "/path/to/vault"
```

Each real install creates a unique timestamped backup under the target Hermes home and backs up replaced skills plus the prior profile `config.yaml` when present. The installer prints the exact backup path.

To roll back, stop the affected gateway/session, restore the desired skill directories and `config.yaml` from that backup, then start a new session or reload skills. The installer never deletes vault notes.

See [CHANGELOG.md](CHANGELOG.md) for compatibility changes.

## Validation

```bash
python3 -m pip install -r requirements-dev.txt
python3 tools/validate.py
python3 -m unittest discover -s tests -v
bash -n scripts/install-hermes.sh
bash -n scripts/wiki-janitor-cron-wrapper.sh.example
shellcheck scripts/install-hermes.sh scripts/wiki-janitor-cron-wrapper.sh.example
```

CI runs behavioral tests on both Ubuntu and macOS, including profile targeting, paths with spaces, idempotent replacement, portable timeout behavior, lock contention, and output-marker safety.

## Repository layout

```text
skills/note-taking/obsidian-memory-wiki/   Canonical skill, references, templates
skills/note-taking/{obsidian,prepforreset,wikijanitor}/
                                           Compatibility aliases
scripts/install-hermes.sh                  Profile-aware installer
scripts/wiki-janitor-cron-wrapper.sh.example
                                           Portable scheduled wrapper
tests/                                     Behavioral regression tests
tools/validate.py                          Schema/link/secret/package validation
docs/                                      Installation and operating guides
```

## Documentation

- [Installation](docs/installation.md)
- [Architecture](docs/architecture.md)
- [Slash-command setup](docs/slash-command-setup.md)
- [Scheduling Wiki Janitor](docs/scheduling-wikijanitor.md)
- [Security and secret hygiene](docs/security-and-secret-hygiene.md)
- [Generic agent copy/paste prompt](docs/agent-copy-paste-prompt.md)

## License

MIT. See [LICENSE](LICENSE).
