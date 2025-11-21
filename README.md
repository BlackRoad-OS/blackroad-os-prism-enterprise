# BlackRoad Prism Console

A production-grade multi-agent AI platform featuring quantum computing capabilities, sacred geometry-based agent coordination, distributed intelligence orchestration, and comprehensive visualization tools.

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
