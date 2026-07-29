# Scheduling Wiki Janitor

`wikijanitor` is optional. Enable recurring model-powered reconciliation only when missed capture and agent activity justify it.

## 1. Install and configure first

Install `obsidian-memory-wiki`, verify `skills.config.obsidian_memory_wiki.vault_path`, and successfully run `/prepforreset` or a manual janitor before scheduling anything.

Copy the wrapper into the selected profile’s scripts directory:

```bash
cp scripts/wiki-janitor-cron-wrapper.sh.example \
  "$HOME/.hermes/profiles/my-agent/scripts/wikijanitor_cron.sh"
chmod 700 "$HOME/.hermes/profiles/my-agent/scripts/wikijanitor_cron.sh"
```

For the default profile, use `$HOME/.hermes/scripts/`.

The wrapper reads these profile settings through `hermes config get`:

- `skills.config.obsidian_memory_wiki.vault_path` — must resolve to an existing directory;
- `skills.config.obsidian_memory_wiki.janitor_timeout_seconds` — defaults to `300`;
- `skills.config.obsidian_memory_wiki.janitor_max_turns` — defaults to `100`.

Set overrides explicitly when needed:

```bash
hermes -p my-agent config set skills.config.obsidian_memory_wiki.janitor_timeout_seconds 300
hermes -p my-agent config set skills.config.obsidian_memory_wiki.janitor_max_turns 100
```

The process-level controls are:

- `HERMES_PROFILE` — preferred explicit profile; otherwise derived from a named profile `HERMES_HOME`, then defaults to `default`;
- `HERMES_BIN` — defaults to `hermes`;
- `OBSIDIAN_VAULT_PATH`, `WIKI_JANITOR_TIMEOUT_SECONDS`, and `WIKI_JANITOR_MAX_TURNS` — optional compatibility/debug overrides;
- `WIKI_JANITOR_LOCK_ROOT` — optional profile-local override.

Do not put configuration or secret values directly in the wrapper.

## 2. Size the outer scheduler timeout

The cron scheduler’s script timeout must exceed the wrapper timeout with room for startup and teardown. For a 300-second wrapper:

```bash
hermes -p my-agent config set cron.script_timeout_seconds 360
```

## 3. Create the script-only job

Use an explicit approved delivery destination rather than relying on a platform home-channel default:

```bash
hermes -p my-agent cron create \
  '30 3 * * *' \
  --name 'Memory wiki janitor' \
  --deliver '<platform>:<approved-destination-id>' \
  --no-agent \
  --script wikijanitor_cron.sh
```

Cron expressions use the scheduler host’s timezone. Inspect the created job’s next-run timestamp and confirm it matches the intended local time.

The scheduler runs the script only. The script invokes Hermes with the selected profile and the canonical `obsidian-memory-wiki` skill.

## 4. Marker contract

A no-activity or routine-only reconciliation run returns exactly:

```text
[[WIKI_JANITOR_SILENT]]
```

The wrapper suppresses it.

A run with warnings, gaps, uncertainty, or actions requiring user attention returns:

```text
[[WIKI_JANITOR_NOTIFY]]
<concise internal digest>
[[WIKI_JANITOR_END]]
```

The wrapper validates one complete exact-line envelope but never forwards model-authored digest text. It emits a constant notification directing the user to the newest protected Janitor Report. Raw, unmarked, partial, duplicate-marker, and envelope-body output is suppressed.

## 5. Verify end to end

1. Run the private wrapper manually under the target profile.
2. Confirm a clean/routine run is silent or a notify run emits only the constant wrapper-authored notification.
3. Run the cron job once with `hermes -p my-agent cron run <job-id>`.
4. Verify the actual Janitor Report path inside the intended vault.
5. Verify delivery contains no scheduler error.
6. Verify the next-run timestamp and timezone.
7. Confirm no stale lock directory remains under the configured lock root.

A scheduler status of `ok` alone is not proof that the correct vault was written.

## Failure behavior

- Missing vault, invalid profile, missing Hermes binary, timeout, and malformed output produce a concise alert without raw output.
- Overlapping runs do not start a second agent invocation.
- The wrapper does not claim that raw diagnostics were logged; sensitive raw output is deliberately not persisted.
- If a process is killed outside normal signal handling and leaves a stale lock directory, verify no run is active and remove only that profile’s lock directory.
