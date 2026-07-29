---
name: wikijanitor
description: "Compatibility slash-command alias for the Wiki Janitor phase of obsidian-memory-wiki. Use obsidian-memory-wiki as the canonical parent for scheduled janitor runs."
version: 2.0.0
author: Jacobi Lange (@cobi_bean)
license: MIT
metadata:
  hermes:
    tags: [wiki-janitor, janitor-report, memory-wiki, wikijanitor, compatibility-alias]
    related_skills: [obsidian-memory-wiki]
    config:
      - key: obsidian_memory_wiki.vault_path
        description: Absolute path to this agent's isolated Obsidian memory-wiki vault
        prompt: Memory-wiki vault path
---

# Wiki Janitor — Compatibility Alias

This skill keeps `/wikijanitor` and older references working. The canonical package is `obsidian-memory-wiki`.

Load and follow `obsidian-memory-wiki`, then execute its **Wiki Janitor Maintenance** phase. New cron wrappers should invoke:

```text
--skills obsidian-memory-wiki
```

Do not schedule new runs with the retired split dependency `--skills wikijanitor,obsidian`.

If the parent skill is unavailable, use this fallback:

1. Review the requested lookback window, defaulting to 24 hours.
2. Compare recent sessions with Daily Logs, Session Logs, and Janitor Reports.
3. If there is no activity, or only routine reconciliation with no user attention needed, make no user notification.
4. If there is activity, write a Janitor Report under `Janitor Reports/`.
5. Make only conservative routine changes such as backlinks or index links.
6. Record uncertainty and missing notes as gaps instead of inventing narrative.
7. Keep user-facing output concise and never print secrets.
8. Scheduled wrappers validate an internal digest only between exact marker lines:

```text
[[WIKI_JANITOR_NOTIFY]]
<concise internal digest>
[[WIKI_JANITOR_END]]
```

Use exactly `[[WIKI_JANITOR_SILENT]]` for a no-activity or routine-only run. Notify only for warnings, gaps, uncertainty, or actions requiring user attention. The wrapper must emit a constant notification and never forward model-authored digest text. Unmarked or partially marked raw output must remain suppressed.
