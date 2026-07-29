<div align="center">

# Agent Memory Wiki

**Obsidian-powered daily logs, session logs, and context-reset handoffs for AI agents.**

[![Validate](https://github.com/cobibean/agent-memory-wiki/actions/workflows/validate.yml/badge.svg)](https://github.com/cobibean/agent-memory-wiki/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agent--skills-v2.0.0-7C3AED.svg)](skills/)
[![Obsidian](https://img.shields.io/badge/Obsidian-vault-8B5CF6.svg)](https://obsidian.md/)
[![Hermes](https://img.shields.io/badge/Hermes-%2Fprepforreset-111827.svg)](https://hermes-agent.nousresearch.com/docs)
[![No Secrets](https://img.shields.io/badge/secrets-never%20log%20values-red.svg)](docs/security-and-secret-hygiene.md)

<table>
  <tr>
    <td align="center"><a href="#quick-start"><b>Quick Start</b></a><br/>install the skills</td>
    <td align="center"><a href="#make-prepforreset-a-slash-command"><b>/prepforreset</b></a><br/>make it a command</td>
    <td align="center"><a href="#copy-paste-prompt-for-your-agent"><b>Agent Prompt</b></a><br/>paste into your agent</td>
    <td align="center"><a href="#optional-wiki-janitor"><b>Wiki Janitor</b></a><br/>optional reconciliation</td>
  </tr>
</table>

Created by **Jacobi Lange** — [@cobi_bean](https://twitter.com/cobi_bean) / [GitHub @cobibean](https://github.com/cobibean)

</div>

---

## What this is

Agent Memory Wiki is a portable skill bundle for giving AI agents a durable, human-readable operating memory in an Obsidian vault.

It turns this:

> “I’m about to reset the context window. Preserve what matters.”

into this:

```text
Daily Logs/2026-06-13.md
Session Logs/2026-06-13-agent-memory-wiki-open-source.md
Janitor Reports/2026-06-14-last-24h.md
```

The core command is **`/prepforreset`**: a context-reset workflow that writes a curated Daily Log and Session Log, then returns a short copy/paste handoff for the next agent context.

This is not raw transcript dumping. The notes are meant to help humans and future agents recover the work: decisions, rationale, alternatives, verified outcomes, artifacts, blockers, open loops, gotchas, and source references.

> **Version 2.0.0:** one canonical `obsidian-memory-wiki` skill now owns the behavior. The familiar `obsidian`, `prepforreset`, and `wikijanitor` names remain as small compatibility aliases, so existing workflows keep working without maintaining three competing implementations.

## The bundle

| Skill | Role | What it does |
| --- | --- | --- |
| [`obsidian-memory-wiki`](skills/note-taking/obsidian-memory-wiki/SKILL.md) | **Canonical** | Owns vault operations, reset capture, janitor behavior, safety rules, templates, and fleet rollout guidance. |
| [`obsidian`](skills/note-taking/obsidian/SKILL.md) | Compatibility alias | Routes low-level vault operations to the canonical parent. |
| [`prepforreset`](skills/note-taking/prepforreset/SKILL.md) | Compatibility alias | Keeps `/prepforreset` working for daily/session capture and the final handoff. |
| [`wikijanitor`](skills/note-taking/wikijanitor/SKILL.md) | Compatibility alias | Keeps manual janitor/reconciliation workflows working. |

New automation and scheduled jobs should load only:

```text
--skills obsidian-memory-wiki
```

## Quick start

### Option A — Hermes Agent

#### Requirements

- Bash
- Python 3
- [Hermes Agent](https://hermes-agent.nousresearch.com/docs)
- An existing Markdown/Obsidian vault, or permission to initialize one

Clone the repository, then install the bundle into a Hermes profile:

```bash
git clone https://github.com/cobibean/agent-memory-wiki.git
cd agent-memory-wiki

# Existing vault, named profile
bash scripts/install-hermes.sh \
  --profile my-agent \
  --vault "$HOME/Documents/Obsidian/agent-wikis/my-agent-wiki"
```

Or create a safe starter vault at the same time:

```bash
bash scripts/install-hermes.sh \
  --profile my-agent \
  --vault "$HOME/Documents/Obsidian/agent-wikis/my-agent-wiki" \
  --init-vault
```

For the default profile, omit `--profile`. To target an exact Hermes home directly, use `--hermes-home PATH`.

The installer:

- treats explicit `--profile` or `--hermes-home` as authoritative over inherited `HERMES_HOME`;
- rejects unresolved interpolation-like paths containing literal `${...}` segments;
- supports spaces and special characters in paths;
- installs the canonical parent and all three aliases by default;
- writes the vault path to `skills.config.obsidian_memory_wiki.vault_path` in the target `config.yaml`;
- keeps `.env` reserved for secrets instead of normal skill configuration;
- creates a unique timestamped backup before replacing an existing package;
- keeps relevant configuration and backup files private.

Use `--dry-run` to inspect the resolved profile, destinations, and vault before making changes. Use `--no-aliases` for a parent-only install.

Start a fresh session—or run `/reload-skills` where your Hermes version supports it—then try:

```text
/prepforreset
```

See [`docs/installation.md`](docs/installation.md) for upgrades, rollback, generic-agent installation, and readiness checks.

### Option B — Any agent that supports Markdown skills

Copy the canonical package into the skill directory your agent runtime uses:

```text
skills/note-taking/obsidian-memory-wiki/
```

Copy the compatibility aliases too if you want the familiar command names:

```text
skills/note-taking/obsidian/
skills/note-taking/prepforreset/
skills/note-taking/wikijanitor/
```

Configure an absolute vault path using your runtime's non-secret skill configuration. If no native config system exists, `OBSIDIAN_VAULT_PATH` remains the compatibility fallback.

Create—or allow the installer to create—the standard folders:

```text
Daily Logs/
Session Logs/
Janitor Reports/
Templates/
```

Then map `/prepforreset` to the Reset Preparation phase of `obsidian-memory-wiki`.

## Make `prepforreset` a slash command

### Hermes

Hermes exposes installed skills as slash commands by normalizing each skill's frontmatter `name`.

Because the compatibility skill is named:

```yaml
name: prepforreset
```

it becomes:

```text
/prepforreset
```

Start a fresh session or refresh the skill command cache after installation. If a chat platform does not show the command in autocomplete, try typing `/prepforreset` manually; some platform menus are capped even when a skill is installed and dispatchable.

The compatibility alias loads the canonical parent and runs its **Reset Preparation** phase. New scripts and cron jobs should still name `obsidian-memory-wiki` directly.

### Generic agents

If your runtime has a command registry, define the equivalent of:

```text
/prepforreset -> Load obsidian-memory-wiki and run Reset Preparation:
resolve the configured vault, update the Daily Log and Session Log,
verify the files, then return a lean handoff.
```

If your runtime has no command registry, keep the prompt below as a reusable trigger.

## Copy-paste prompt for your agent

Paste this after installing the bundle:

```md
You have access to Agent Memory Wiki v2.

- `obsidian-memory-wiki` is the canonical skill.
- `obsidian`, `prepforreset`, and `wikijanitor` are compatibility aliases.

When I type `/prepforreset` or say “prep for reset” / “prepare for a context window”:

1. Load and follow `obsidian-memory-wiki`.
2. Run its Reset Preparation phase.
3. Resolve the vault from the runtime's native skill configuration. Use
   `OBSIDIAN_VAULT_PATH` only as a compatibility fallback. If neither provides
   a concrete absolute path, stop and ask me; never guess a vault.
4. Keep every write inside the resolved vault root.
5. Search existing Daily Logs and Session Logs before creating new notes.
6. Update or create:
   - `Daily Logs/YYYY-MM-DD.md`
   - `Session Logs/YYYY-MM-DD-short-topic-slug.md`
7. Curate rather than dump the transcript. Capture the goal, current status,
   decisions, rationale, alternatives, artifacts, commands/tests and real
   outcomes, verification, blockers, lessons, and next concrete actions.
8. Never write secret values. Reference only credential locations such as
   `.env`, Keychain, or secret-manager paths.
9. Add backlinks between the daily and session notes.
10. Verify both artifacts, then return their paths and a lean copy/paste handoff.

For manual vault operations, use the Vault Operations phase. For `/wikijanitor`
or scheduled reconciliation, use the Wiki Janitor Maintenance phase.
```

A longer standalone version lives at [`docs/agent-copy-paste-prompt.md`](docs/agent-copy-paste-prompt.md).

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

Do not silently point every agent at one shared vault. Do not use an entire code repository as a vault merely because it contains Markdown.

`--init-vault` creates the starter structure without overwriting existing files. Open the vault in Obsidian and enable the built-in **Daily Notes** and **Templates** plugins if you want Obsidian-native shortcuts.

## What gets written

| Artifact | Purpose |
| --- | --- |
| `Daily Logs/YYYY-MM-DD.md` | Standalone day summary with decisions, verified outcomes, open loops, routing candidates, and links. |
| `Session Logs/YYYY-MM-DD-short-topic-slug.md` | Deeper session distillation with state, commands/tests, verification, blockers, and next actions. |
| `Janitor Reports/YYYY-MM-DD-...md` | Optional reconciliation report describing reviewed sources, routine fixes, gaps, uncertainty, and follow-up. |
| Chat handoff | Lean bridge into the next context window; the durable details stay in the vault. |

## Design principles

- **Curate, don't dump.** Preserve durable understanding, not transcript volume.
- **Human-readable first.** Clear headings, dates, wikilinks, rationale, and source references help both people and agents.
- **Operating memory, not universal truth.** Repositories, manifests, issue trackers, and domain systems remain authoritative for their own artifacts; the wiki points back to them.
- **No silent mutation outside the vault.** Routing candidates may suggest memory, skill, manifest, or backlog updates, but those stores change only when separately requested.
- **Secrets are never note content.** Record credential locations, never credential values.
- **One vault per persistent agent by default.** Shared access requires an explicit design decision.
- **Portable by default.** The package does not assume a private fleet, host path, vendor runtime, `flock`, or GNU `timeout`.

## Optional Wiki Janitor

The Wiki Janitor is a conservative reliability layer for missed or incomplete capture. It is optional; manual `/prepforreset` is useful for most persistent agents, while recurring model-powered reconciliation is justified only when activity and missed-capture risk warrant it.

The included wrapper:

- runs on Linux and stock macOS;
- prevents overlap with an atomic profile-local lock when `flock` is unavailable;
- uses a bounded Python subprocess fallback when `timeout`/`gtimeout` is unavailable;
- starts Hermes in its own process group and terminates the complete group on timeout;
- invokes Hermes directly with an explicit profile and argument array;
- accepts only one exact silent marker or one complete ordered notify envelope;
- suppresses malformed, mixed, partial, duplicate, reversed, and unmarked output;
- never forwards model-authored digest text;
- emits only a fixed, secret-free notification when review-worthy findings exist.

Routine-only reconciliation is silent. The newest protected Janitor Report—not raw cron output—is the review surface.

Follow [`docs/scheduling-wikijanitor.md`](docs/scheduling-wikijanitor.md) and verify a real created report plus delivery behavior, not only scheduler status.

## Updating and rollback

Update the checkout, then rerun the installer with the same explicit profile and vault:

```bash
git pull --ff-only

bash scripts/install-hermes.sh \
  --profile my-agent \
  --vault "/absolute/path/to/my-agent-wiki"
```

Each real install creates a unique timestamped backup under the target Hermes home and preserves replaced skills plus the previous profile `config.yaml` when present. The installer prints the exact backup location.

To roll back:

1. Stop or isolate only the affected session/gateway if needed.
2. Restore the desired skill directories and `config.yaml` from the printed backup.
3. Start a fresh session or reload skills.
4. Verify the resolved vault before writing.

The installer never deletes vault notes.

See [`CHANGELOG.md`](CHANGELOG.md) for v2 compatibility changes.

## Repository layout

```text
skills/note-taking/obsidian-memory-wiki/   Canonical skill, references, templates
skills/note-taking/obsidian/               Vault-operations compatibility alias
skills/note-taking/prepforreset/            Reset-capture compatibility alias
skills/note-taking/wikijanitor/             Janitor compatibility alias
scripts/install-hermes.sh                   Profile-aware installer
scripts/wiki-janitor-cron-wrapper.sh.example
                                            Portable scheduled wrapper
tests/                                      Behavioral regression tests
tools/validate.py                           Package/link/secret validation
docs/                                       Installation and operating guides
examples/                                   Native Hermes config example
```

## Documentation

| Guide | Purpose |
| --- | --- |
| [`docs/installation.md`](docs/installation.md) | Hermes and generic-agent installation, upgrade, rollback, and readiness. |
| [`docs/architecture.md`](docs/architecture.md) | Canonical-parent architecture and compatibility model. |
| [`docs/slash-command-setup.md`](docs/slash-command-setup.md) | How to expose and verify `/prepforreset`. |
| [`docs/agent-copy-paste-prompt.md`](docs/agent-copy-paste-prompt.md) | Full reusable setup prompt for another agent. |
| [`docs/scheduling-wikijanitor.md`](docs/scheduling-wikijanitor.md) | Optional scheduled janitor setup and output contract. |
| [`docs/security-and-secret-hygiene.md`](docs/security-and-secret-hygiene.md) | Path safety, secret handling, permissions, and public-repo hygiene. |
| [`CHANGELOG.md`](CHANGELOG.md) | Release history and v2 migration notes. |

## Validation

Install the pinned development dependency, then run the same core checks used by CI:

```bash
python3 -m pip install -r requirements-dev.txt
python3 tools/validate.py
python3 -m unittest discover -s tests -v
python3 -m compileall -q tools tests
bash -n scripts/install-hermes.sh
bash -n scripts/wiki-janitor-cron-wrapper.sh.example
shellcheck scripts/install-hermes.sh scripts/wiki-janitor-cron-wrapper.sh.example
```

CI exercises the package on Ubuntu and macOS, including explicit profile targeting, paths with spaces and special characters, idempotent replacement, restrictive config permissions, portable lock/timeout behavior, descendant cleanup, marker parsing, raw-output suppression, and live Hermes argument parsing where available.

## Security

Agent Memory Wiki is designed to preserve useful context without becoming a credential archive.

- Never store tokens, passwords, private keys, raw `.env` contents, OAuth responses, or credential-bearing URLs in notes.
- Resolve and verify the vault root before every write.
- Reject writes that escape the resolved vault.
- Keep profile configuration and backups private.
- Treat model and tool output as sensitive until the wrapper's exact protocol has been validated.

Read [`docs/security-and-secret-hygiene.md`](docs/security-and-secret-hygiene.md) before deploying the package in a shared, business, or client environment.

## License

MIT. See [`LICENSE`](LICENSE).
