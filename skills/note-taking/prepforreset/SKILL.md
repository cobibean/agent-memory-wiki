---
name: prepforreset
description: Use when the user says “prep for reset”, “prep for a context window”, “prepare for a context window”, or invokes /prepforreset. Create curated Obsidian Daily Log and Session Log notes, then return a lean copy/paste handoff.
version: 1.0.0
author: Jacobi Lange (@cobi_bean)
license: MIT
metadata:
  hermes:
    tags: [daily-log, session-log, context-reset, obsidian]
    related_skills: [obsidian, wikijanitor]
---

# Prep for Reset

## Overview

Use this skill to preserve session or day nuance before a context reset, at the end of a work block, or whenever the user asks the agent to “prep for reset.”

The primary artifact is a curated Obsidian memory-wiki update: a standalone-useful Daily Log plus a deeper Session Log. The secondary artifact is a short copy/paste handoff in chat so the next context can restart smoothly.

This is not transcript dumping. Distill what future humans and agents need: what happened, why it mattered, decisions, rejected options when important, lessons/gotchas, artifacts, open loops, routing candidates, and source references.

## When to Use

Use when:

- the user says “prep for reset”
- the user says “prepare for a context window”
- the user says “prep for a context window”
- the user invokes `/prepforreset`
- the user asks for an end-of-session or end-of-day Obsidian memory/wiki log
- a context reset is likely and durable notes should be written first

Do not use for raw transcript archival, ordinary short-term memory writes, secret storage, or mutation of non-Obsidian stores unless separately requested.

## Required Companion Skill

Before writing any vault file, load and follow the `obsidian` skill. It owns vault resolution and low-level vault conventions.

If the vault path is missing or ambiguous, ask for it instead of writing elsewhere. Resolve canonical paths before writing and refuse any write whose final resolved path is outside the resolved vault root.

## Slash Command Discovery

Hermes automatically exposes installed skills as slash commands by normalizing the skill `name` from frontmatter. Because this skill is named `prepforreset`, it is invoked as:

```text
/prepforreset
```

after the gateway or CLI skill command cache has reloaded. There is no separate plugin required for Hermes.

For other agent runtimes, create a command alias that loads and follows this skill.

## Folder and Filename Conventions

Default folders, relative to the Obsidian vault:

```text
Daily Logs/
Session Logs/
Janitor Reports/
```

Daily log:

```text
Daily Logs/YYYY-MM-DD.md
```

Session log:

```text
Session Logs/YYYY-MM-DD-<auto-short-title>.md
```

Slug rules:

- Always prefix with the local date: `YYYY-MM-DD-`.
- Generate a concise lowercase slug from the real topic.
- Prefer 3–6 words.
- Include project or agent names when obvious.
- Avoid generic slugs such as `daily-work`, `session-notes`, or `context-reset`.
- If a note already exists, append `-2`, `-3`, etc. rather than overwriting.

## Minimal Frontmatter

Daily log:

```yaml
---
type: daily-log
date: YYYY-MM-DD
agent: <agent-name>
profile: <profile-name>
tags:
  - daily-log
---
```

Session log:

```yaml
---
type: session-log
date: YYYY-MM-DD
title: <Human Title>
agent: <agent-name>
profile: <profile-name>
trigger: prepforreset
tags:
  - session-log
  - context-reset
---
```

Add `review-needed` only when the note contains review candidates or uncertainty. Include `agent` and `profile` when known; omit unknown fields rather than inventing metadata.

## Daily Log Shape

Daily logs should be standalone useful, not merely indexes. Create the note if missing; otherwise append/update conservatively.

Before appending a Session Log link, check whether the same target link already exists in the Daily Log. If it exists, update the one-line outcome only when clearly beneficial; do not create duplicate links on rerun.

Recommended sections:

```md
# Daily Log — YYYY-MM-DD

## Day summary

## Sessions
- [[Session Logs/YYYY-MM-DD-topic|Topic]] — one-line outcome.

## Decisions

## Lessons / gotchas

## Open loops

### Explicit

### Inferred

## Routing candidates

## Artifacts

## Janitor reports
```

## Session Log Shape

Recommended sections:

```md
# Session Log — YYYY-MM-DD — Topic

## Summary

## Context

## Decisions

## Alternatives considered

## Lessons / gotchas

## Artifacts touched

## Open loops

### Explicit

### Inferred

## Routing candidates

## Source references
```

Use concise structured sections with enough narrative to preserve nuance. Do not write stiff “AI retrieval optimized” prose; optimize through stable headings, specific entities, dates, wikilinks, artifact paths, source references, and explicit rationale.

## Decisions and Alternatives

Preserve rejected alternatives based on importance:

- Minor operational choice: final decision only, maybe one-line rationale.
- Medium choice: final decision plus brief rejected alternatives.
- Strategic or likely-to-be-revisited choice: include meaningful tradeoffs and why alternatives were rejected.

## Open Loops

Include both explicit and inferred open loops, but label inferred loops clearly. Do not invent vague tasks. Infer only when the follow-up is necessary for the agreed workflow to work. If unsure, put it under Routing candidates instead of Open loops.

## Routing Candidates

Routing candidates are items that may belong somewhere more specific than the session log. Write candidates with suggested destinations/actions, but do not apply non-Obsidian mutations automatically.

Candidate destinations include long-term user/profile memory, skills, manifests/rosters, project docs/gotchas, backlog/plans, and Obsidian daily/session notes.

## Secret Hygiene

Never print secret values in Obsidian notes or handoffs.

Do not include API keys, OAuth tokens, private keys, webhook secrets, passwords, credential-bearing connection strings, or raw `.env` contents.

Allowed references:

- `Credential reference: see profile-local .env`
- `Token presence verified in /path/to/.env; value intentionally omitted`
- `Secret stored in deployment environment; value intentionally omitted`

## Source References

Use traceable references when available:

```md
## Source references

- Platform: <chat / CLI / IDE / other, when known>
- Agent: <agent, when known>
- Profile: <profile, when known>
- Session date: YYYY-MM-DD
- Session ID: `<session_id if available>`
- Evidence source: active conversation / session DB / existing notes
- Related artifacts:
  - `path/or/link`
```

## Handoff Output

After writing the Obsidian notes, return a concise chat summary plus a copy/pastable codeblock handoff.

````md
Notes written:

- Daily log: `Daily Logs/YYYY-MM-DD.md`
- Session log: `Session Logs/YYYY-MM-DD-topic.md`

Optional lean handoff if you’re opening a new context:

```md
Context reset handoff — YYYY-MM-DD

Main source of truth:
- Obsidian Daily Log: `Daily Logs/YYYY-MM-DD.md`
- Obsidian Session Log: `Session Logs/YYYY-MM-DD-topic.md`

Continue from:
- <2–5 bullets max>

Important guardrail:
- Wiki notes are the primary memory; this handoff is only a bridge.
```
````

Avoid giant handoffs or duplicating the whole session log.

## Execution Checklist

1. Load `obsidian` if not already loaded.
2. Resolve the Obsidian vault path.
3. Determine local date, agent name, profile name, platform, session/message IDs if available.
4. Generate session title and unique date-prefixed slug.
5. Create the Session Log with frontmatter and full distillation.
6. Create or update the Daily Log so it is standalone useful and links the Session Log.
7. Include routing candidates with suggested destinations/actions only.
8. Include source references.
9. Run a bounded secret-pattern scan on the created/updated notes.
10. Return note paths plus a lean copy/paste handoff.
11. Do not mutate memory, skills, manifests, rosters, backlog, or project docs unless separately requested.

## Common Pitfalls

1. **Dumping transcripts.** The value is curated distillation, not raw chat archival.
2. **Letting the handoff become the memory.** The handoff is a bridge; the wiki is source of truth.
3. **Mutating other stores automatically.** Record routing candidates, but do not patch non-Obsidian stores without separate approval.
4. **Printing secrets.** Reference only where credentials live.
5. **Over-tagging.** Use minimal tags; use wikilinks/headings/paths for specificity.
6. **Creating vague inferred TODOs.** Label inferred loops and include why they were inferred.
7. **Writing outside the vault.** Resolve the vault and keep writes inside it.
8. **Inflating quiet closeouts.** If the user invokes `/prepforreset` after a simple closeout, write a compact Session Log; do not invent follow-up work.
9. **Ignoring a stop-fixing boundary.** If `/prepforreset` follows “stop fixing / just write a handoff,” preserve that boundary and do not mutate services/state.
10. **Duplicate Daily Log session links.** Put the Session Log wikilink in `## Sessions` only; use plain paths elsewhere.

## Verification Checklist

- [ ] `obsidian` was loaded and vault path resolved.
- [ ] Daily Log exists or was updated.
- [ ] Session Log exists with date-prefixed unique slug.
- [ ] Both note paths resolve inside the resolved vault root.
- [ ] Daily Log links the Session Log exactly once.
- [ ] Frontmatter includes type/date/agent/profile where known.
- [ ] Minimal tags are used.
- [ ] Secrets are omitted; only locations are referenced.
- [ ] A bounded secret-pattern scan passes on created/updated notes.
- [ ] Routing candidates are recommendations only.
- [ ] Source references are traceable.
- [ ] Final chat includes note paths, verification highlights, and a lean handoff.
