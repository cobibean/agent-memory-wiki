# Architecture

## Canonical package

Version 2 has one behavioral source of truth:

```text
obsidian-memory-wiki
├── Vault Operations
├── Reset Preparation
└── Wiki Janitor Maintenance
```

The `obsidian`, `prepforreset`, and `wikijanitor` directories are small compatibility aliases. They retain familiar slash commands and a minimal safe fallback, but new installs and automation should load the canonical parent.

## Durable artifacts

The default vault contains:

```text
Home.md
Vault Guide.md
Daily Logs/YYYY-MM-DD.md
Session Logs/YYYY-MM-DD-<topic>.md
Janitor Reports/<dated-report>.md
Templates/
.obsidian/
```

- Daily Logs summarize the day and link to deeper notes.
- Session Logs preserve a work block’s goal, state, decisions, artifacts, verification, blockers, and next actions.
- Janitor Reports reconcile a bounded lookback without pretending to be the original session author.
- The chat handoff is a bridge, not the durable artifact.

The wiki is authoritative for session continuity and curated operating memory. Project repositories and domain systems remain authoritative for their own artifacts.

## Write boundaries

Every phase resolves the vault root and final target path. Writes outside the resolved root are refused. Existing notes are searched before creation. Continuing work updates an authoritative session note with timestamped state rather than producing unnecessary near-duplicates.

Secrets are never written. Notes may identify a credential location without copying its value.

## Multi-store capture

When explicitly requested, Reset Preparation may also create compact pointers in built-in or external memory and a project-memory note in the project repository. Each store has a distinct purpose; the workflow does not mutate other stores automatically.

## Scheduled janitor boundary

Hermes cron runs the wrapper in script-only mode. The wrapper invokes Hermes with `obsidian-memory-wiki`, an explicit profile, bounded runtime, and a profile-local lock.

The agent returns one of two contracts:

```text
[[WIKI_JANITOR_SILENT]]
```

or:

```text
[[WIKI_JANITOR_NOTIFY]]
<concise internal digest>
[[WIKI_JANITOR_END]]
```

Only a complete exact-line notify envelope is accepted. Its model-authored body is never forwarded; the wrapper emits a constant notification directing the user to the newest protected Janitor Report. Unmarked, partial, duplicate-marker, and raw output is suppressed.

## Multi-agent topology

Use one Obsidian application per human workstation and one isolated vault per persistent agent. Keep personal, business, and client memory boundaries separate. Treat vault provisioning, skill installation, and recurring janitor scheduling as separate decisions.
