#!/usr/bin/env bash
set -euo pipefail

PROFILE=""
VAULT=""
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'USAGE'
Install Agent Memory Wiki skills into a Hermes profile.

Usage:
  bash scripts/install-hermes.sh --vault "/path/to/Obsidian Vault" [--profile NAME]

Options:
  --vault PATH      Required. Obsidian vault path for OBSIDIAN_VAULT_PATH.
  --profile NAME    Optional. Hermes profile name. Omit for default ~/.hermes.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) PROFILE="${2:-}"; shift 2 ;;
    --vault) VAULT="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$VAULT" ]]; then
  echo "Missing --vault" >&2
  usage
  exit 2
fi

if [[ "$VAULT" != /* ]]; then
  echo "Vault path must be absolute: $VAULT" >&2
  exit 2
fi

if [[ -n "$PROFILE" ]]; then
  HERMES_HOME="${HERMES_HOME:-$HOME/.hermes/profiles/$PROFILE}"
else
  HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
fi

SKILLS_DEST="$HERMES_HOME/skills/note-taking"
mkdir -p "$SKILLS_DEST"
mkdir -p "$VAULT/Daily Logs" "$VAULT/Session Logs" "$VAULT/Janitor Reports"

BACKUP_ROOT="$HERMES_HOME/skills.backup.agent-memory-wiki.$(date -u +%Y%m%dT%H%M%SZ)"
for skill in obsidian prepforreset wikijanitor; do
  if [[ -e "$SKILLS_DEST/$skill" ]]; then
    mkdir -p "$BACKUP_ROOT"
    cp -R "$SKILLS_DEST/$skill" "$BACKUP_ROOT/$skill"
    rm -rf "$SKILLS_DEST/$skill"
  fi
  cp -R "$SRC_DIR/skills/note-taking/$skill" "$SKILLS_DEST/$skill"
done

ENV_FILE="$HERMES_HOME/.env"
mkdir -p "$(dirname "$ENV_FILE")"
touch "$ENV_FILE"
chmod 600 "$ENV_FILE"

if grep -q '^OBSIDIAN_VAULT_PATH=' "$ENV_FILE"; then
  tmp="$(mktemp)"
  awk -v v="$VAULT" 'BEGIN{done=0} /^OBSIDIAN_VAULT_PATH=/{print "OBSIDIAN_VAULT_PATH=" v; done=1; next} {print} END{if(!done) print "OBSIDIAN_VAULT_PATH=" v}' "$ENV_FILE" > "$tmp"
  cat "$tmp" > "$ENV_FILE"
  rm -f "$tmp"
else
  printf '\nOBSIDIAN_VAULT_PATH=%s\n' "$VAULT" >> "$ENV_FILE"
fi

cat <<EOF
Installed Agent Memory Wiki skills.

Hermes home: $HERMES_HOME
Skills:      $SKILLS_DEST/{obsidian,prepforreset,wikijanitor}
Vault:       $VAULT

Next steps:
1. In a running Hermes session/gateway, run: /reload-skills
2. Try: /prepforreset
EOF
