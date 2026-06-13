# Slash Command Setup

## Hermes

Hermes exposes installed skills as slash commands by normalizing the skill `name` field.

This frontmatter:

```yaml
name: prepforreset
```

becomes:

```text
/prepforreset
```

After installing the skill, reload skills:

```text
/reload-skills
```

If you are using a long-running gateway, restart or reload it if the command cache does not refresh.

Some messaging platforms cap visible command menus. If `/prepforreset` does not show in autocomplete, type it manually before assuming it is missing.

## Generic command registry

Map `/prepforreset` to this behavior:

```text
Load `prepforreset`, load `obsidian`, resolve OBSIDIAN_VAULT_PATH, write/update Daily Logs and Session Logs, then return the lean context-reset handoff.
```

Map `/wikijanitor` to this behavior:

```text
Load `wikijanitor`, load `obsidian`, review recent sessions and existing memory-wiki notes, create a Janitor Report if there was activity, and notify only for review/uncertainty.
```

## No command registry

If your runtime has no slash commands, use the copy-paste prompt in [`agent-copy-paste-prompt.md`](agent-copy-paste-prompt.md). The agent can treat phrases like “prep for reset” as the trigger.
