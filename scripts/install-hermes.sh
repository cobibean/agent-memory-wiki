#!/usr/bin/env bash
set -euo pipefail
umask 077

PROFILE=""
VAULT=""
EXPLICIT_HERMES_HOME=""
INIT_VAULT=0
INSTALL_ALIASES=1
DRY_RUN=0
HERMES_BIN="${HERMES_BIN:-hermes}"
BACKUP_ROOT=""
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
Install Agent Memory Wiki v2 into a Hermes profile.

Usage:
  bash scripts/install-hermes.sh --vault PATH [options]

Required:
  --vault PATH          Existing vault directory, unless --init-vault is used.

Profile targeting:
  --profile NAME        Install to ~/.hermes/profiles/NAME. The special name
                        "default" installs to ~/.hermes. This overrides an
                        inherited HERMES_HOME.
  --hermes-home PATH    Install to this exact Hermes home. Cannot be combined
                        with --profile.

Options:
  --init-vault          Create the vault and a safe starter structure.
  --no-aliases          Install only obsidian-memory-wiki; omit the legacy
                        /obsidian, /prepforreset, and /wikijanitor aliases.
  --dry-run             Print resolved destinations without changing files.
  -h, --help            Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      [[ $# -ge 2 ]] || { echo "--profile requires a value" >&2; exit 2; }
      PROFILE="$2"; shift 2 ;;
    --hermes-home)
      [[ $# -ge 2 ]] || { echo "--hermes-home requires a value" >&2; exit 2; }
      EXPLICIT_HERMES_HOME="$2"; shift 2 ;;
    --vault)
      [[ $# -ge 2 ]] || { echo "--vault requires a value" >&2; exit 2; }
      VAULT="$2"; shift 2 ;;
    --init-vault) INIT_VAULT=1; shift ;;
    --no-aliases) INSTALL_ALIASES=0; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$VAULT" ]] || { echo "--vault is required" >&2; usage >&2; exit 2; }
[[ -z "$PROFILE" || -z "$EXPLICIT_HERMES_HOME" ]] || {
  echo "Use either --profile or --hermes-home, not both." >&2
  exit 2
}
[[ "$VAULT" != *$'\n'* && "$VAULT" != *$'\r'* ]] || {
  echo "Vault paths cannot contain newlines." >&2
  exit 2
}
# This is the literal expansion prefix we reject.
# shellcheck disable=SC2016
literal_config_expansion='${'
[[ "$VAULT" != *"$literal_config_expansion"* ]] || {
  echo "Vault paths containing literal \${...} segments are unsupported because Hermes expands config variables." >&2
  exit 2
}

if [[ -n "$PROFILE" ]]; then
  [[ "$PROFILE" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]] || {
    echo "Invalid profile name. Use 1-64 letters, numbers, dots, underscores, or hyphens; do not use path separators." >&2
    exit 2
  }
  if [[ "$PROFILE" == "default" ]]; then
    TARGET_HERMES_HOME="$HOME/.hermes"
  else
    TARGET_HERMES_HOME="$HOME/.hermes/profiles/$PROFILE"
  fi
elif [[ -n "$EXPLICIT_HERMES_HOME" ]]; then
  TARGET_HERMES_HOME="$EXPLICIT_HERMES_HOME"
elif [[ -n "${HERMES_HOME:-}" ]]; then
  TARGET_HERMES_HOME="$HERMES_HOME"
else
  TARGET_HERMES_HOME="$HOME/.hermes"
fi

command -v python3 >/dev/null 2>&1 || {
  echo "python3 is required for safe path and profile configuration handling." >&2
  exit 2
}
command -v "$HERMES_BIN" >/dev/null 2>&1 || {
  echo "Hermes executable was not found: $HERMES_BIN" >&2
  exit 2
}

canonical_path() {
  python3 - "$1" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).expanduser().resolve(strict=False))
PY
}

TARGET_HERMES_HOME="$(canonical_path "$TARGET_HERMES_HOME")"
VAULT="$(canonical_path "$VAULT")"
CANONICAL_HOME="$(canonical_path "$HOME")"
if [[ "$TARGET_HERMES_HOME" == "/" || "$TARGET_HERMES_HOME" == "$CANONICAL_HOME" ]]; then
  echo "Refusing unsafe Hermes home target: $TARGET_HERMES_HOME" >&2
  exit 2
fi
if [[ "$VAULT" == "/" ]]; then
  echo "Refusing to use the filesystem root as a vault." >&2
  exit 2
fi
SKILLS_DEST="$TARGET_HERMES_HOME/skills/note-taking"
CONFIG_FILE="$TARGET_HERMES_HOME/config.yaml"
CANONICAL_SRC="$SRC_DIR/skills/note-taking/obsidian-memory-wiki"
ALIASES=(obsidian prepforreset wikijanitor)

[[ -f "$CANONICAL_SRC/SKILL.md" ]] || {
  echo "Canonical skill source is missing: $CANONICAL_SRC/SKILL.md" >&2
  exit 2
}
if [[ "$INSTALL_ALIASES" -eq 1 ]]; then
  for skill in "${ALIASES[@]}"; do
    [[ -f "$SRC_DIR/skills/note-taking/$skill/SKILL.md" ]] || {
      echo "Compatibility alias source is missing: $skill/SKILL.md" >&2
      exit 2
    }
  done
fi
if [[ ! -d "$VAULT" && "$INIT_VAULT" -ne 1 ]]; then
  echo "Vault does not exist: $VAULT" >&2
  echo "Create it first or rerun with --init-vault." >&2
  exit 2
fi

printf 'Agent Memory Wiki install plan\n'
printf '  Hermes home: %s\n' "$TARGET_HERMES_HOME"
printf '  Skills root: %s\n' "$SKILLS_DEST"
printf '  Vault: %s\n' "$VAULT"
printf '  Initialize vault: %s\n' "$INIT_VAULT"
printf '  Compatibility aliases: %s\n' "$INSTALL_ALIASES"
if [[ "$DRY_RUN" -eq 1 ]]; then
  exit 0
fi

mkdir -p "$SKILLS_DEST" "$TARGET_HERMES_HOME"
BACKUP_ROOT="$(mktemp -d "$TARGET_HERMES_HOME/agent-memory-wiki.backup.$(date -u +%Y%m%dT%H%M%SZ).XXXXXX")"
install_failed() {
  status=$?
  printf 'Installation failed with status %s. Backup: %s\n' "$status" "$BACKUP_ROOT" >&2
  exit "$status"
}
trap install_failed ERR

backup_and_replace_skill() {
  local skill="$1"
  local src="$2"
  local dest="$SKILLS_DEST/$skill"
  if [[ -e "$dest" || -L "$dest" ]]; then
    cp -R "$dest" "$BACKUP_ROOT/$skill"
    rm -rf "${dest:?}"
  fi
  cp -R "$src" "$dest"
}

backup_and_replace_skill "obsidian-memory-wiki" "$CANONICAL_SRC"
if [[ "$INSTALL_ALIASES" -eq 1 ]]; then
  for skill in "${ALIASES[@]}"; do
    backup_and_replace_skill "$skill" "$SRC_DIR/skills/note-taking/$skill"
  done
else
  for skill in "${ALIASES[@]}"; do
    dest="$SKILLS_DEST/$skill"
    if [[ -e "$dest" || -L "$dest" ]]; then
      cp -R "$dest" "$BACKUP_ROOT/$skill"
      rm -rf "${dest:?}"
    fi
  done
fi

if [[ -f "$CONFIG_FILE" ]]; then
  cp -p "$CONFIG_FILE" "$BACKUP_ROOT/profile-config.yaml"
  chmod 600 "$BACKUP_ROOT/profile-config.yaml"
fi
HERMES_HOME="$TARGET_HERMES_HOME" "$HERMES_BIN" config set --force \
  skills.config.obsidian_memory_wiki.vault_path "$VAULT" >/dev/null
chmod 600 "$CONFIG_FILE"

if [[ "$INIT_VAULT" -eq 1 ]]; then
  mkdir -p "$VAULT/Daily Logs" "$VAULT/Session Logs" "$VAULT/Janitor Reports" "$VAULT/Templates" "$VAULT/.obsidian"
  for template in daily-log.md session-log.md janitor-report.md; do
    if [[ ! -e "$VAULT/Templates/$template" ]]; then
      cp "$CANONICAL_SRC/templates/$template" "$VAULT/Templates/$template"
    fi
  done
  if [[ ! -e "$VAULT/Home.md" ]]; then
    cat > "$VAULT/Home.md" <<'MD'
# Agent Memory Wiki

## Navigation

- [[Vault Guide]]
- [[Daily Logs]]
- [[Session Logs]]
- [[Janitor Reports]]

This vault is curated operating memory. Project repositories and domain systems remain authoritative for their own artifacts.
MD
  fi
  if [[ ! -e "$VAULT/Vault Guide.md" ]]; then
    cat > "$VAULT/Vault Guide.md" <<'MD'
# Vault Guide

- `Daily Logs/` contains day-level summaries.
- `Session Logs/` contains deeper work-block handoffs.
- `Janitor Reports/` contains optional reconciliation reports.
- `Templates/` contains starter templates.

Keep secrets out of notes. Reference credential locations instead of values.
Search before creating notes, preserve time-bounded history, and update an existing authoritative session note when work continues.
MD
  fi
  if [[ ! -e "$VAULT/.obsidian/templates.json" ]]; then
    printf '%s\n' '{"folder":"Templates"}' > "$VAULT/.obsidian/templates.json"
  fi
  if [[ ! -e "$VAULT/.obsidian/daily-notes.json" ]]; then
    printf '%s\n' '{"folder":"Daily Logs","format":"YYYY-MM-DD","template":"Templates/daily-log"}' > "$VAULT/.obsidian/daily-notes.json"
  fi
fi

trap - ERR
printf '\nInstalled Agent Memory Wiki v2.\n\n'
printf 'Backup: %s\n' "$BACKUP_ROOT"
printf 'Hermes home: %s\n' "$TARGET_HERMES_HOME"
printf 'Canonical skill: %s\n' "$SKILLS_DEST/obsidian-memory-wiki"
printf 'Vault: %s\n\n' "$VAULT"
printf 'Next steps:\n'
printf '1. Start a new Hermes session or run /reload-skills where available.\n'
printf '2. Verify /prepforreset if compatibility aliases were installed.\n'
printf '3. If the vault was initialized, open it in Obsidian and enable Daily Notes and Templates.\n'
