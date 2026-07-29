# Slash-Command Setup

Hermes exposes installed skills as slash commands by normalizing the frontmatter `name`.

The canonical behavioral package is:

```text
obsidian-memory-wiki
```

Compatibility aliases retain:

```text
/obsidian
/prepforreset
/wikijanitor
```

The installer includes aliases by default. Use `--no-aliases` only when command continuity is unnecessary and users will invoke the parent skill directly.

After installation, start a new session or run:

```text
/reload-skills
```

where that command is available. If a long-running gateway still has a stale slash-command cache, restart only the affected profile gateway after checking for active work.

New automation must load:

```text
--skills obsidian-memory-wiki
```

Do not create new cron or workflow dependencies on `wikijanitor,obsidian` or `prepforreset,obsidian`; those are compatibility names rather than behavioral sources of truth.

For another runtime, map the familiar commands to the parent’s Vault Operations, Reset Preparation, and Wiki Janitor Maintenance phases.
