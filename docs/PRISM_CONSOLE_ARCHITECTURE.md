# Prism Console Architecture

**Version:** 1.0.0
**Last Updated:** 2025-11-15
**Status:** Pre-production (hardening in progress)

## Overview

Blackroad Prism Console is the **observability and orchestration control plane** for the BlackRoad ecosystem. It provides unified dashboards, agent coordination, miner telemetry, and runbook execution across distributed services.

### Core Responsibilities

- **Observability**: Aggregate metrics, logs, and telemetry from all ecosystem services
- **Agent Coordination**: Registry, job orchestration, and event logging for 100+ agents
- **Runbook Execution**: Operational procedure catalog with validated execution
- **Miner Telemetry**: Real-time hashrate, share acceptance, and hardware monitoring
- **Unified API**: Single API surface for web/mobile consoles and CLI tools

### What Prism is NOT

- **NOT a blockchain node** – Delegates to external RoadChain service
- **NOT a wallet service** – Delegates to external RoadWallet API
- **NOT an LLM inference engine** – Delegates to Lucidia services
- **NOT a quantum simulator** – Delegates to Quantum Math Lab

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PRISM CONSOLE                               │
│  (Control Plane / Observability / Orchestration Layer)            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐      ┌─────────────────────────────────┐ │
│  │ Prism Console Web   │─────▶│  Prism Console API              │ │
│  │ (Next.js 14)        │      │  (FastAPI)                      │ │
│  │                     │ SSE  │                                 │ │
│  │ - Dashboards        │◀─────│  - Agent Registry               │ │
│  │ - Agent Catalog     │      │  - Miner Telemetry Ingestion    │ │
│  │ - Runbook UI        │      │  - Runbook Execution Orchestrator│ │
│  │ - Miner Telemetry   │      │  - Metrics Aggregation          │ │
│  └─────────────────────┘      │  - SSE Broadcaster              │ │
│                               └─────────────────────────────────┘ │
│                                         │                          │
│                                         │ (DB: SQLite/Postgres)    │
│                                         ▼                          │
│                          ┌──────────────────────────┐             │
│                          │ Prism DB                 │             │
│                          │ - agents, agent_events   │             │
│                          │ - runbooks, metrics      │             │
│                          │ - minersample (tsdb)     │             │
│                          └──────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                               ▲         │         ▲
                               │ Events  │ Commands│
                               │         ▼         │
┌──────────────────────────────┴──────────────────┴─────────────────────┐
│                       ECOSYSTEM SERVICES                               │
│                    (Specialized, External Repos)                       │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ RoadChain       │  │ RoadWallet API  │  │ Lucidia / Lucidia   │  │
│  │ (Ledger)        │  │ (Wallet/PSBT)   │  │ Lab (AI/LLM)        │  │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────────┤  │
│  │ - PoS Consensus │  │ - Wallet Mgmt   │  │ - LLM Inference     │  │
│  │ - Smart Contract│  │ - Tx Signing    │  │ - Model Training    │  │
│  │ - Block Storage │  │ - Balance Track │  │ - Cognitive System  │  │
│  │ - Merkle Roots  │  │ - PSBT Builder  │  │                     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
│                                                                        │
│  ┌─────────────────┐  ┌─────────────────┐                            │
│  │ Quantum Math Lab│  │ PS-SHA-Infinity │                            │
│  │ (Quantum Sim)   │  │ (Identity/Hash) │                            │
│  ├─────────────────┤  ├─────────────────┤                            │
│  │ - Qiskit Jobs   │  │ - Proof Anchor  │                            │
│  │ - Circuit Exec  │  │ - Hash Verif.   │                            │
│  └─────────────────┘  └─────────────────┘                            │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
                               ▲         │
                               │ Telemetry│ Commands
                               │         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      EDGE / AGENT LAYER                                │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ BlackRoad OS    │  │ Agent Swarm     │  │ Pi Cortex Stack     │  │
│  │ Agent (Daemon)  │  │ (100+ Agents)   │  │ (Edge Devices)      │  │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────────┤  │
│  │ - Plugin System │  │ - Cecilia       │  │ - Pi Launcher       │  │
│  │ - Telemetry Pub │  │ - Codex         │  │ - Mac Agent         │  │
│  │ - Command Sub   │  │ - Athena        │  │ - MQTT Bridge       │  │
│  │ - Local Infer.  │  │ - Quantum Coder │  │                     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────┘  │
│                                                                        │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │ Miners (external) → POST /api/miners/sample → Prism Console  │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### Prism Console API (`services/prism-console-api/`)

**Technology:** FastAPI + SQLModel + SQLite/Postgres

**Key Endpoints:**
- `GET /health` – Health check
- `GET /metrics` – Prometheus metrics
- `GET /api/mobile/dashboard` – Dashboard metrics + shortcuts
- `GET /api/agents`, `GET /api/agents/{id}` – Agent catalog
- `GET /api/runbooks`, `POST /api/runbooks/{id}/execute` – Runbook ops
- `POST /api/miners/sample` – Miner telemetry ingestion
- `GET /api/miners/latest` – Latest miner samples
- `GET /api/stream/ops` – SSE stream for real-time events

**Database Models:**
- `Agent` – Agent registry (id, name, domain, status, memory, version)
- `AgentEvent` – Agent event log (id, agent_id, kind, at, message)
- `Runbook` – Runbook catalog (id, title, description, inputs_schema)
- `Metric` – Dashboard metrics (id, title, value, status, icon)
- `MinerSample` – Miner telemetry timeseries (miner_id, hashrate, shares, temperature)
- `Setting` – Key-value config store

**External Dependencies:**
- Auth: Token validation (OIDC or mock mode)
- Runbook Proxy: External workflow engine (Temporal, Argo, etc.)
- SSE Broadcaster: Real-time event pub/sub to web clients

**Observability:**
- Prometheus metrics (`REQUEST_COUNT`, `REQUEST_LATENCY`, `RUNBOOK_EXECUTIONS`, `SSE_CLIENTS`)
- Structured JSON logging
- Health checks

### Prism Console Web (`apps/prism-console-web/`)

**Technology:** Next.js 14 (App Router) + React Query + SSE

**Key Components:**
- `AgentTable` – Agent list with status indicators
- `MinersPanel` – Real-time miner telemetry with sparklines
- `MetricsGrid` – Dashboard metric cards
- `RunbookList` – Runbook catalog with execution UI
- `OverviewContent` – Main dashboard view

**Data Flow:**
- HTTP GET: Dashboard metrics, agents, runbooks from Prism Console API
- SSE: `/api/stream/ops` for real-time miner telemetry
- Offline Mode: Falls back to mocks if API unavailable

**Tech Stack:**
- Next.js 14 (React Server Components + App Router)
- TailwindCSS for styling
- React Query for data fetching
- Vitest + Testing Library for unit tests
- Playwright for E2E tests
- Storybook for component development

---

## Database Architecture

### Two Separate Databases

**IMPORTANT:** Prism uses **separate databases** for different services:

1. **Prism Console API Database** (`prism.db`)
   - Tables auto-created by SQLModel from `services/prism-console-api/src/prism/models.py`
   - Models: `Agent`, `AgentEvent`, `Runbook`, `Metric`, `MinerSample`, `Setting`
   - Used exclusively by Prism Console API

2. **Main BlackRoad API Database** (used by `os/docker/services/blackroad-api/`)
   - Tables defined in `db/migrations/*.sql`
   - Models: `users`, `agents` (different schema), `wallets`, `transactions`, `roadchain_*`, etc.
   - Used by main blackroad-api service and other services

**Why Separate?**
- Prism Console API is an independent microservice with its own data model
- Main API handles user accounts, wallets, and ledger integration
- Separation allows independent deployment and scaling

See [DATABASE.md](./DATABASE.md) for detailed schema documentation.

---

## Event & Telemetry Pipelines

### Miner Telemetry Flow

```
┌─────────┐        ┌────────────────┐        ┌──────────┐        ┌──────────┐
│ Miners  │──POST──▶│ Prism Console │──Write─▶│ SQLite   │──Query─▶│ Web UI   │
│(xmrig)  │        │ API            │        │(tsdb)    │        │(charts)  │
└─────────┘        │  /api/miners/  │        └──────────┘        └──────────┘
                   │  sample        │              │                    ▲
                   └────────────────┘              │                    │
                          │                        │                    │
                          │ Publish                │                    │
                          ▼                        │                    │
                   ┌────────────────┐              │                    │
                   │ SSE Broadcaster│──────────────┴────────SSE─────────┘
                   └────────────────┘
```

**Steps:**
1. Miner → `POST /api/miners/sample` (HTTP)
2. API → Write to `minersample` table (SQLite)
3. API → Publish to SSE broadcaster (`/api/stream/ops`)
4. Web UI → Subscribe to SSE → Render sparklines

**Data Format:**
```json
{
  "type": "miner.sample",
  "miner_id": "xmrig-001",
  "sample": {
    "hashrate_1m": 50000.0,
    "shares_accepted": 1234,
    "stale_rate": 0.02,
    "temperature_c": 72.5
  }
}
```

---

## Deployment

### Local Development

```bash
# 1. Install dependencies
npm install
cd services/prism-console-api && poetry install

# 2. Start Prism Console API
cd services/prism-console-api
poetry run uvicorn prism.main:app --reload --port 4000

# 3. Start Prism Console Web (separate terminal)
cd apps/prism-console-web
pnpm install
pnpm dev

# 4. Visit http://localhost:3000
```

### Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check health
curl http://localhost:4000/health
curl http://localhost:3000
```

---

## Security

### Auth & AuthZ

- **Authentication:** OIDC token validation (configurable provider)
- **Mock Mode:** For local dev without external auth (set `PRISM_API_MOCK_MODE=true`)
- **API Tokens:** JWT bearer tokens required for all non-health endpoints
- **Token Caching:** In-memory cache to reduce auth provider load

### Security Headers

Middleware stack includes:
- CORS (configurable origins)
- Request ID tracing
- Rate limiting
- Security headers (CSP, X-Frame-Options, etc.)

---

## Known Limitations

### Tier 1 (Critical)

1. **RoadChain Service is Prototype**
   - Ephemeral in-memory state (no persistence)
   - Doesn't write to `roadchain_*` tables in DB
   - **Fix:** Deprecate and integrate with external RoadChain node

2. **Agent Event Ingestion Missing**
   - No endpoint for agents to publish events to Prism
   - **Fix:** Implement `POST /api/agents/{id}/events`

3. **Lucidia Service Fragmentation**
   - Logic spread across 10+ directories
   - **Fix:** Consolidate into single `services/lucidia_api/`

4. **AutoPal Duplication**
   - 4 implementations across codebase
   - **Fix:** Pick canonical impl, deprecate others

---

## References

- [Main README](../README.md)
- [Database Schema Documentation](./DATABASE.md)
- [Getting Started Guide](./GETTING_STARTED.md)
- [Deployment Guide](../DEPLOYMENT.md)
- [Security Policy](../SECURITY.md)

---

**Last Updated:** 2025-11-15
**Maintainer:** Cecilia (Cece) - Systems Architect
