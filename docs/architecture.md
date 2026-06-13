# Architecture

Agent Memory Wiki is split into three skills so each layer has a clear job.

```text
obsidian       -> vault mechanics and path safety
prepforreset   -> manual context-reset capture
wikijanitor    -> optional scheduled/manual reconciliation
```

## Why not just one skill?

`prepforreset` needs safe vault operations, but those operations are also useful to `wikijanitor` and future note-writing workflows. Keeping `obsidian` separate prevents every workflow from re-implementing path resolution and safety rules.

`wikijanitor` is optional because not every user wants scheduled review. It belongs in the same repo because it is the supporting reliability layer for the same memory-wiki pattern.

## Data flow

```text
Conversation / session history
        |
        v
/prepforreset  ---> Daily Logs/YYYY-MM-DD.md
        |        -> Session Logs/YYYY-MM-DD-topic.md
        v
short handoff in chat

Nightly/manual /wikijanitor
        |
        v
Janitor Reports/YYYY-MM-DD-last-24h.md
        |
        v
routine backlinks / review candidates
```

## Provisioning boundary

The product/installer should provide:

- the vault root
- expected folders
- environment variables/config
- command registration
- optional schedule

The skills should enforce:

- path safety
- note structure
- no secret values
- conservative writes
- clear user-facing handoffs
