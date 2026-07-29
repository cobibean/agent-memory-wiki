# Per-Agent Obsidian Vault Layout

Use this reference when several persistent Hermes profiles share one workstation or server and the operator wants the Obsidian memory-wiki workflow across the fleet.

## Recommended topology

Install the Obsidian desktop application once per human workstation, but provision one isolated vault per active agent:

```text
~/Documents/Obsidian/agent-wikis/
├── <agent-a>-wiki/
├── <agent-b>-wiki/
└── <agent-c>-wiki/
```

Register each directory as a separate Obsidian vault. Do not make the common parent a vault and do not merge all agents into one shared vault.

Each agent profile should resolve only its own vault through `skills.config.obsidian_memory_wiki.vault_path` and should not receive another profile's vault path by default. This preserves ownership, retirement/export boundaries, and separation between personal, business-internal, and client material.

## Standard vault shape

```text
<agent>-wiki/
├── Home.md
├── Daily Logs/
├── Session Logs/
├── Janitor Reports/
└── Templates/
```

Obsidian creates `.obsidian/` when the folder is opened as a vault. `Home.md` should link to recent logs/reports, unresolved items, and the agent's canonical workspace or corpus without copying that repository wholesale into the vault.

## Multi-agent discovery before provisioning

Inventory every active profile, not only the profile handling the setup request:

- active roster and scope classification;
- existing memory-wiki vault config value and whether it resolves;
- installed canonical/compatibility skills;
- existing Daily Logs, Session Logs, and Janitor Reports;
- scheduled janitor jobs and spacing;
- whether the current vault target is an entire source repository rather than a dedicated wiki;
- retired profiles that should be archived rather than newly provisioned.

Treat the application install, vault provisioning, skill installation, and janitor scheduling as separate rollout surfaces.

## Migration from workspace-as-vault

When an agent's vault path points at its whole code/content repository, migrate only the memory-wiki folders unless the operator explicitly wants the entire repository indexed in Obsidian:

1. Create the dedicated target vault.
2. Copy Daily Logs, Session Logs, and Janitor Reports while preserving filenames and timestamps.
3. Search for collisions and compare counts/hashes.
4. Set the profile-local vault path to the dedicated vault.
5. Verify `/prepforreset` and a manual janitor run against the new path.
6. Verify any scheduled janitor writes to the new path.
7. Retain the old folders as a rollback snapshot until acceptance.

Do not sweep every Markdown file from the source repository into the new wiki. The repository remains the canonical project/documentation store; the vault is curated operating memory.

## Automation policy

Give each persistent active agent the canonical `obsidian-memory-wiki` skill and manual reset-preparation capability. Scheduled janitors are opt-in rather than an automatic consequence of vault creation:

- preserve existing useful janitors;
- add new janitors only when missed capture justifies recurring inference;
- stagger fleet jobs according to the operator's cron-spacing policy;
- verify the created note path, not only scheduler status, because wrappers may intentionally exit successfully after emitting a setup warning;
- archive retired-agent vaults read-only instead of creating fresh automation for retired profiles.

## Acceptance criteria

- Obsidian opens every intended vault independently.
- Each profile resolves only its assigned vault.
- Existing notes were reconciled without silent loss or duplication.
- `/prepforreset` creates a Daily Log and Session Log with reciprocal links.
- Manual janitor verification succeeds before scheduled automation is trusted.
- Scheduled output, when enabled, writes to the canonical vault and follows the marker/silence contract.
- The agent manifest records vault path, skill state, janitor policy, migration/rollback location, and backup posture.
