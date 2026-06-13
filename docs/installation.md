# Installation

## Prerequisites

- An agent runtime that can load Markdown skills.
- An Obsidian vault or any Markdown folder you want to use as a vault.
- A concrete vault path available to the agent as `OBSIDIAN_VAULT_PATH`.

## Hermes install

```bash
git clone https://github.com/cobibean/agent-memory-wiki.git
cd agent-memory-wiki
bash scripts/install-hermes.sh --vault "$HOME/Documents/Obsidian Vault"
```

For a named Hermes profile:

```bash
bash scripts/install-hermes.sh --profile my-profile --vault "/absolute/path/to/Obsidian Vault"
```

Then refresh your running session:

```text
/reload-skills
```

or restart the gateway / start a new CLI session.

## Manual install

Copy:

```text
skills/note-taking/obsidian/
skills/note-taking/prepforreset/
skills/note-taking/wikijanitor/
```

into your runtime's skill directory.

Configure:

```bash
OBSIDIAN_VAULT_PATH="/absolute/path/to/Obsidian Vault"
```

Create:

```text
Daily Logs/
Session Logs/
Janitor Reports/
```

inside that vault.

## Verification

Ask your agent:

```text
What skills can you see for Agent Memory Wiki? Do you have obsidian, prepforreset, and wikijanitor? What vault path will you use? Do not write notes yet.
```

Then run a real capture when you are ready:

```text
/prepforreset
```
