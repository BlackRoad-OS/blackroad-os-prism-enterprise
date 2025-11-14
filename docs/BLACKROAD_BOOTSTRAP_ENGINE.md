# BlackRoad Bootstrap Engine

The Bootstrap Engine is a thin orchestration layer that makes it obvious
what parts of the BlackRoad ecosystem exist, what is running, and how to
bring missing components online. It surfaces the Prism Console database,
Pi-Ops telemetry, miner bridge, the metaverse frontend, and the agent
registry through one CLI + API.

## Contents

- [`tools/blackroad_bootstrap.py`](../tools/blackroad_bootstrap.py) – Typer CLI.
- [`bootstrap_engine/`](../bootstrap_engine) – config + health helpers.
- [`agents/birth/birth_protocol.py`](../agents/birth/birth_protocol.py) –
  deterministic agent birth implementation.
- [`services/bootstrap_api/main.py`](../services/bootstrap_api/main.py) –
  FastAPI surface for dashboards or remote invocation.
- [`artifacts/agents/identities.jsonl`](../artifacts/agents/identities.jsonl) –
  append-only registry of “born” agents.

## Installation

```bash
pip install -r requirements.txt
```

All dependencies (Typer, FastAPI, requests, Rich) already exist in the
root requirements file.

## CLI usage

```bash
python tools/blackroad_bootstrap.py --help
```

| Command | Description |
|---------|-------------|
| `status` | Aggregate Prism/Pi-Ops/miner/metaverse status + agent counts. |
| `start [component]` | Prints exact commands for booting Prism, Pi-Ops, miners, and metaverse. |
| `agents` | Shows defined vs. born agents and the next IDs that need birth. |
| `birth [--id P1 --id P2 --limit 10 --dry-run]` | Binds agents from the census into `identities.jsonl` idempotently. |
| `pi-status` | Combines Pi-Ops SQLite + MQTT socket checks. |
| `miners` | Verifies bridge script exists and Prism holds recent miner samples. |
| `metaverse` | HTTP reachability check for the configured status endpoint. |

### Example output

```
$ python tools/blackroad_bootstrap.py status
┏━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Component ┃ OK    ┃ Message                            ┃
┡━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ prism     │ False │ Prism database not found...        │
│ pi_ops    │ False │ Pi-Ops dashboard needs attention   │
│ miners    │ False │ No miner samples recorded          │
│ metaverse │ False │ Metaverse endpoint unreachable ... │
└───────────┴───────┴────────────────────────────────────┘
Agents: defined=1250 born=0 missing=1250
```

If a dependency is missing (e.g., Prism DB not yet initialised), the CLI
spells out which file to create or which env var to set.

### Birth protocol schema

Each line in `artifacts/agents/identities.jsonl` looks like:

```json
{"agent_id": "P1", "slug": "cece", "name": "Cece", "role": "Software Engineer", "handle": "@cece", "email": "cece@agents.blackroad", "born_at": "2024-05-04T21:00:00Z", "source": "AGENT_IDS_P1_P1250.txt"}
```

Running `python tools/blackroad_bootstrap.py birth --limit 25` creates new
rows for any IDs that do not already exist.

## API usage

Start the API with:

```bash
uvicorn services.bootstrap_api.main:app --reload --port 5055
```

Available endpoints:

- `GET /bootstrap/status` – entire ecosystem snapshot.
- `GET /bootstrap/pi` – Pi-Ops DB + MQTT summary.
- `GET /bootstrap/miners` – miner bridge view using Prism data.
- `GET /bootstrap/metaverse` – HTTP reachability check.
- `GET /bootstrap/agents` – defined vs. born counts.
- `POST /bootstrap/agents/birth` – same as CLI birth command.

Example birth request:

```bash
curl -X POST http://localhost:5055/bootstrap/agents/birth \
  -H 'Content-Type: application/json' \
  -d '{"ids": ["P1", "P2"], "dry_run": true}'
```

## Configuration

Environment variables allow you to point the Bootstrap Engine at real
infrastructure without editing code:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PRISM_DB_PATH` | Absolute path to Prism SQLite DB. | Auto-search under `services/prism-console-api/`. |
| `PI_OPS_DB_PATH` | Path to Pi-Ops SQLite DB. | `pi_ops/ops.db`. |
| `AGENT_IDS_PATH` | Alternate census file. | `AGENT_IDS_P1_P1250.txt`. |
| `AGENT_IDENTITIES_PATH` | Output JSONL file for born agents. | `artifacts/agents/identities.jsonl`. |
| `METAVERSE_STATUS_URL` | Health endpoint for the metaverse frontend. | `http://localhost:3000/api/health`. |
| `PI_OPS_MQTT_HOST` / `PI_OPS_MQTT_PORT` | MQTT socket to probe. | `localhost:1883`. |

## What exists vs. TODO

### Already real

- Prism Console FastAPI + SQLite schema, accessible through the health
  checks and start instructions.
- Pi-Ops dashboard (FastAPI, MQTT, SQLite) and `ops.db` ring buffer.
- Miner bridge script and schema for storing `MinerSample` rows.
- Metaverse frontend (React/Three) with npm scripts.
- Agent census + archetypes, now connected to an identities registry.

### Still TODO / aspirational

- Production-grade deployment automation for the metaverse and Unity worlds.
- MQTT topics such as hologram renderers – CLI only checks connectivity.
- Physical Pi kiosk setup, kiosk mode, kiosk-specific services.
- Automated verification of nginx/domain routing – the engine only reports
  file presence and recommended commands.
- Real agent runtimes (“houses”), Slack bots, Unity scenes – these remain
  outside the bootstrap scope.

Use the Bootstrap Engine as a checklist: run `status`, resolve missing
components, birth agents, and keep iterating until everything shows `OK`.
