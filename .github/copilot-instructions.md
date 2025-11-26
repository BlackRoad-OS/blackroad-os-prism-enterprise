## Copilot / AI Agent instructions — BlackRoad Prism Console

This is a compact, actionable guide for automated coding agents working in this monorepo. Keep edits small, confirm with a maintainer for risky or scope-changing work, and prefer adding tests/docs alongside code changes.

Key facts (big picture)

- Monorepo layout: `srv/` (servers), `sites/` (frontends), `apps/` (standalones), `packages/` (shared libs).
- Runtime: Express API at `srv/blackroad-api` (entry: `server_full.js`) using SQLite and Socket.IO; frontend at `sites/blackroad` (Vite + React, dev port 5173); LLM bridge commonly at `srv/lucidia-llm/` (FastAPI stub, default 127.0.0.1:8000).

Quick dev commands

- Bootstrap (create .env, install deps): `bash ops/install.sh`
- Start API (dev): `cd srv/blackroad-api && npm run dev`
- Start frontend (dev from repo root): `npm run dev:site`

Repo rules & patterns you must follow

- Dependency hygiene: do not manually edit package.json for packages — run `node tools/dep-scan.js --dir <package>` or `bash ops/install.sh` and commit the tool's outputs only.
- Env vars: add or change defaults in `srv/blackroad-api/.env.example`.
- Feature flags: reuse existing flags (e.g. `BILLING_DISABLE`, `ALLOW_SHELL`) instead of adding global toggles.

Critical files to inspect before edits

- `srv/blackroad-api/server_full.js` — API entry/middleware
- `srv/blackroad-api/.env.example` — canonical env names
- `ops/install.sh`, `tools/dep-scan.js`, `tools/verify-runtime.sh` — installer and dependency tooling
- `docker-compose*.yml` — local orchestration and common ports (4000 / 5173 / 8000)
- `codex/`, `scripts/`, `tools/` — chat-first automation and deploy scaffolds

Integration notes & common pitfalls

- Many scripts assume an LLM at 127.0.0.1:8000 — prefer making that URL configurable via env and update `.env.example`.
- Stripe/webhook code lives under `srv/blackroad-api` — validate webhook signature handling in staging before production.
- Database defaults to a local SQLite file; avoid blind schema migrations and back up before changes.

PR & safety checklist (copy into PR body)

- Short summary (1-2 lines)
- Files changed and why
- Commands run (lint/test/build) and results
- Env vars added and `.env.example` updated? (yes/no)
- Any docker-compose or port changes? (yes/no)

Where to look first (recommended order)

1. `srv/blackroad-api/server_full.js`
2. `srv/blackroad-api/.env.example`
3. `ops/install.sh`, `tools/dep-scan.js`
4. `docker-compose*.yml`
5. `codex/`, `scripts/`, `tools/`

If you'd like, I can also add a short `.github/PULL_REQUEST_TEMPLATE.md` and an `AGENT_CHECKLIST.md` with the exact commands used for lint/test/dep-scan.

## When Copilot is enabled

If your organization enables GitHub Copilot agent features for this Codespace, Copilot will consult `.github/copilot-instructions.md` and may surface quick actions in the chat panel. Recommended additions for that flow:

- Keep the top of this file small and actionable (the agent reads it). Avoid long narrative sections.
- Emphasize imperative commands (e.g., `bash ops/install.sh`, `node tools/dep-scan.js --dir srv/blackroad-api --save`).
- Document any environment-specific defaults in `srv/blackroad-api/.env.example` (LLM_URL, PORT, DB_PATH).

For organization-level Copilot setup instructions, see `COPILOT_SETUP.md` in the repo root.

## Copilot / AI Agent instructions — BlackRoad Prism Console

This is a compact, actionable guide for automated coding agents working in this monorepo. Keep edits small, confirm with a maintainer for risky or scope-changing work, and prefer adding tests/docs alongside code changes.

Key facts (big picture)

- Monorepo layout: `srv/` (servers), `sites/` (frontends), `apps/` (standalones), `packages/` (shared libs).
- Runtime: Express API at `srv/blackroad-api` (entry: `server_full.js`) using SQLite and Socket.IO; frontend at `sites/blackroad` (Vite + React, dev port 5173); LLM bridge commonly at `srv/lucidia-llm/` (FastAPI stub, default 127.0.0.1:8000).

Quick dev commands

- Bootstrap (create .env, install deps): `bash ops/install.sh`
- Start API (dev): `cd srv/blackroad-api && npm run dev`
- Start frontend (dev from repo root): `npm run dev:site`

Repo rules & patterns you must follow

- Dependency hygiene: do not manually edit package.json for packages — run `node tools/dep-scan.js --dir <package>` or `bash ops/install.sh` and commit the tool's outputs only.
- Env vars: add or change defaults in `srv/blackroad-api/.env.example`.
- Feature flags: reuse existing flags (e.g. `BILLING_DISABLE`, `ALLOW_SHELL`) instead of adding global toggles.

Critical files to inspect before edits

- `srv/blackroad-api/server_full.js` — API entry/middleware
- `srv/blackroad-api/.env.example` — canonical env names
- `ops/install.sh`, `tools/dep-scan.js`, `tools/verify-runtime.sh` — installer and dependency tooling
- `docker-compose*.yml` — local orchestration and common ports (4000 / 5173 / 8000)
- `codex/`, `scripts/`, `tools/` — chat-first automation and deploy scaffolds

Integration notes & common pitfalls

- Many scripts assume an LLM at 127.0.0.1:8000 — prefer making that URL configurable via env and update `.env.example`.
- Stripe/webhook code lives under `srv/blackroad-api` — validate webhook signature handling in staging before production.
- Database defaults to a local SQLite file; avoid blind schema migrations and back up before changes.

PR & safety checklist (copy into PR body)

- Short summary (1-2 lines)
- Files changed and why
- Commands run (lint/test/build) and results
- Env vars added and `.env.example` updated? (yes/no)
- Any docker-compose or port changes? (yes/no)

Where to look first (recommended order)

1. `srv/blackroad-api/server_full.js`
2. `srv/blackroad-api/.env.example`
3. `ops/install.sh`, `tools/dep-scan.js`
4. `docker-compose*.yml`
5. `codex/`, `scripts/`, `tools/`

If you'd like, I can also add a short `.github/PULL_REQUEST_TEMPLATE.md` and an `AGENT_CHECKLIST.md` with the exact commands used for lint/test/dep-scan.
# BlackRoad Prism Console - AI Coding Agent Guide

## Architecture Overview

BlackRoad Prism Console is a **deterministic, file-backed system** for PLM (Product Lifecycle Management), manufacturing operations, treasury, and enterprise automation. The system uses **bot orchestration** with strict guardrails and performance SLOs.

### Core Stack
- **Backend**: Python CLI (`brc` command) with Typer + file-based storage
- **Frontend**: Next.js/React apps in `/apps/*` and `/sites/*`
- **API**: Express.js server at `srv/blackroad-api/server_full.js` (port 4000)
- **Database**: SQLite + file artifacts in `/artifacts/*`
- **Deployment**: Docker Compose + K8s, with chat-driven pipeline tools

### Key Patterns

**Bot Architecture**: All business logic lives in `/bots/*` extending `BaseBot`. Each bot has strict:
- Mission statement with INPUTS/OUTPUTS/KPIS/GUARDRAILS/HANDOFFS
- Performance SLOs (`orchestrator/slo.py`)
- Red team validation in `orchestrator.py`

**CLI-First Design**: The `brc` command (`cli/console.py`) is the primary interface:
```bash
brc task:create --goal "Build 13-week cash view"
brc task:route --id T0001 --bot "Treasury-BOT"
brc plm:bom:explode --item PROD-100 --rev A --level 3
```

**File-Based Storage**: No external databases - everything persists to `/artifacts/*` as JSON/CSV for deterministic behavior.

## Development Workflows

### Adding New Bots
1. Create `bots/my_bot.py` extending `BaseBot`
2. Include complete docstring with MISSION/INPUTS/OUTPUTS/KPIS/GUARDRAILS/HANDOFFS
3. Register in `bots/__init__.py` auto-discovery
4. Add SLO targets in `orchestrator/slo.py`

### Testing Strategy
- `pytest -q` for unit tests
- `make demo` for full PLM/MFG workflow validation
- Determinism checks: artifacts must hash identically across runs
- Contract validation via JSON schemas in `scripts/validate_contracts.py`

### Chat-Driven Deployment
Use natural language deployment commands:
```bash
python scripts/blackroad_sync.py "Push latest to BlackRoad.io"
bin/blackroad-sync refresh
```

## Project-Specific Conventions

**Naming**: Services use hyphenated names (`blackroad-api`), bots use PascalCase with -BOT suffix (`Treasury-BOT`)

**Port Allocation**:
- 3000: Next.js frontend
- 4000: Express API
- 8000: LLM stub service

**Environment Variables**: All sensitive config via `.env` files, never hardcoded

**Codacy Integration**: After ANY file edit, you MUST run `codacy_cli_analyze` for quality gates

## Key Integration Points

**Task Orchestration**: Tasks flow through `Task` → `Bot` → `BotResponse` with perf tracking and red team validation

**Multi-Language**: Python CLI + Node.js services communicate via file artifacts, not APIs

**Docker/DevContainers**: Use `.devcontainer/devcontainer.json` for consistent dev environments with Node 20, Go 1.22, Terraform

**GitHub Actions**: Extensive automation with ~200 workflows covering security, deployment, ChatOps, and quality gates

## Critical Commands
```bash
# Core development
make setup && make test && make lint
brc bot:list  # See available bots
make demo     # Full system validation

# Deployment
make build && make deploy PR=123
docker compose up --build app

# Quality gates
python scripts/validate_contracts.py
bash scripts/hash_artifacts.sh
```

**Security Note**: This system emphasizes deterministic, offline-first operation with no external API dependencies in core business logic.
