# Copy-Paste Prompt for Your Agent

Paste this into your agent after installing the skills.

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

Optional: set up `/wikijanitor` as a manual or scheduled command that loads `wikijanitor`, reviews recent sessions against the vault, writes Janitor Reports when there was activity, makes only conservative routine note updates, and notifies me only for gaps/review candidates/uncertainty.
```
