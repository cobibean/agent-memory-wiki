---
name: obsidian
description: "Compatibility slash-command alias for the Vault Operations phase of obsidian-memory-wiki. Install/load obsidian-memory-wiki as the canonical parent skill."
version: 2.0.0
author: Jacobi Lange (@cobi_bean)
license: MIT
metadata:
  hermes:
    tags: [obsidian, notes, vault, memory-wiki, compatibility-alias]
    related_skills: [obsidian-memory-wiki]
    config:
      - key: obsidian_memory_wiki.vault_path
        description: Absolute path to this agent's isolated Obsidian memory-wiki vault
        prompt: Memory-wiki vault path
---

# Obsidian — Compatibility Alias

This skill keeps `/obsidian` and older profile references working. The canonical package is `obsidian-memory-wiki`.

Before doing vault work, load and follow `obsidian-memory-wiki` and execute its **Vault Operations** phase. If the parent skill is unavailable, use this safe fallback:

1. Resolve the vault path from injected skill config `obsidian_memory_wiki.vault_path`; for non-Hermes compatibility, use `OBSIDIAN_VAULT_PATH`. If neither is concrete, stop rather than guessing an ambient vault.
2. Resolve both the vault root and final write target; refuse any write outside the resolved vault root.
3. Search before creating notes to avoid duplicates and contradictions.
4. Use filesystem-native note operations and Markdown files.
5. Use stable filenames, clear headings, dates where useful, and Obsidian wikilinks.
6. Never store or print raw secrets; reference secret locations only.
7. Verify every created or edited path after writing.

For new installs and automation, use `obsidian-memory-wiki`; this alias exists only for command continuity.
