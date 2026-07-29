# Copy/Paste Setup Prompt for Another Agent

Use this when the target runtime cannot use the included Hermes installer.

```text
Install the Agent Memory Wiki v2 package from this repository.

Requirements:
1. Treat skills/note-taking/obsidian-memory-wiki as the canonical behavior package.
2. Install obsidian, prepforreset, and wikijanitor only as compatibility aliases when their commands are needed.
3. Configure a concrete per-agent vault path equivalent to skills.config.obsidian_memory_wiki.vault_path; use OBSIDIAN_VAULT_PATH only as a non-Hermes compatibility fallback.
4. Keep all resolved write targets inside that vault.
5. Do not use an entire project repository or a shared multi-agent parent directory as the vault unless explicitly approved.
6. Create or verify Daily Logs, Session Logs, Janitor Reports, and Templates.
7. Never copy tokens, passwords, private keys, raw .env contents, or credential-bearing URLs into notes.
8. Search before creating notes and update an authoritative session note when work genuinely continues.
9. Map /prepforreset to Reset Preparation and /wikijanitor to Wiki Janitor Maintenance.
10. Treat recurring janitor scheduling as opt-in. If scheduled, preserve non-overlap, bounded runtime, explicit delivery, and the exact notify/silent marker contract.
11. Test with a disposable vault first and report the exact created files and verification results.
```

Do not paste private paths, credentials, delivery IDs, or client-specific topology into a public issue or shared prompt.
