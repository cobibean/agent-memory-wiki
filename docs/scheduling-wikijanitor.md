# Scheduling Wiki Janitor

`wikijanitor` is optional. Use it when you want a daily reliability pass that catches missed or incomplete memory-wiki capture.

## Recommended schedule

Run once per day, usually around 3:30am local time.

## Cron wrapper contract

A scheduled wrapper should:

- set `OBSIDIAN_VAULT_PATH`
- run the agent with the `wikijanitor` skill/command
- use a lock to avoid overlapping runs
- set a bounded timeout
- suppress raw model output on failure
- parse the marker contract:
  - `[[WIKI_JANITOR_NOTIFY]]` means send the digest
  - `[[WIKI_JANITOR_SILENT]]` means send nothing

See [`../scripts/wiki-janitor-cron-wrapper.sh.example`](../scripts/wiki-janitor-cron-wrapper.sh.example).

## Hermes example

Copy the wrapper into your Hermes scripts directory, edit the profile and vault path, then create a script-only cron job using your Hermes version's cron command.

The exact command can vary by Hermes version, but the shape is:

```bash
hermes cron create '30 3 * * *' --no-agent --script wiki-janitor-cron-wrapper.sh --profile my-profile
```

If your Hermes version does not expose those flags, create the cron through the interactive `/cron` UI or your platform's scheduler.

## Safety notes

- Do not schedule janitor before the vault path is configured.
- Do not dump raw captured agent output into notifications.
- Do not let routine cleanup spam the user.
- Do not create full missing Session Logs automatically; report gaps.
