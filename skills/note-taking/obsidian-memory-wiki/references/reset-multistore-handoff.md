# Reset Multi-Store Handoff Pattern

## Trigger

Use this when the user asks for `/prepforreset`, context-reset preparation, or says to save the project state in “memory,” “Honcho,” “anywhere else,” etc.

## Provider-neutral pattern

1. **Recover the current authoritative state first.** Use recent session/search context and the relevant manifest/source-of-truth doc; do not rely on the transient chat tail alone.
2. **Write normal Obsidian reset notes.** Create/update:
   - `Daily Logs/YYYY-MM-DD.md`
   - `Session Logs/YYYY-MM-DD-<topic>.md`
3. **Add project-memory when a repo is the durable corpus.** For substantial project work, create `docs/memory/YYYY-MM-DD/<topic>-memory-YYYY-MM-DD.md` in the repo. Keep it human-skimmable and point to the source-of-truth manifest/runbook.
4. **Save compact built-in memory only for stable pointers.** Good: “source of truth is X; durable follow-up is Y.” Bad: full task narrative, command transcript, or stale progress.
5. **Save external memory provider handoff if configured.** For Honcho or similar, write a concise conclusion/session handoff and verify retrieval/search with a harmless marker. Never store or echo secrets.
6. **Secret scan before git persistence.** Scan newly written repo notes for obvious API-key/token/private-key patterns before commit/push.
7. **Commit/push only when it matches repo policy or the user explicitly asked for durable save.** Verify local and remote HEAD when pushing; if push is blocked, report the blocker and the local commit/path.
8. **Final handoff names durability tiers.** If the Obsidian vault path looks temporary/ephemeral, call that out and direct the next session to the repo/manifest instead.

## What to avoid

- Do not save raw secrets, pasted credential values, raw logs, or full transcripts.
- Do not create a new narrow one-off skill for a single project reset; update this umbrella or add a reference.
- Do not treat external provider setup failures as durable negative rules. Capture the working save/verification pattern, not transient connection errors.
