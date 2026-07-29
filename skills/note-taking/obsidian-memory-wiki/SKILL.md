---
name: obsidian-memory-wiki
description: "Use when operating an Obsidian-backed agent memory wiki: safe vault note operations, context-reset handoffs, optional scheduled reconciliation, and multi-agent vault rollout."
version: 2.0.0
author: Jacobi Lange (@cobi_bean)
license: MIT
metadata:
  hermes:
    tags: [obsidian, memory-wiki, notes, reset-handoff, wiki-janitor]
    related_skills: [obsidian, prepforreset, wikijanitor]
    config:
      - key: obsidian_memory_wiki.vault_path
        description: Absolute path to this agent's isolated Obsidian memory-wiki vault
        prompt: Memory-wiki vault path
      - key: obsidian_memory_wiki.janitor_timeout_seconds
        description: Maximum runtime in seconds for a scheduled janitor invocation
        default: 300
        prompt: Wiki Janitor timeout in seconds
      - key: obsidian_memory_wiki.janitor_max_turns
        description: Maximum Hermes turns for a scheduled janitor invocation
        default: 100
        prompt: Wiki Janitor maximum turns
---

# Obsidian Memory Wiki

## Canonical Package

`obsidian-memory-wiki` is the canonical parent skill for three formerly separate phases:

- `obsidian` → low-level vault/file operations.
- `prepforreset` → context-reset and end-of-session handoff capture.
- `wikijanitor` → scheduled or manual memory-wiki reconciliation.

The old skill names may still exist as compatibility slash-command aliases so `/prepforreset`, `/wikijanitor`, and `/obsidian` keep working. New automation, cron wrappers, and shared-skill installs should load/install this parent package:

```text
--skills obsidian-memory-wiki
```

Do **not** schedule new runs with `--skills wikijanitor,obsidian` or `--skills prepforreset,obsidian`; those names are compatibility aliases and may be absent on newer profiles.

## When to Use

Use this skill when:

- Reading, searching, creating, or editing notes in an Obsidian vault.
- The user says “prep for reset”, “prepare for a context window”, or invokes `/prepforreset`.
- A scheduled or manual wiki janitor should review recent sessions and memory-wiki notes.
- Installing or packaging this workflow for another compatible agent runtime.

Do not use it for:

- Dumping raw transcripts without distillation.
- Storing secrets or credential values in notes.
- Mutating non-wiki memory stores, project repositories, manifests, or backlogs unless the user separately asks for that mutation.
- Writing outside the resolved vault root.

## Required Setup and Safety

1. Resolve the vault path before file operations.
   - Preferred in Hermes: injected skill config `obsidian_memory_wiki.vault_path` from the active profile `config.yaml`.
   - Compatibility fallback for other runtimes: `OBSIDIAN_VAULT_PATH` from the active process environment.
   - If neither source provides a concrete path, stop and request configuration; never guess a vault from an ambient directory.
2. Resolve the final absolute path and refuse writes whose resolved path is outside the vault root.
3. Prefer file tools for note operations: `read_file`, `search_files`, `write_file`, and `patch`.
4. Use terminal only for environment/profile checks, path resolution, or verification that genuinely needs a shell.
5. Keep durable knowledge separate from stale task progress. If it will be stale next week, put it in a handoff/session note, not a permanent concept note.
6. Never print or store raw secrets. Reference only secret locations such as `.env`, keychain, vault item, or config path.

## Phase Selection

- If invoked through `/obsidian` or a vault CRUD request, run **Vault Operations**.
- If invoked through `/prepforreset` or reset/handoff language, run **Reset Preparation**.
- If invoked through `/wikijanitor`, a scheduled janitor wrapper, or reconciliation language, run **Wiki Janitor Maintenance**.
- If the request is ambiguous, choose the safest read-only phase first and ask only when the ambiguity changes what file would be written.

## Vault Operations Phase

### Read/list/search

- Search before creating a new note; update existing notes when the topic already exists.
- For filenames, use file search under the resolved vault path.
- For content, search Markdown files under the vault and read enough surrounding context to avoid duplicates or contradictions.

### Create/edit notes

- Use stable filenames and clear headings.
- Use dates where useful, especially for logs and reports.
- Use Obsidian wikilinks such as `[[Related Note]]` for durable graph links.
- Prefer targeted `patch` edits when an anchor is stable; otherwise rewrite the whole note deliberately with `write_file`.
- Verify the file exists and contains the intended content after writing.

### Default folder conventions

Relative to the vault root:

```text
Daily Logs/
Session Logs/
Janitor Reports/
```

These folders are conventions, not license to invent a vault. Create them only after the vault root is concrete.

## Reset Preparation Phase (`/prepforreset`)

Goal: preserve the useful session/day knowledge before context is lost, then return a lean handoff that the next agent can act on immediately.

Use `templates/daily-log.md` for day-level capture and `templates/session-log.md` for a reset/session handoff. Preserve their required status, commands/tests and outcomes, verification, blockers, and next-action sections.

### Artifacts

1. **Daily Log** — `Daily Logs/YYYY-MM-DD.md`
   - Standalone day-level summary.
   - Important work blocks, decisions, artifacts, open loops, and routing candidates.
   - Links to session logs and janitor reports.
2. **Session Log** — `Session Logs/YYYY-MM-DD-<short-topic-slug>.md`
   - Deeper distillation of the current session/work block.
   - Goal, state, decisions, commands run, files touched, verification, blockers, and next steps.
3. **Chat handoff** — short copy/paste summary.
   - Current goal/status.
   - Important files/URLs/notes.
   - Next concrete actions.
   - Known blockers and cautions.

### Continuation and slug rules

- Prefix session logs with the local date: `YYYY-MM-DD-`.
- Use a concise lowercase topic slug, preferably 3–6 words.
- Avoid generic slugs such as `session-notes`, `daily-work`, or `context-reset`.
- If the filename collides with an unrelated session, append `-2`, `-3`, etc. rather than overwriting.
- If the current work explicitly continues an existing authoritative session note—or the user supplies that continuation note—update the existing note with a clearly timestamped completion/update section instead of creating a near-duplicate. Preserve the earlier snapshot and open loops as history, then state which items are now resolved or superseded.

### Capture content

Include durable items future humans/agents need:

- User goal and actual current status.
- Important decisions, rejected options when relevant, and assumptions.
- Artifacts created or modified, with paths/URLs.
- Commands/tests already run and real outcomes.
- Bugs, gotchas, or environment lessons that may recur.
- Open loops and explicit next steps.
- Suggested routing destinations for knowledge that belongs in skills, manifests, docs, memories, or backlog.

Do **not** include raw secrets, huge transcript dumps, or stale internal chain-of-thought. Summarize tool results and cite paths instead of pasting sensitive output.

### Verification before final handoff

- Daily log path exists or was intentionally left unchanged.
- Session log path exists when a session-level note was warranted.
- Backlinks between day/session notes are present when both exist.
- Final handoff includes next actions and blockers, not just history.
- If the handoff records an intentionally stopped, retired, migrated, or powered-off runtime, inspect scheduled jobs that still target it. Pause/remove only jobs whose purpose is now invalid or would create false alerts/revival risk; preserve deliberate observation/reminder jobs. Record job IDs and the disposition in the handoff. Do not turn reset prep into an unrelated fleet-wide cron cleanup.
- If an earlier Daily Log or janitor report contains a correct time-bounded snapshot that is now stale, preserve it as history and add a clearly labeled later reset/update section; do not rewrite the earlier observation as though it was never true.
- For a Git-backed handoff, distinguish the verified product/release commit from the later documentation-only handoff HEAD. Commit, push, and verify the handoff once; then record its final SHA/run in the non-Git Daily/Session note rather than creating a recursive chain of repository commits whose only purpose is to mention the previous CI run.

### Multi-store reset capture

When the user says to save state in “memory,” “Honcho,” “anywhere else,” or similar before a reset, treat that as broader than Obsidian-only capture:

1. Write the normal Daily Log / Session Log first, but keep it distilled and secret-free.
2. Save a compact built-in memory pointer only for stable facts that should survive future sessions, such as the source-of-truth manifest/path and one durable follow-up. Do not store stale progress or raw task logs in memory.
3. If an external memory provider such as Honcho is configured and safe to use, save a concise handoff there too, then verify retrieval/search when the provider exposes a no-secret check.
4. If a project/corpus repo is the durable source of truth, create or update a project-memory note in that repo and follow that repo’s git/secret-scan expectations before calling it saved.
5. If the resolved Obsidian vault looks temporary or otherwise less durable, say so in both the note and the final handoff; prefer the repo/manifest as the authoritative continuation point.

Reference: `references/reset-multistore-handoff.md` provides a provider-neutral multi-store handoff pattern.

## Wiki Janitor Maintenance Phase (`/wikijanitor` / scheduled)

Goal: conservatively reconcile recent sessions against the memory wiki. The janitor is a reliability layer for missed or incomplete capture; it should not pretend to be the original session author.

### Default behavior

- Default lookback: last 24 hours unless the user/schedule specifies otherwise.
- If there was no meaningful activity, create no report and send no user notification.
- If there was activity, create a first-class Janitor Report under `Janitor Reports/`.
- Link the Janitor Report to relevant Daily Logs and, when obvious, related Session Logs.
- Make only small routine note updates automatically, such as backlinks or index references.
- Surface missing session logs, uncertainty, and review candidates as report gaps instead of auto-writing major narrative notes.
- Routine-only reconciliation is silent. Notify only for warnings, gaps, uncertainty, or actions that require user attention.

### Janitor report contents

Use `templates/janitor-report.md`. A useful Janitor Report includes:

- Exact lookback start/end timestamps and a stable run/window identifier.
- Sessions/sources reviewed.
- Notes created or updated.
- Routine link/index fixes made.
- Gaps, uncertainty, and review candidates.
- Suggested follow-up actions.

### Cron/output discipline

For scheduled Hermes cron wrappers:

- Load the parent skill: `--skills obsidian-memory-wiki`.
- Avoid overlapping janitor runs; size timeouts for the vault and model path.
- Keep wrappers portable across Linux and macOS. Linux commonly provides `flock` and GNU `timeout`; stock macOS provides neither. Use an atomic profile-local `mkdir` lock fallback when `flock` is absent, and use a bounded Python `Popen(..., start_new_session=True)` fallback that terminates the whole process group and exits `124` on timeout. Test the actual target host rather than treating `bash -n` as runtime proof.
- Keep user-facing output concise: changed files, warnings, and follow-up actions.
- Verify cron delivery resolution on the target profile. A generic platform target such as `deliver: telegram` can run the script successfully yet fail delivery when that profile has no `TELEGRAM_HOME_CHANNEL`. Prefer an explicit approved target such as `telegram:<chat_id>` when the destination is stable, then run the scheduler once and confirm there is no delivery error.
- If a wrapper suppresses raw output until a marker appears, use an exact-line envelope for the internal report digest:

```text
[[WIKI_JANITOR_NOTIFY]]
<concise internal digest>
[[WIKI_JANITOR_END]]
```

- For a clean no-activity or routine-only run, output exactly `[[WIKI_JANITOR_SILENT]]`; the wrapper suppresses it.
- A notify envelope causes only a constant wrapper-authored notification. Never forward model-authored digest text; the newest protected Janitor Report is the review surface.
- Never forward unmarked, partially marked, or multiply marked output. It may contain tool output, paths, or secrets.
- Parse marker output before treating a non-zero Hermes process status as user-facing failure; Hermes can finish the assistant response and still exit non-zero during max-turn/teardown paths.
- Test wrappers with a fake Hermes binary that exits non-zero after printing a complete notify envelope, plus malformed, mixed-marker, timeout, lock-contention, and secret-shaped digest cases.

## Multi-Agent Vault Provisioning

When the operator asks for a shared-host or fleet rollout, inventory and classify the active roster before changing any profile. Do not infer fleet scope from the profile that received the request.

The authoritative contracts are intentionally split:

- `references/per-agent-vault-layout.md` owns vault topology, isolation, migration policy, automation disposition, and acceptance criteria.
- `references/dedicated-vault-rollout.md` owns pilot-first sequencing, deterministic evidence, target-OS runtime checks, and promotion gates; it references the topology contract rather than redefining it.

Follow both references. Keep discovery read-only, pilot one approved operator-owned profile end to end, and promote only the verified package. Do not duplicate those contracts here or silently mutate every profile during discovery.

## Distribution and Compatibility Packaging

- Publish and install `obsidian-memory-wiki` as the canonical package.
- Keep `obsidian`, `prepforreset`, and `wikijanitor` as compatibility aliases only when slash-command continuity is needed.
- Alias packages should instruct agents to install/load this parent and should not be treated as independent canonical skills.
- After installing into a running gateway, start a new session, run `/reload-skills` if available, or restart only the affected profile gateway when a live slash-command cache must be refreshed.

## Common Pitfalls

1. **Loading retired split names in cron.** Use `--skills obsidian-memory-wiki`, not `wikijanitor,obsidian`.
2. **Creating near-duplicate notes.** Search aliases and related terms first.
3. **Reset notes without next actions.** A future agent needs runnable continuation steps.
4. **Saving temporary progress as permanent knowledge.** Keep stale task progress in session/handoff notes.
5. **Assuming file existence means slash commands are live.** Running gateways may cache skill commands.
6. **Reporting janitor success from unmarked output.** Require the exact marker contract and emit only a constant wrapper-authored notification; never forward model-authored digest text.
7. **Capturing the wrong project after an ambiguous reset request.** If the user corrects the target project mid-reset, treat it as an active correction: create/update the correct session log, daily backlink, project memory, and any requested memory/Honcho state before finalizing. Do not leave only the mistaken capture.
8. **Confusing product verification SHAs with later handoff-doc commits.** When a reset handoff itself creates and pushes memory/docs, record both: the product/build commit that was verified and the final repo HEAD after documentation-only reset notes. Future agents need to know which SHA passed tests and which SHA is just the latest handoff state.
9. **Assuming Linux janitor shell tools exist on macOS.** A wrapper can pass `bash -n` and still exit before Hermes because stock macOS lacks both `flock` and GNU `timeout`. Provide the atomic `mkdir` and Python-timeout fallbacks described above, then execute the real wrapper on the target host.
10. **Designing only for the profile that received a fleet setup request.** On a shared agent host, inventory the active roster first. Install the desktop app once, but use a separate `<agent>-wiki` vault and profile-local path for each persistent agent; do not accidentally turn one profile's vault into the fleet-wide default.
11. **Treating vault creation and daily janitor scheduling as the same decision.** Give persistent agents manual reset capture broadly, but enable recurring model-powered janitors only where activity and missed-capture risk justify them.
12. **Trusting pre-open `.obsidian` settings as final state.** After registering and opening each vault, re-read the required core-plugin configuration. Obsidian may normalize vault state during first open; verify `core-plugins.json` still enables Templates and Daily Notes and that `templates.json` and `daily-notes.json` still exist with the intended folders. Repair missing settings, reopen the vault, and visually verify again before acceptance.

## Verification Checklist

- [ ] Vault root resolved and write targets verified inside it.
- [ ] For shared-host rollouts, the active roster was inventoried and each persistent agent received an explicit vault/skill/janitor disposition.
- [ ] Each profile resolves only its assigned vault unless shared access was explicitly approved.
- [ ] Existing notes searched before creation.
- [ ] Created/edited note paths verified.
- [ ] Reset handoff includes goal, state, blockers, artifacts, and next steps.
- [ ] Janitor reports record reviewed sources, changes, gaps, and follow-up.
- [ ] Cron wrappers use `obsidian-memory-wiki` and do not leak unmarked output.
- [ ] After first UI open, Templates/Daily Notes remain enabled and their vault-local config files still exist with the intended folders.
- [ ] Profile installs include this parent package; old names are aliases only.
