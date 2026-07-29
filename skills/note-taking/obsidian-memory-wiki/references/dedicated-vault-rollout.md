# Dedicated Agent Vault Pilot and Multi-Agent Rollout

Use this reference when moving a multi-profile Hermes fleet from server-era workspaces or temporary vault paths into Obsidian on one persistent desktop host.

Vault topology, ownership boundaries, migration policy, automation disposition, and final acceptance criteria are authoritative in `per-agent-vault-layout.md`. Read that contract first. This reference owns only pilot/rollout sequencing and evidence gates; it does not redefine the layout.

## Rollout sequence

1. **Inventory every active profile.** Record installed skill package, current vault path, existing Daily/Session/Janitor folders, note counts, cron job, delivery target, schedule, wrapper path, and profile scope. Keep discovery read-only.
2. **Pilot one representative agent first.** Choose an approved operator-owned profile with existing notes and a janitor schedule. Complete migration, UI acceptance, `/prepforreset`, manual janitor, and real scheduler execution before changing another profile.
3. **Pause only the pilot janitor.** Prevent writes during copy/config changes; keep unrelated agent schedules untouched.
4. **Back up before copy.** Preserve the old vault and profile `config.yaml`; record paths without secret values.
5. **Copy and prove parity.** Compare relative Markdown paths, total bytes, and a deterministic manifest hash before adding new pilot artifacts.
6. **Register and visually inspect the vault.** Open `Home.md`, confirm expected folders and links, and check for onboarding blockers or visible errors. After first open, re-read `.obsidian/core-plugins.json`, `.obsidian/templates.json`, and `.obsidian/daily-notes.json`; repair any normalized or missing settings and reopen before acceptance. Restart normally after any temporary debugging instrumentation and verify it is removed.
7. **Run Reset Preparation through a fresh Hermes process.** Require a Daily Log and Session Log with reciprocal links and a deterministic completion marker. This proves profile config loading, skill discovery, and write containment—not just filesystem access.
8. **Run the actual janitor wrapper on the target OS.** `bash -n` is not runtime proof. Confirm lock and timeout dependencies or fallbacks, then verify a real report lands inside the canonical vault.
9. **Resume and trigger the Hermes cron job.** Verify scheduler status, constant wrapper notification or silent result, report path, delivery target, and next schedule.
10. **Record the pilot and only then fan out.** Reuse the exact verified structure and wrapper behavior for the remaining agents. Promote shared skill and template changes through the package’s reviewed release path rather than silently changing every profile during the pilot.


## Evidence-bounded recovery

If a temporary or deleted vault lost notes but cron outputs/session history remain:

- create a clearly labeled recovery audit;
- cite the surviving output/session sources;
- reconstruct only facts supported by those sources;
- do not fabricate missing full Daily Logs, Session Logs, original prose, or backlinks;
- preserve the durable corpus/project records as the authoritative continuation when they are stronger than the recovered wiki evidence.

## Pilot acceptance gates

- Obsidian application installed and normal-launch UI accepted.
- Dedicated vault registered with no cross-profile nesting.
- Post-open core-plugin and Templates/Daily Notes configuration re-read and verified.
- Old note manifest parity proven before new files are added.
- Profile `config.yaml` points to the canonical vault and retains secure permissions.
- `/prepforreset` creates and verifies reciprocal Daily/Session links.
- Manual wrapper execution succeeds on the target OS.
- Actual Hermes scheduler run succeeds and writes into the canonical vault.
- Delivery target and next schedule are correct.
- Temporary debug listeners/instrumentation are removed.
- Rollback paths and durable manifest/gotcha updates are recorded.
