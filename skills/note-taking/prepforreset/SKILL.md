---
name: prepforreset
description: "Compatibility slash-command alias for the Reset Preparation phase of obsidian-memory-wiki. Use when the user invokes /prepforreset or asks to prep for a context reset."
version: 2.0.0
author: Jacobi Lange (@cobi_bean)
license: MIT
metadata:
  hermes:
    tags: [context-reset, daily-log, session-log, memory-wiki, prepforreset, compatibility-alias]
    related_skills: [obsidian-memory-wiki]
    config:
      - key: obsidian_memory_wiki.vault_path
        description: Absolute path to this agent's isolated Obsidian memory-wiki vault
        prompt: Memory-wiki vault path
---

# Prep for Reset — Compatibility Alias

This skill keeps `/prepforreset` working. The canonical package is `obsidian-memory-wiki`.

Load and follow `obsidian-memory-wiki`, then execute its **Reset Preparation** phase. If the parent skill is unavailable, use this fallback:

1. Resolve the Obsidian vault path safely and keep writes inside it.
2. Search existing Daily Logs and Session Logs before writing.
3. Update or create:
   - `Daily Logs/YYYY-MM-DD.md`
   - `Session Logs/YYYY-MM-DD-<short-topic-slug>.md`
4. Continue an existing authoritative session note when work is genuinely continuing; suffix filenames only for unrelated collisions.
5. Distill rather than dump the transcript. Capture the goal, current status, decisions, artifacts, verified outcomes, blockers, and next concrete actions.
6. Do not store secrets or raw credential values.
7. Add backlinks between daily and session notes when both exist.
8. Return a lean copy/paste handoff naming current state, authoritative artifacts, blockers, and next steps.

For new installs and automation, use `obsidian-memory-wiki`; this alias exists only for command continuity.
