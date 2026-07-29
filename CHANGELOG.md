# Changelog

All notable package changes are documented here.

## 2.0.0 — 2026-07-29

### Changed

- Made `obsidian-memory-wiki` the single canonical behavioral skill.
- Converted `obsidian`, `prepforreset`, and `wikijanitor` into compatibility aliases.
- Added continuation-aware reset capture, multi-store routing, and per-agent vault guidance.
- Moved templates into the installable canonical package.
- Replaced the installer with profile-authoritative targeting, path validation, unique backups, native `skills.config` updates, hardened config permissions, dry-run support, and optional vault initialization.
- Replaced the janitor wrapper with portable macOS/Linux locking and timeout behavior plus an exact notify envelope.
- Expanded validation and behavioral tests across installer and wrapper failure modes.
- Added Ubuntu and macOS CI coverage.

### Compatibility

- Existing slash commands remain available when aliases are installed.
- New cron jobs must load `obsidian-memory-wiki`, not the retired split dependency list.
- Scheduled notify output now requires `[[WIKI_JANITOR_NOTIFY]]` and `[[WIKI_JANITOR_END]]`; clean runs use `[[WIKI_JANITOR_SILENT]]`.

## 1.0.0 — 2026-06-13

- Initial public package with separate Obsidian, reset-preparation, and wiki-janitor skills.
