# BlackRoad Prism Console

A production-grade multi-agent AI platform featuring quantum computing capabilities, sacred geometry-based agent coordination, and distributed intelligence orchestration.

## Overview

The BlackRoad Prism Console is a comprehensive ecosystem for:

- **Multi-Agent Orchestration**: 1000+ agent swarm with sacred formation patterns (DELTA, HALO, LATTICE, HUM, CAMPFIRE)
- **Quantum Computing**: Production quantum lab with NumPy simulator, Qiskit hardware wrappers, and pedagogical notebooks
- **Distributed Intelligence**: Polyglot microservices architecture with 36+ services
- **Sacred Geometry**: Mathematical foundations for agent coordination and coherence
- **Real-time Collaboration**: Multi-protocol message bus (QLM, MQTT, Redis, REST)

## Quickstart

```bash
# Install dependencies
make setup

# Run development server
npm run dev

# Run quantum demo
make demo
```

## Architecture

### Agent Swarm System

The platform features a sophisticated agent swarm with:

- **Language Abilities Registry**: Maps agents to linguistic capabilities
- **Swarm Orchestrator**: Intelligent task routing and coordination
- **Formation Patterns**: Sacred geometric coordination patterns
- **Unified Message Bus**: Multi-protocol communication layer

### Agent Archetypes (20 Clusters)

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

### Quantum Lab

A production-grade quantum computing teaching lab featuring:

- Local NumPy-based quantum simulator
- Qiskit hardware integration (IBM Quantum)
- Circuit visualization and analysis tools
- Pedagogical notebooks for learning quantum computing
- CHSH inequality demonstrations and Bell state analysis

**Quantum Feature Matrix:**

| Capability | Local Simulator | Qiskit Backends |
| --- | --- | --- |
| Statevector simulation | ✅ | ✅ |
| Noise channels | ✅ | ✅ (through backend models) |
| Circuit visualization | ✅ | ✅ |
| Hardware execution | ❌ | ✅ (token required) |

**Running Quantum Demos:**

```bash
make demo
```

This produces artifacts in `artifacts/`:
- `bell_hist.png` - Bell state histogram
- `bloch_example.png` - Bloch sphere visualization
- `grover_success.png` - Grover algorithm success curve

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

# Run tests
make test

# Format code
make format

# Lint
make lint
```

### Project Structure

```
blackroad-prism-console/
├── agents/           # 1000+ agent system
├── frontend/         # React + Vite SPA
├── services/         # 36+ microservices
├── apps/             # Multiple applications
├── infra/            # Terraform, Kubernetes configs
├── packages/         # 57 shared packages
├── tools/            # Utilities and tooling
└── docs/             # Comprehensive documentation
```

## Deployment

Multiple deployment options supported:

- **Fly.io**: `make deploy-fly`
- **AWS ECS**: `make deploy-ecs`
- **Kubernetes**: `kubectl apply -f infra/k8s/`
- **Docker Compose**: `docker-compose -f docker-compose.prod.yml up`

See [README-DEPLOY.md](./README-DEPLOY.md) for detailed deployment instructions.

## Sacred Geometry & Mathematics

The platform includes sophisticated mathematical tools:

- Magic square generation toolkit
- Amundson ring coherence simulation
- Projective depth solver
- Cross-ratio calculations
- Spectral gap analysis
- Angle defect computations

## Pedagogy Path (Quantum Learning)

1. `notebooks/01_qubit_basics.ipynb` — Single qubits and Bloch sphere
2. `notebooks/02_entanglement_bell.ipynb` — Bell states and CHSH violations
3. `notebooks/03_qft_and_phase.ipynb` — Fourier transforms and phase estimation
4. `notebooks/04_grover_vs_random.ipynb` — Search speed-ups
5. `notebooks/05_noise_and_mitigation.ipynb` — Ideal vs noisy evolutions
6. `notebooks/06_qiskit_hardware_roundtrip.ipynb` — Simulator to hardware handoff

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

## License

See [LICENSE](./LICENSE) for details.

## Unsolved Problems

See `quantum_lab/pedagogy/unsolved/` for mini-essays connecting demos to enduring mathematical challenges.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-09
**Status**: Pre-production (hardening in progress)
