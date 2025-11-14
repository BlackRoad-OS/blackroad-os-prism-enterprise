# Codex Automation

This directory houses utilities that support recurring engineering
rituals across the BlackRoad platform. The centerpiece is a lightweight
**BlackRoad pipeline** script that demonstrates how commits can move
from a developer workstation to deployment. The script is intentionally
modular so additional steps—such as quality gates or integration hooks—
can drop in without rewriting the entire workflow.

## Codex Entries

| ID  | Title                       | Description                                                 |
| --- | --------------------------- | ----------------------------------------------------------- |
| 001 | The First Principle         | Lucidia exists to protect and empower everyone.             |
| 003 | The Workflow Circle         | Work runs in visible capture → adjust loops.                |
| 004 | The Autonomy Manifest       | Data autonomy through consent, export, and wipe.            |
| 007 | The Resilience Code         | Failure is expected; recovery keeps service live.           |
| 012 | The Creativity Pact         | Sandbox-first rituals keep experimentation safe and playful.|
| 015 | The Trust Ledger            | Trust is tracked via a public reliability ledger.           |
| 018 | The Memory Covenant         | Memory stays purposeful, finite, and revocable.             |
| 021 | The Interface Promise       | Interfaces stay honest, accessible, and quiet.              |
| 028 | The Custodianship Code      | Stewardship keeps Lucidia healthy across generations.       |
| 033 | The Wholeness Rule          | People remain whole; balance is built into Lucidia.         |
| 041 | The Restraint Principle     | Restraint on data, models, features, and kill switches.     |
| 055 | Generative Care Frameworks  | Signal loops and rituals that propagate care inventions.    |

## BlackRoad Pipeline

```bash
python3 codex/agents/blackroad_pipeline.py "Push latest to BlackRoad.io"
```

Available commands:

* `Push latest to BlackRoad.io` – commit, push, then kick off a deploy.
* `Refresh working copy and redeploy` – update the branch before deploy.
* `Rebase branch and update site` – rebase on `origin/main` prior to push.
* `Sync Salesforce -> Airtable -> Droplet` – placeholder for connector syncs.

Each command prints the high-level actions it would perform. Real OAuth
or webhook integrations can be added later by filling in the TODO
sections.

## Codex Agent (“next” trigger watcher)

`codex/tools/codex-agent.sh` can run on any Linux host to watch for a
`next` flag, capture diagnostics, and optionally call a webhook. The
tool clears the trigger file after every run, gathers device stats, and
reboots unless `REBOOT_ON_TRIGGER=false` is set. Environment variables
(`PINGBACK_URL`, `STATE_FILE`, `NEXT_TOKEN`, `MAX_DIAG_LINES`) customise
its behaviour without editing the script.

## Auditing Historic Entries

Use the audit helper to list every entry and catch early-branch
fingerprints:

```bash
python3 codex/tools/codex_entries_audit.py
```

Add `--format json` for machine-readable output that downstream
automation can ingest.
