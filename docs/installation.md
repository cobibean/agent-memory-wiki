# Installation

## Prerequisites

- Bash
- Python 3
- Hermes Agent with `hermes config set/get` support
- An existing Obsidian vault/Markdown directory, unless you use `--init-vault`

## Hermes installer

Inspect the resolved destinations first:

```bash
bash scripts/install-hermes.sh \
  --profile my-agent \
  --vault "/absolute/path/to/my-agent-wiki" \
  --dry-run
```

Install into an existing vault:

```bash
bash scripts/install-hermes.sh \
  --profile my-agent \
  --vault "/absolute/path/to/my-agent-wiki"
```

Or create the starter vault:

```bash
bash scripts/install-hermes.sh \
  --profile my-agent \
  --vault "/absolute/path/to/my-agent-wiki" \
  --init-vault
```

### Targeting rules

- `--profile my-agent` installs to `~/.hermes/profiles/my-agent` and overrides inherited `HERMES_HOME`.
- `--profile default` installs to `~/.hermes`.
- `--hermes-home PATH` targets an exact Hermes home and cannot be combined with `--profile`.
- With neither option, the installer uses `HERMES_HOME` when set, otherwise `~/.hermes`.

Profile names are validated and cannot contain path separators or traversal segments.

### Installed package

By default the installer adds:

- `obsidian-memory-wiki` — canonical parent;
- `obsidian`, `prepforreset`, `wikijanitor` — command-compatibility aliases.

Use `--no-aliases` for a parent-only install.

Every real install:

- validates the destination and vault;
- creates a unique backup directory under the target Hermes home;
- backs up each replaced skill and the prior `config.yaml` when present;
- replaces skill directories completely so removed upstream files do not linger;
- writes `skills.config.obsidian_memory_wiki.vault_path` through `hermes config set`;
- hardens the resulting `config.yaml` and its backup to `0600`.

The installer never deletes or rewrites existing vault notes. `--init-vault` creates missing starter files but leaves existing files untouched.

## Readiness verification

After installation:

1. Start a new Hermes session or run `/reload-skills` where available.
2. Confirm the canonical skill exists under the intended profile—not merely the ambient profile.
3. Run `hermes -p my-agent config get skills.config.obsidian_memory_wiki.vault_path` and verify the intended vault.
4. Invoke `/prepforreset` and verify real Daily and Session note paths.
5. If initialized, open the vault in Obsidian and enable Daily Notes and Templates.

Do not infer readiness only from successful file copying.

## Updating

```bash
git pull --ff-only
bash scripts/install-hermes.sh --profile my-agent --vault "/absolute/path/to/my-agent-wiki"
```

Review [CHANGELOG.md](../CHANGELOG.md) before updating across a major version.

## Rollback

The installer prints a backup path such as:

```text
~/.hermes/profiles/my-agent/agent-memory-wiki.backup.<timestamp>.<unique-suffix>
```

To roll back:

1. Stop or avoid active runs on the affected profile.
2. Move the current affected skill directories aside.
3. Restore the desired directories from the printed backup.
4. Restore `profile-config.yaml` to the profile `config.yaml` if the prior vault configuration must also be restored.
5. Start a new session or reload skills and repeat readiness verification.

The vault is separate and is not part of installer rollback.

## Generic-agent installation

For another Markdown-skill runtime:

1. Install `skills/note-taking/obsidian-memory-wiki/` as the canonical package.
2. Install alias folders only if command continuity is useful.
3. Expose a concrete vault path equivalent to `obsidian_memory_wiki.vault_path` (or use the `OBSIDIAN_VAULT_PATH` compatibility fallback).
4. Give the agent read/search/write/patch access limited to that vault.
5. Map `/prepforreset` and `/wikijanitor` to the corresponding parent phases if the runtime does not derive commands from skill names.
6. Test inside a disposable vault before production use.

The scheduled wrapper is Hermes-specific; port its lock, timeout, and exact marker-envelope contract rather than copying its CLI unchanged.
