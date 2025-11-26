# BlackRoad Prism Console
![Build](https://github.com/blackboxprogramming/blackroad-prism-console/actions/workflows/monorepo-matrix.yml/badge.svg) ![E2E](https://github.com/blackboxprogramming/blackroad-prism-console/actions/workflows/playwright.yml/badge.svg) ![Deploy](https://github.com/blackboxprogramming/blackroad-prism-console/actions/workflows/deploy-blackroad.yml/badge.svg)
# BlackRoad.io — Dependency & Ops Bundle
[![CI](https://github.com/<org>/prism/actions/workflows/ci.yml/badge.svg)](https://github.com/<org>/prism/actions/workflows/ci.yml)
# Blackroad Prism Console

A minimal multi-bot orchestration console demonstrating task routing and guardrails.

Requires Node.js 20 or later. If you're bootstrapping a Red Hat Enterprise Linux
(or CentOS Stream) host, follow the step-by-step guide in
[`docs/rhel-node-web-console.md`](docs/rhel-node-web-console.md) to enable the
Cockpit web console and install Node.js 20 with `dnf`.

This bundle is a **drop-in helper** to resolve “missing dependencies etc.” without requiring
connector access. Push it into your working copy, then run one script on the server to scan
your API, install missing npm packages, set up env defaults, and (optionally) boot a local
LLM stub on port **8000** if none is running.

> **Heads-up from the maintainer:** I'm still getting everything set up and I'm honestly not a
> strong coder yet. Thank you for your patience if anything here is rough around the edges —
> I'm doing my best and truly sorry for any bumps along the way.
## Note on GitHub Copilot agent UI

The Codespaces chat quick-actions are provided by GitHub Copilot's agent features and are
controlled by the Copilot service (not repo files). See `COPILOT_SETUP.md` and
`.github/copilot-instructions.md` for guidance to enable and tune Copilot agent behavior.

**What’s included**

- `ops/install.sh` — one-shot setup for `/srv/blackroad-api` (or detected API path)
- `tools/dep-scan.js` — scans JS/TS for `require()`/`import` usage and installs missing packages
- `tools/verify-runtime.sh` — quick health checks (API on 4000, LLM on 8000)
- `srv/blackroad-api/.env.example` — sample env for your Express API
- `srv/blackroad-api/package.json.sample` — a safe starter if your API has no package.json
- `srv/lucidia-llm/` — minimal FastAPI echo stub (only used if you don’t already run an LLM on 8000)
- `srv/lucia-llm/` — same stub (duplicate dir name for compatibility with earlier scripts)

Date: 2025-08-22

This bundle is a **drop-in helper** to resolve “missing dependencies etc.” without requiring
connector access. Push it into your working copy, then run one script on the server to scan
your API, install missing npm packages, set up env defaults, and (optionally) boot a local
LLM stub on port **8000** if none is running.

**What’s included**

- `ops/install.sh` — one-shot setup for `/srv/blackroad-api` (or detected API path)
- `tools/dep-scan.js` — scans JS/TS for `require()`/`import` usage and installs missing packages
- `tools/verify-runtime.sh` — quick health checks (API on 4000, LLM on 8000)
- `srv/blackroad-api/.env.example` — sample env for your Express API
- `srv/blackroad-api/package.json.sample` — a safe starter if your API has no package.json
- `srv/lucidia-llm/` — minimal FastAPI echo stub (only used if you don’t already run an LLM on 8000)
- `srv/lucia-llm/` — same stub (duplicate dir name for compatibility with earlier scripts)

> Nothing here overwrites your existing code. The scripts are defensive: they detect paths,
> **merge** deps, and only generate files if missing.

---

## Quick start

**On your workstation**

1. Unzip this at the **root of your working copy** (where your repo root lives).
2. Commit and push.
uring quantum computing capabilities, sacred geometry-based agent coordination, distributed intelligence orchestration, and comprehensive visualization tools.

## Overview

The BlackRoad Prism Console is a comprehensive ecosystem combining:
- **100 Production-Ready AI Agents** with specialized capabilities
- **Quantum Computing Lab** with simulators and hardware integration
- **Agent Gateway API** for orchestrating distributed agent swarms
- **Cecilia Memory System** for persistent context across interactions
- **Multi-Agent Orchestration**: 1000+ agent swarm with sacred formation patterns (DELTA, HALO, LATTICE, HUM, CAMPFIRE)
- **Distributed Intelligence**: Polyglot microservices architecture with 36+ services
- **Sacred Geometry**: Mathematical foundations for agent coordination and coherence
- **Real-time Collaboration**: Multi-protocol message bus (QLM, MQTT, Redis, REST)
- **57+ Infrastructure Packages** for gateways, engines, and SDKs
- **Multiple Web Applications** including Prism Console, agent catalog, and BlackRoad sites

## Quick Start

```bash
# Setup environment
npm install
make setup
cd /path/to/your/working/copy
sudo bash ops/install.sh
bash tools/verify-runtime.sh
```

- The installer will:
  - Locate your API (prefers `./srv/blackroad-api`, then `/srv/blackroad-api`, else searches for `server_full.js`)
  - Create `package.json` if missing and **auto-install** any missing npm packages it finds
  - Create `.env` from the example if missing and generate strong secrets
  - Ensure your SQLite file exists (defaults to `blackroad.db` inside the API dir if `DB_PATH` is not set)
  - Check if `127.0.0.1:8000` is serving `/health`. If not, it prints a one-liner to launch the stub.

## Git workflow

When you're ready to share changes:

1. Stage your updates:
   ```bash
   git add -A
   ```
2. Commit with a clear message:
   ```bash
   git commit -m "feat: describe your change"
   ```

## Executive Autopilot

Offline analytics helpers:

```bash
python -m cli.console cohort:new --name apac_flagship --criteria samples/cohorts/apac_flagship.json
python -m cli.console anomaly:run --rules configs/anomaly_rules.yaml --window W
python -m cli.console decide:plan --anomalies artifacts/anomalies/latest.json --goals configs/goals.yaml --constraints configs/constraints.yaml
python -m cli.console narrative:build --plan artifacts/decisions/plan_*.json --out artifacts/reports/exec_latest
```
3. Push the branch:
   ```bash
   git push origin <branch-name>
   ```
4. Open a Pull Request and review the CI results.

## Developing with VS Code and Docker on macOS

1. Start [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac/).
2. Install [Visual Studio Code](https://code.visualstudio.com/) and the **Dev Containers** extension.
3. Open this repository in VS Code and select **Reopen in Container** to use `.devcontainer/devcontainer.json`.
4. Once the container is running, use the integrated terminal to run commands like `npm install`, `npm run lint`, or `npm test`.

---

## Notes & assumptions

- Stack recorded in memory (Aug 2025): SPA on `/var/www/blackroad/index.html`, Express API on port **4000**
  at `/srv/blackroad-api` with SQLite; LLM service on **127.0.0.1:8000**; NGINX proxies `/api` and `/ws`.
- This bundle does **not** ship `node_modules/` (native builds vary by machine). Instead, it generates
  and installs what’s actually needed by **scanning your sources**.
- If your API already has `package.json`, nothing is overwritten; missing deps are added.
- If you maintain your API directly under a different path, run the scanner manually, e.g.:
  ```bash
  node tools/dep-scan.js --dir /path/to/api --save
  ```

If anything looks off, run `bash tools/verify-runtime.sh` and share the output.

## Subscribe API

# Start Prism Console web interface
npm run dev

# Run quantum computing demos
make demo

# Launch agent via Prism Shell
./prism/prismsh.js spawn cecilia
```

## Deployment & Environments

The Prism Console web service for BlackRoad OS is deployed to Railway under the project **`blackroad-prism-console`** as the **`prism-console-web`** service.

- **Environments & URLs**
  - **dev:** Railway preview URL for the dev environment
  - **staging:** https://staging.console.blackroad.systems
  - **prod:** https://console.blackroad.systems
- **Build command:** `npm run build` (executed in `frontend`)
- **Start command:** `npm run start` (serves the Vite build and `/health` / `/version` routes)
- **Required environment variables:**
  - `CORE_API_URL`, `AGENTS_API_URL`, `PUBLIC_CONSOLE_URL`
  - `NEXT_PUBLIC_CORE_API_URL`, `NEXT_PUBLIC_AGENTS_API_URL`, `NEXT_PUBLIC_CONSOLE_URL`

## GitHub Automation Manual

For a visual, emoji-driven overview of how humans 🧍 and agents 🤖 should work inside this repo—including branching rules, PR flow, CI expectations, and onboarding steps—see [`docs/github_automation_manual_emoji.md`](docs/github_automation_manual_emoji.md).

## Architecture

### Core Components

#### Prism Console (`apps/prism-console-web`)
Next.js 14 web application for managing agents, viewing metrics, and orchestrating tasks.

#### Agent Swarm System (`agents/`)

The platform features a sophisticated agent swarm with:

- **100+ Production-Ready Agents**: Specialized capabilities for different domains
- **Language Abilities Registry**: Maps agents to linguistic capabilities
- **Swarm Orchestrator**: Intelligent task routing and coordination
- **Formation Patterns**: Sacred geometric coordination patterns (DELTA, HALO, LATTICE, HUM, CAMPFIRE)
- **Unified Message Bus**: Multi-protocol communication layer

**Key Agents:**
- **Cecilia** (`CECILIA-7C3E-SPECTRUM-9B4F`): Creative systems architect and infrastructure engineer
- **Quantum Coder**: Quantum algorithm development and optimization
- **Security Guardian**: Security auditing and vulnerability scanning
- **Deployment Orchestrator**: CI/CD and infrastructure deployment

**Agent Archetypes (20 Clusters):**
- **athenaeum** (knowledge management)
- **aurum** (economic systems)
- **blackroad** (platform core)
- **continuum** (operations)
- **eidos** (strategy)
- **mycelia** (ecological systems)
- **parallax** (storytelling)
- **soma** (wellness)
- **lucidia** (core intelligence)
- And 11 more specialized clusters

#### Gateway Packages (`packages/`)
- `@blackroad/hjb-gateway`: Hamilton-Jacobi-Bellman optimization gateway
- `@blackroad/media-gateway`: Media processing and streaming
- `@blackroad/diffusion-gateway`: Stable Diffusion and image generation
- `@blackroad/obs-gateway`: GraphQL subscriptions and observability
- `@blackroad/correlation-engine`: Event correlation and pattern detection
- `@blackroad/graph-engines`: Graph processing and analysis

## Quantum Computing Features

### Capabilities
- **Simulators**: NumPy statevector simulation + Qiskit hardware wrappers
- **Algorithms**: Bell states, Grover search, QFT, phase estimation
- **Visualization**: Circuit diagrams, Bloch spheres, measurement histograms
- **Hardware Integration**: IBM Quantum via `QISKIT_API_TOKEN`
- **Pedagogical Notebooks**: Learning path for quantum computing
- **CHSH Inequality Demonstrations**: Bell state analysis

### Learning Path (Quantum Pedagogy)
1. `notebooks/01_qubit_basics.ipynb` — Single qubits and Bloch sphere
2. `notebooks/02_entanglement_bell.ipynb` — Bell states and CHSH violations
3. `notebooks/03_qft_and_phase.ipynb` — Quantum Fourier transforms
4. `notebooks/04_grover_vs_random.ipynb` — Grover's search algorithm
5. `notebooks/05_noise_and_mitigation.ipynb` — Error handling and mitigation
6. `notebooks/06_qiskit_hardware_roundtrip.ipynb` — IBM Quantum integration

## Agent Development

### Spawning Agents
```bash
# Via Prism Shell
./prism/prismsh.js spawn <agent-name>

# Via Agent Gateway API
curl -X POST http://localhost:3001/v1/agents/cecilia/tasks \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze system architecture"}'
```

### Agent Manifests
Each agent has a manifest at `agents/<agent-name>/manifest.json`:

```json
{
  "name": "cecilia",
  "version": "1.0.0",
  "agent_id": "CECILIA-7C3E-SPECTRUM-9B4F",
  "description": "Creative spectrum engineer",
  "capabilities": [
    "code_architecture",
    "system_design",
    "ui_creation",
    "problem_solving"
  ]
}
```

## Development

### Project Structure
```
blackroad-prism-console/
├── agents/                 # 100 agent manifests and implementations
├── apps/                   # Web applications
│   ├── prism-console-web/  # Main console (Next.js 14)
│   ├── prismweb/           # Alternative console interface
│   └── ...                 # Additional web apps
├── packages/               # 57+ infrastructure packages
│   ├── hjb-gateway/
│   ├── media-gateway/
│   ├── correlation-engine/
│   └── ...
├── prism/                  # Prism Shell CLI
├── notebooks/              # Quantum computing tutorials
└── artifacts/              # Generated outputs
```

### Building
```bash
# Build all packages
npm run build

# Run tests
npm test

# Type checking
tsc --noEmit
```

## Deployment

### Docker
```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Variables
```bash
# Quantum hardware access
QISKIT_API_TOKEN=your_token_here

# Agent Gateway
AGENT_GATEWAY_PORT=3001

# Cecilia Memory API
CECILIA_MEMORY_PORT=3000
```

**Running Quantum Demos:**

```bash
make demo
```

This produces artifacts in `artifacts/`:
- `bell_hist.png` — Bell state measurement distributions
- `bloch_example.png` / `bloch_q0.png` — Bloch sphere visualizations
- `grover_success.png` / `grover_curve.png` — Grover algorithm success rates
- `lineage.jsonl` — Agent interaction logs

**Hardware Access:**

Set the `QISKIT_API_TOKEN` environment variable to access IBM Quantum hardware. Without a token, the system defaults to Aer simulators and fake backends.

For detailed quantum lab documentation, see [README-quantum-lab.md](./README-quantum-lab.md).

### Microservices (36+)

**Core Services:**
- api, api-gateway, auth
- prism-console-api, prism

**LLM & AI:**
- llm-gateway, llm-healthwatch
- lucidia-cognitive-system, lucidia-api

**Quantum & Scientific:**
- quantum_copilot, quantum_lab
- origin-qlm-bridge

**Infrastructure:**
- health-sidecar, error-logger
- model-health, mock-issuer

## Development

### Prerequisites

- Node.js >= 20
- Python >= 3.10
- Docker (for containerized services)

### Setup

```bash
# Install dependencies
make install
npm install

# Run tests
make test
npm test

# Format code
make format

# Lint
make lint

# Type checking
tsc --noEmit
```

### Project Structure

```
blackroad-prism-console/
├── agents/           # 100+ production-ready agents
├── frontend/         # React + Vite SPA
├── services/         # 36+ microservices
├── apps/             # Multiple web applications
│   ├── prism-console-web/
│   ├── prismweb/
│   └── ...
├── packages/         # 57+ infrastructure packages
│   ├── hjb-gateway/
│   ├── media-gateway/
│   └── ...
├── prism/            # Prism Shell CLI
├── notebooks/        # Quantum computing tutorials
├── infra/            # Terraform, Kubernetes configs
├── artifacts/        # Generated outputs
├── tools/            # Utilities and tooling
└── docs/             # Comprehensive documentation
```

## Deployment

Multiple deployment options supported:

- **Docker Compose**: `docker-compose -f docker-compose.prod.yml up`
- **Fly.io**: `make deploy-fly`
- **AWS ECS**: `make deploy-ecs`
- **Kubernetes**: `kubectl apply -f infra/k8s/`

See [README-DEPLOY.md](./README-DEPLOY.md) for detailed deployment instructions.

## Sacred Geometry & Mathematics

The platform includes sophisticated mathematical tools:

- Magic square generation toolkit
- Amundson ring coherence simulation
- Projective depth solver
- Cross-ratio calculations
- Spectral gap analysis
- Angle defect computations

## Bot Family Demo

The repository includes an in-memory message bus with cooperating bots demonstrating planning, execution, and artifact logging:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python orchestrator/run_demo.py
```

This generates a Bell pair histogram at `artifacts/bell_hist.png` with lineage logging in `lineage.jsonl`.

## Security & Policy

The platform enforces policy-as-code constraints:

- Network access disabled by default in quantum environments
- Artifact size budgets enforced
- All tool calls logged through lineage subsystem
- mTLS between services (production)
- Non-root container execution
- Secret rotation policies (see SECURITY.md)

## Monitoring & Observability

- **Metrics**: Prometheus + Grafana
- **Logging**: Structured JSON logging
- **Tracing**: Distributed tracing support
- **Health Checks**: `/healthz`, `/health.json`, `/api/version`

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for development workflow, commit message style, and code review checklist.

## Documentation

Comprehensive documentation available in `docs/`:

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment guide
- [RUNBOOK.md](./RUNBOOK.md) - Operations runbook
- [SECURITY.md](./SECURITY.md) - Security practices
- [AGENT_WORKBOARD.md](./AGENT_WORKBOARD.md) - Agent development
- [README-OPS.md](./README-OPS.md) - Operations guide
- [BLACKROAD_CORPORATE_ORG_V1.md](./docs/BLACKROAD_CORPORATE_ORG_V1.md) - Full corporate org structure

## License

See [LICENSE](./LICENSE) for details.

## Unsolved Problems

See `quantum_lab/pedagogy/unsolved/` for mini-essays connecting demos to enduring mathematical challenges.

## Support

- **Documentation**: `docs/`
- **Issues**: GitHub Issues
- **Security**: See `SECURITY.md`

---

**Version**: 1.0.0
**Last Updated**: 2025-11-10
**Status**: Pre-production (hardening in progress)
    def run(self, task: Task) -> BotResponse:
        ...
```

## Compliance Readiness

Example commands:

```bash
python -m cli.console esign:keygen --user U_PM
python -m cli.console sop:new --name release --from sop/templates/release.yaml
python -m cli.console hitl:enqueue --task T100 --type security --artifact artifacts/T100/response.json --reviewers U_SEC,U_CTO
python -m cli.console records:status
python -m cli.console tui:run --theme high_contrast --lang es
```

## Flags

```
python -m cli.console flags:list
python -m cli.console flags:set --name bot.SRE-BOT.postmortem_v2 --value true
```

## Migrations
## ⚙️ COMMAND-LINE SHORTCUTS

Run `rohonc_toolkit_cli.py` to access the most common workflows without writing Python code:

```bash
# Apply a Caesar shift (use --decrypt to reverse the direction)
python rohonc_toolkit_cli.py caesar "Af lzw twyaffafy" --alphabet 26 --decrypt

# Peek at the Bible number stream
python rohonc_toolkit_cli.py numbers --limit 15 --offset 100

# Decode a numeric Rohonc sequence
python rohonc_toolkit_cli.py decode-numbers --sequence "100, 200, 300, 400"

# Inspect high-frequency Bible words to map symbols
python rohonc_toolkit_cli.py frequencies --limit 20 --min-length 3

# Regenerate JSON artifacts (quietly skip progress logs)
python rohonc_toolkit_cli.py export --master-guide --quiet
```

Each sub-command prints focused output and reuses cached Bible data, so repeated calls stay fast.

---

## 🔢 EXAMPLE TRANSFORMATIONS

```
python -m cli.console migrate:status
python -m cli.console migrate:up
```

## Tenancy

```
python -m cli.console --tenant ACME task:create --goal "Tenant task"
```

## Quotas

```
python -m cli.console quota:show --as-user U_PM
```
See [docs/blackroad-equation-backbone.md](docs/blackroad-equation-backbone.md) for a curated list of one hundred foundational equations across mathematics, physics, computer science, and engineering.

_Last updated on 2025-09-11_

## Master Data & Governance Quickstart

```bash
python -m cli.console mdm:stage --domain account --file fixtures/mdm/account.csv
python -m cli.console mdm:match --domain account --config configs/mdm/match_account.yaml
python -m cli.console mdm:golden --domain account --policy configs/mdm/survivorship_account.yaml
python -m cli.console mdm:dq --domain account --config configs/mdm/dq_account.yaml
## Prism Developer Mode

Start the development server:

```bash
cd prism/server
npm install
npm run dev
```

Run the web console with Approvals panel:

```bash
cd apps/prismweb
npm install
npm run dev
```

## Console Quickstart

```bash
pip install -r requirements.txt
python -m cli.console bot:list
python -m cli.console task:create --goal "Build 13-week cash view"
python -m cli.console task:route --id <ID> --bot "Treasury-BOT"
```

## Add a new bot

Create `bots/my_bot.py`:

```python
from orchestrator.base import BaseBot
from orchestrator.protocols import Task, BotResponse

class MyBot(BaseBot):
    """
    MISSION: ...
    INPUTS: ...
    OUTPUTS: ...
    KPIS: ...
    GUARDRAILS: ...
    HANDOFFS: ...
    """
    name = "My-BOT"
    mission = "..."

    def run(self, task: Task) -> BotResponse:
        ...
```
## Policy Packs
Default governance policies can be applied via the CLI.

## Encryption at Rest
Data under the data/ directory can be encrypted with AES-GCM.

## Docs Site
Documentation can be generated with `python -m cli.console docs:generate`.
## Prism Console Bots

### Plugin How-To
Drop a new `*_bot.py` under `/plugins/` exposing `NAME`, `MISSION`, `SUPPORTED_TASKS`, and a `BaseBot` implementation. Call `register()` from `orchestrator.registry` and it will be auto-discovered.

### Metrics & Logging
- Metrics written to `orchestrator/metrics.jsonl`
- Structured logs written to `orchestrator/memory.jsonl`

### Example Commands
```bash
python -m cli.console bot:list
python -m cli.console bot:run --bot "RevOps-BOT" --goal "Check forecast accuracy for Q3"
python -m cli.console bot:run --bot "SRE-BOT" --goal "Compute error-budget burn for Service A"
```

## Data Layer Quickstart

Build and query the offline lake:

```
python -m cli.console index:build
python -m cli.console sem:metrics
```

## Training & Enablement Hub Quickstart

```bash
python -m cli.console learn:courses:load --dir configs/enablement/courses
python -m cli.console learn:courses:list --role_track "Solutions Engineer"
```

## Integration Security Playbook

For guidance on connecting Slack, Asana, GitLab, GitHub, Discord, Airtable, and other
automation bots to the BlackRoad Prism Console, review
[`INTEGRATIONS_SECURITY.md`](./INTEGRATIONS_SECURITY.md). The playbook documents
hardening steps for key management, OAuth scopes, monitoring, and incident response so
that integrations remain auditable and compliant.
## Running Tests

Install dependencies and execute the Jest suite:

```bash
npm install
npm test
## Quickstart

```bash
python -m cli.console bot:list
python -m cli.console task:create "Review cash" finance
# copy the returned task id
python -m cli.console task:route <TASK_ID>
```

## Architecture

```
+-----------+        +--------------+        +------------+
|   CLI     | -----> | Orchestrator | -----> |   Bots     |
+-----------+        +--------------+        +------------+
                               |
                        memory.jsonl
```

## Security Model

- No network or database calls.
- All actions appended to `memory.jsonl`.
- Tasks checked for privacy/security metadata.
- Bots contain guardrail docstrings and red-team awareness.

## Bot Template

```python
class ExampleBot:
    """ExampleBot

    MISSION: Example mission.
    INPUTS: Expected inputs.
    OUTPUTS: Expected outputs.
    KPIS: Key performance indicators.
    GUARDRAILS: Safety constraints.
    HANDOFFS: Downstream bots.
    """

    def run(self, task: Task) -> Response:
        ...
```

## Example Run

```bash
$ python -m cli.console task:create "Review treasury position" finance
123e4567-e89b-12d3-a456-426614174000
$ python -m cli.console task:route 123e4567-e89b-12d3-a456-426614174000
success
```

## Infrastructure

Terraform examples live in `infra/terraform`. Configure a remote backend (e.g. S3 state bucket) inside `terraform {}` before running `terraform init`.

## Running Tests in Docker

This repository includes Docker support for running tests in an isolated environment.

### Quick Start

Validate your Docker test environment:

```bash
./scripts/validate-docker-test.sh
```

Run all tests (Jest + pytest):

```bash
docker compose run --rm tests
```

Run specific test suites:

```bash
# JavaScript tests only
docker compose run --rm test-node

# Python tests only
docker compose run --rm test-python
```

For detailed documentation, see [DOCKER_TESTS.md](DOCKER_TESTS.md).

