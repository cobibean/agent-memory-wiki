<div align="center">

# Agent Memory Wiki

**Obsidian-powered daily logs, session logs, and context-reset handoffs for AI agents.**

[![Validate](https://github.com/cobibean/agent-memory-wiki/actions/workflows/validate.yml/badge.svg)](https://github.com/cobibean/agent-memory-wiki/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agent Skills](https://img.shields.io/badge/agent--skills-ready-7C3AED.svg)](skills/)
[![Obsidian](https://img.shields.io/badge/Obsidian-vault-8B5CF6.svg)](https://obsidian.md/)
[![Hermes](https://img.shields.io/badge/Hermes-%2Fprepforreset-111827.svg)](https://hermes-agent.nousresearch.com/docs)
[![No Secrets](https://img.shields.io/badge/secrets-never%20log%20values-red.svg)](docs/security-and-secret-hygiene.md)

<table>
  <tr>
    <td align="center"><a href="#quick-start"><b>Quick Start</b></a><br/>install the skills</td>
    <td align="center"><a href="#make-prepforreset-a-slash-command"><b>/prepforreset</b></a><br/>make it a command</td>
    <td align="center"><a href="#copy-paste-prompt-for-your-agent"><b>Agent Prompt</b></a><br/>paste into your agent</td>
    <td align="center"><a href="docs/scheduling-wikijanitor.md"><b>Wiki Janitor</b></a><br/>optional nightly review</td>
  </tr>
</table>

Created by **Jacobi Lange** — [@cobi_bean](https://twitter.com/cobi_bean) / [GitHub @cobibean](https://github.com/cobibean)

</div>

---

## What this is

Agent Memory Wiki is a small skill bundle for giving AI agents a durable, human-readable memory trail in an Obsidian vault.

It turns this:

> “I’m about to reset the context window. Preserve what matters.”

into this:

```text
Daily Logs/2026-06-13.md
Session Logs/2026-06-13-agent-memory-wiki-open-source.md
Janitor Reports/2026-06-14-last-24h.md
```

The core command is **`/prepforreset`**: a context-reset workflow that writes a curated Daily Log and Session Log, then returns a short copy/paste handoff for the next agent context.

This is not raw transcript dumping. The notes are meant to be useful to humans and future agents: decisions, rationale, alternatives, artifacts, open loops, gotchas, and source references.

## The bundle

| Skill | Required? | What it does |
| --- | --- | --- |
| [`obsidian`](skills/note-taking/obsidian/SKILL.md) | Yes | Low-level vault operations: resolve the vault path, read/search/write notes, stay inside the vault root. |
| [`prepforreset`](skills/note-taking/prepforreset/SKILL.md) | Yes | Manual context-reset capture: creates/updates Daily Logs and Session Logs, then returns a lean handoff. |
| [`wikijanitor`](skills/note-taking/wikijanitor/SKILL.md) | Optional | Scheduled/manual reconciliation: reviews recent sessions and existing notes, writes Janitor Reports, flags gaps. |

## Quick start

### Option A — Hermes Agent

Clone this repo, then install the skills into your Hermes profile:

```bash
git clone https://github.com/cobibean/agent-memory-wiki.git
cd agent-memory-wiki

# Pick your Obsidian vault path.
export OBSIDIAN_VAULT_PATH="$HOME/Documents/Obsidian Vault"

# Default profile install. For a named profile, add: --profile my-profile
bash scripts/install-hermes.sh --vault "$OBSIDIAN_VAULT_PATH"
```

Then reload skills in your running Hermes session/gateway if needed:

```text
/reload-skills
```

Now try:

```text
/prepforreset
```

### Option B — Any agent that supports Markdown skills

Copy these folders into whatever skill directory your agent/harness uses:

```text
skills/note-taking/obsidian/
skills/note-taking/prepforreset/
skills/note-taking/wikijanitor/   # optional
```

Then configure a vault path for the agent runtime:

```bash
OBSIDIAN_VAULT_PATH="/absolute/path/to/your/Obsidian Vault"
```

Create the expected folders inside the vault:

```text
Daily Logs/
Session Logs/
Janitor Reports/
```

Finally, add `/prepforreset` as a command/alias that loads and follows the `prepforreset` skill.

## Make `prepforreset` a slash command

### Hermes

Hermes exposes installed skills as slash commands by normalizing the skill frontmatter `name`.

Because the skill is named:

```yaml
name: prepforreset
```

it becomes:

```text
/prepforreset
```

after the skill command cache is refreshed. Usually one of these is enough:

```text
/reload-skills
```

or restart the gateway / start a fresh session.

If the command does not appear in a platform autocomplete menu, still try typing `/prepforreset` manually. Some chat platforms cap visible slash-command menus even when the command is dispatchable.

### Generic agents

If your agent runtime has a command registry, create an alias like:

```text
/prepforreset -> Load the prepforreset skill, load the obsidian companion skill, write the Daily Log and Session Log into OBSIDIAN_VAULT_PATH, then return the short handoff.
```

If your agent has no command registry, keep the prompt below as a reusable snippet.

## Copy-paste prompt for your agent

Paste this into your agent after installing the skills:

```md
You have access to an Agent Memory Wiki skill bundle with these skills:

- `obsidian`: low-level Obsidian vault operations.
- `prepforreset`: context-reset capture into Daily Logs and Session Logs.
- `wikijanitor`: optional review/reconciliation into Janitor Reports.

Set up `/prepforreset` as a command or reusable trigger.

When I type `/prepforreset` or say “prep for reset” / “prepare for a context window”:

1. Load and follow the `prepforreset` skill.
2. Load and follow the `obsidian` companion skill before any vault operation.
3. Resolve `OBSIDIAN_VAULT_PATH` or ask me for the vault path if it is missing.
4. Ensure these folders exist inside the vault:
   - `Daily Logs/`
   - `Session Logs/`
   - `Janitor Reports/`
5. Write a curated Daily Log and Session Log. Do not dump the raw transcript.
6. Include decisions, rationale, rejected alternatives when important, artifacts, lessons/gotchas, explicit open loops, inferred open loops clearly labeled, routing candidates, and source references.
7. Never write secret values. Reference only where credentials live, such as `.env` or secret manager paths.
8. Return a short response with the note paths and a lean copy/paste handoff for the next context.

If this runtime supports slash commands, register `/prepforreset` as an alias for that workflow. If it does not, treat this prompt as the command definition.
```

A longer standalone prompt lives at [`docs/agent-copy-paste-prompt.md`](docs/agent-copy-paste-prompt.md).

## What gets written

- `Daily Logs/YYYY-MM-DD.md` — standalone day summary.
- `Session Logs/YYYY-MM-DD-short-topic-slug.md` — deeper session distillation.
- `Janitor Reports/YYYY-MM-DD-last-24h.md` — optional review/reconciliation note.

## Design principles

- **Curate, don’t dump.** Durable understanding, not transcript hoarding.
- **Human-readable first.** Agents benefit from headings, dates, links, rationale, source references.
- **The wiki is source of truth.** The chat handoff is only a bridge across context windows.
- **No silent mutation outside Obsidian.** Routing candidates can suggest memory/skill/backlog updates, but the skill does not patch other stores unless separately asked.
- **Secrets are never note content.** Record credential locations, never values.
- **Portable by default.** The skills do not assume a private fleet, host path, or vendor runtime.

## Repository layout

```text
skills/       Agent skills you install into your agent runtime.
docs/         Setup, slash-command, scheduling, and safety docs.
templates/    Human-readable note templates.
scripts/      Optional installer and janitor wrapper examples.
examples/     Environment/config examples.
tools/        Local validation script used by CI.
```

## Documentation

| Doc | Purpose |
| --- | --- |
| [`docs/installation.md`](docs/installation.md) | Detailed installation for Hermes and generic agents. |
| [`docs/slash-command-setup.md`](docs/slash-command-setup.md) | How to expose `/prepforreset`. |
| [`docs/agent-copy-paste-prompt.md`](docs/agent-copy-paste-prompt.md) | Full prompt to paste into your agent. |
| [`docs/scheduling-wikijanitor.md`](docs/scheduling-wikijanitor.md) | Optional scheduled janitor setup. |
| [`docs/security-and-secret-hygiene.md`](docs/security-and-secret-hygiene.md) | Secret-handling rules and safe examples. |
| [`docs/architecture.md`](docs/architecture.md) | Why the bundle is split into three skills. |

## Validation

Run the local validator before publishing changes:

```bash
python3 tools/validate.py
```

It checks skill frontmatter, required docs, executable scripts, template presence, and obvious secret-looking patterns.

## License

MIT. See [`LICENSE`](LICENSE).
