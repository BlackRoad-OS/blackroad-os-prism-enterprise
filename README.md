# BlackRoad Prism Console

A production-grade quantum computing and AI agent orchestration platform featuring quantum simulators, agent swarm coordination, memory systems, and comprehensive visualization tools.

## Overview

BlackRoad Prism Console is a monorepo workspace combining:
- **100 Production-Ready AI Agents** with specialized capabilities
- **Quantum Computing Lab** with simulators and hardware integration
- **Agent Gateway API** for orchestrating distributed agent swarms
- **Cecilia Memory System** for persistent context across interactions
- **57+ Infrastructure Packages** for gateways, engines, and SDKs
- **Multiple Web Applications** including Prism Console, agent catalog, and BlackRoad sites

## Quick Start

```bash
# Setup environment
npm install

# Start Prism Console web interface
npm run dev

# Run quantum computing demos
make setup
make demo

# Launch agent via Prism Shell
./prism/prismsh.js spawn cecilia
```

## Architecture

### Core Components

#### Prism Console (`apps/prism-console-web`)
Next.js 14 web application for managing agents, viewing metrics, and orchestrating tasks.

#### Agent Swarm (`agents/`)
100 specialized agents including:
- **Cecilia** (`CECILIA-7C3E-SPECTRUM-9B4F`): Creative systems architect and infrastructure engineer
- **Quantum Coder**: Quantum algorithm development and optimization
- **Security Guardian**: Security auditing and vulnerability scanning
- **Deployment Orchestrator**: CI/CD and infrastructure deployment
- And 96 more production-ready agents...

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

### Learning Path
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

## Artifacts

Running demos generates:
- `artifacts/bell_hist.png` — Bell state measurement distributions
- `artifacts/bloch_q0.png` — Bloch sphere visualizations
- `artifacts/grover_curve.png` — Grover algorithm success rates
- `artifacts/lineage.jsonl` — Agent interaction logs

## Contributing

See `CONTRIBUTING.md` for development guidelines.

## License

See `LICENSE` for details.

## Support

- Documentation: `docs/`
- Issues: GitHub Issues
- Security: See `SECURITY.md`
