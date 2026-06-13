---
name: wikijanitor
description: Use when the user invokes /wikijanitor or when a scheduled janitor reviews recent sessions. Reconcile Obsidian Daily Logs, Session Logs, and Janitor Reports over a lookback window; make conservative routine updates and notify only for review/uncertainty.
version: 1.0.0
author: Jacobi Lange (@cobi_bean)
license: MIT
metadata:
  hermes:
    tags: [daily-log, session-log, janitor-report, obsidian]
    related_skills: [obsidian, prepforreset]
---

# Wiki Janitor

## Overview

Use this skill to run a conservative Obsidian memory-wiki review over recent agent sessions and existing notes.

The janitor is a reliability layer for missed or incomplete session capture. It does not replace manual `/prepforreset` notes and does not pretend to be the original session author.

The primary artifact is a first-class Obsidian Janitor Report note. The janitor may also make small routine updates to existing Daily Logs and Session Logs, but missing major notes become report gaps/review items rather than automatically created full session logs.

## When to Use

Use when:

- the user invokes `/wikijanitor`
- a scheduled nightly wiki janitor runs
- the user asks to review/reconcile recent sessions against the Obsidian memory wiki
- a missed context-reset/session note may need to be surfaced

Do not use for raw transcript dumping, rewriting the whole daily log, creating missing full session logs by default, mutating non-Obsidian stores automatically, or printing secrets.

## Required Companion Skill

Before any vault operation, load and follow the `obsidian` skill. It owns vault path resolution and low-level vault conventions.

If the vault path is missing or ambiguous, ask for it instead of writing elsewhere. Resolve canonical paths before writing and refuse any write whose final resolved path is outside the resolved vault root.

For session discovery, use the runtime’s session search/history API when available. If session search is not available, inspect only the context and note files that the runtime can safely access.

## Slash Command Discovery

Hermes automatically exposes installed skills as slash commands by normalizing the skill `name` from frontmatter. Because this skill is named `wikijanitor`, it is invoked as:

```text
/wikijanitor
```

after the skill command cache has reloaded.

For other runtimes, create a command alias that loads and follows this skill.

## Default Behavior

Default lookback: last 24 hours.

Scheduled default time: around 3:30am local/system time.

If there are no sessions/activity in the lookback window: create no report, make no note changes, and send no user message.

If there was session activity: create a Janitor Report note, link it both ways with relevant Daily Logs, record what was reviewed, record routine updates made, record gaps/review candidates/uncertainty/suggested actions, and notify the user only if review/uncertainty exists.

## Folder and Filename Conventions

Default folders, relative to the Obsidian vault:

```text
Daily Logs/
Session Logs/
Janitor Reports/
```

Janitor report filename:

```text
Janitor Reports/YYYY-MM-DD-last-24h.md
```

If more than one report is needed on the same date, add a timestamp or numeric suffix:

```text
Janitor Reports/YYYY-MM-DD-0330-last-24h.md
Janitor Reports/YYYY-MM-DD-last-24h-2.md
```

For scheduled runs, prefer idempotency over suffixing: compute and record the exact lookback start/end in the report, reuse/update an existing report for that same window when possible, and de-duplicate Daily Log backlinks before appending.

## Minimal Frontmatter

```yaml
---
type: janitor-report
date: YYYY-MM-DD
agent: <agent-name>
profile: <profile-name>
lookback: 24h
tags:
  - janitor-report
---
```

Add `review-needed` only if the report contains review candidates, gaps requiring judgment, conflicts, sensitive-content risks, or uncertainty.

## Janitor Report Shape

Recommended sections:

```md
# Janitor Report — YYYY-MM-DD — Last 24h

## Summary

## Lookback window

## Related daily logs
- [[Daily Logs/YYYY-MM-DD]]

## Sessions reviewed

## Routine updates made

## Gaps found

## Review candidates

## Suggested actions

## Source references
```

Janitor reports live at the same memory-wiki tier as Daily Logs and Session Logs. They are durable wiki artifacts with provenance: “this came from scheduled/manual reconciliation.”

## Bidirectional Links

Link both ways: Daily Logs should include a `## Janitor reports` section linking relevant reports; Janitor Reports should include `## Related daily logs` linking every reviewed date. Because a last-24h lookback may cross midnight, a report may link two daily logs.

## Routine Updates Allowed

The janitor may silently make small, conservative updates to existing notes when evidence is clear:

- add a missing session link to a Daily Log
- add a missing Janitor Report link to a Daily Log
- append a clearly sourced one-line session summary
- add obvious artifact paths already mentioned in the session
- add backlinks between Daily Logs, Session Logs, and Janitor Reports
- normalize a missing section heading when doing so is non-destructive

Do not notify for routine cleanup.

## Updates Not Allowed by Default

The janitor should not rewrite a whole day, delete nuance, overwrite manual wording, create missing full Session Logs automatically, silently mutate non-Obsidian stores, summarize-away important context, or decide that a preference/decision is permanent without review.

For missing important session logs, write a gap/review item in the Janitor Report.

## Review Candidates

Notify the user only when the report contains review candidates or uncertainty, such as possible new user preferences, important decisions not captured, skill/gotcha candidates, conflicting notes, ambiguous open loops, sensitive content risk, or uncertainty about destination/routing.

Routing candidates should include suggested destinations/actions but not be applied automatically.

## Secret Hygiene

Never print secret values in reports or notifications. Allowed references include `Credential reference: see profile-local .env` and `Token presence verified in /path/to/.env; value intentionally omitted`. Disallowed content includes raw `.env` contents, API keys, OAuth tokens, private keys, webhook secrets, passwords, and credential-bearing connection strings.

## Notification Contract for Cron Wrappers

When used by a script-only cron wrapper, final output should be machine-filterable:

- If there are review candidates/uncertainty: include `[[WIKI_JANITOR_NOTIFY]]` followed by a concise user-friendly digest.
- If routine only: include `[[WIKI_JANITOR_SILENT]]` and no user-facing digest.
- If no sessions/activity: include `[[WIKI_JANITOR_SILENT]]`.

The wrapper may suppress silent output entirely. Manual `/wikijanitor` runs can return a normal concise summary, including the report path.

## Execution Checklist

1. Load `obsidian` if not already loaded.
2. Resolve the Obsidian vault path.
3. Determine agent/profile/platform and current date/time.
4. Search sessions from the last 24 hours unless the user specified another lookback.
5. If no session activity: stop without writing a report.
6. Inspect relevant Daily Logs and Session Logs.
7. Make only conservative routine updates to existing notes.
8. Create a Janitor Report note for any non-empty reviewed lookback.
9. Link report ↔ relevant Daily Logs.
10. Record gaps/review candidates/suggested actions without mutating non-Obsidian stores.
11. Use the notification contract when running under cron.
12. Keep secrets out of notes and notifications.

## Common Pitfalls

1. **Creating missing session logs automatically.** Report gaps instead; manual capture remains primary.
2. **Silent over-editing.** Append/reconcile/flag; do not rewrite or flatten nuance.
3. **Always notifying.** Routine cleanup should be silent in scheduled mode.
4. **No provenance.** Janitor reports must make clear what was reviewed and why changes were made.
5. **Secret leakage.** Report locations, not values.
6. **Treating janitor reports as lower tier.** They are first-class memory-wiki notes.
7. **Forgetting midnight crossing.** Last-24h reports may relate to two daily logs.
8. **Cron raw-output leaks.** Wrappers should parse markers and avoid dumping raw captured model output on failure.
9. **Overlapping scheduled runs.** Use a lock and a bounded timeout.
10. **Unconfigured vault.** Missing vault path is a setup blocker, not permission to guess.

## Verification Checklist

- [ ] `obsidian` was loaded and vault path resolved.
- [ ] Sessions/activity were checked for the requested lookback.
- [ ] No report was created if no activity existed.
- [ ] A Janitor Report was created if activity existed.
- [ ] Report links relevant Daily Logs.
- [ ] Daily Logs link the report.
- [ ] Only conservative routine updates were applied.
- [ ] Missing Session Logs were reported as gaps, not auto-created.
- [ ] Review candidates have suggested destinations/actions.
- [ ] No secrets were printed.
- [ ] Scheduled-mode output follows the notification marker contract.
