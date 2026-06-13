---
name: obsidian
description: Use when an agent needs to read, search, create, or edit Markdown notes inside an Obsidian vault. Resolve the vault path, keep writes inside the vault root, and use filesystem-first note operations.
version: 1.0.0
author: Jacobi Lange (@cobi_bean)
license: MIT
metadata:
  hermes:
    tags: [obsidian, notes, vault, markdown]
    related_skills: []
---

# Obsidian Vault

## Overview

Use this skill as the low-level filesystem layer for Obsidian vault work: reading notes, listing notes, searching Markdown files, creating notes, appending content, targeted edits, and adding wikilinks.

Workflow skills such as `prepforreset` and `wikijanitor` should load this skill before writing anything into the vault.

## Vault Path Contract

Use a known, concrete vault path before calling file tools.

Preferred configuration:

```bash
OBSIDIAN_VAULT_PATH="/absolute/path/to/your/Obsidian Vault"
```

If `OBSIDIAN_VAULT_PATH` is unset, a desktop fallback may be used only when it exists and is clearly intended:

```text
~/Documents/Obsidian Vault
```

For hosted/productized agent runtimes, the product or installer should provide a per-user/per-agent vault path. The skill should consume that resolved value; it should not invent private host paths or write into the current working directory.

## Safety Rules

1. Resolve the vault root to a canonical absolute path before writing.
2. Resolve every target note path before writing.
3. Refuse any write whose final resolved path is outside the vault root.
4. If no vault path exists, report a setup blocker instead of guessing.
5. Never print or store secret values in notes.

## Expected Memory Wiki Folders

Agent Memory Wiki workflows use these folders relative to the vault root:

```text
Daily Logs/
Session Logs/
Janitor Reports/
```

Create them during setup or the first approved provisioning step.

## Reading Notes

Read notes by concrete absolute path. Do not pass shell variables such as `$OBSIDIAN_VAULT_PATH` to file tools; resolve them first.

## Listing Notes

List Markdown notes under the resolved vault path. For subfolders, list beneath the concrete subfolder path.

## Searching Notes

Search note contents with a Markdown file filter when available. Prefer searching only inside the resolved vault path.

## Creating Notes

Create notes with full Markdown content and minimal frontmatter. Prefer complete writes for new notes.

## Appending or Editing Notes

For small edits, use targeted replacement around stable headings. For larger note updates, read the current note, modify the full content, and write the whole note back.

## Wikilinks

Use Obsidian wikilinks for related notes:

```md
[[Daily Logs/2026-06-13]]
[[Session Logs/2026-06-13-agent-memory-wiki|Agent Memory Wiki session]]
```

## Common Pitfalls

1. **Writing outside the vault.** Always resolve paths and enforce the root boundary.
2. **Using unresolved variables in file tools.** Resolve `$OBSIDIAN_VAULT_PATH` before passing paths.
3. **Creating notes in the working directory.** Missing vault config is a setup blocker, not permission to write nearby.
4. **Over-tagging.** Obsidian retrieval works best with stable headings, dates, links, and specific nouns.
5. **Secret leakage.** Notes are durable; credential values do not belong there.

## Verification Checklist

- [ ] Vault path resolved to a canonical absolute path.
- [ ] Target note path resolves inside the vault root.
- [ ] Expected folders exist or were explicitly created.
- [ ] Note operations avoided raw secrets.
- [ ] Wikilinks use stable note paths.
