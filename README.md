# BlackRoad Prism Console

A Python 3.11+ bot orchestration framework for enterprise operations.

## Architecture
[console] → [orchestrator] → [bots]
                ↓
         memory.jsonl

## Quick Start
```bash
# Install
pip install -r requirements.txt

# List available bots
python -m cli.console bot:list

# Create and route a task
python -m cli.console task:create --goal "Build Q3 cash forecast"
python -m cli.console task:route --id <TASK_ID> --bot "Treasury-BOT"

# View task history
cat memory.jsonl | jq
```

## Core Concepts

- **Bots**: Autonomous agents with missions, KPIs, guardrails
- **Tasks**: Work units routed to appropriate bots
- **Orchestrator**: Routes tasks, enforces policy, logs everything
- **Memory**: Append-only audit trail in JSONL format

## Modules

See [docs/MODULES.md](docs/MODULES.md) for an overview of every operational module.

## Creating Custom Bots

See [docs/BOT_DEVELOPMENT.md](docs/BOT_DEVELOPMENT.md) for guidance on extending the platform.

## Configuration

Configuration formats and examples live in [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Security

The complete security model is documented in [docs/SECURITY.md](docs/SECURITY.md).

## Development

Developer workflow, testing, and contribution expectations are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Project Status

⚠️ **Alpha Stage**: This project is under active development. The core orchestration 
framework is functional, but APIs may change. Tool adapters are currently stubbed and 
make no external calls for safety during development.

We welcome feedback and contributions! See CONTRIBUTING.md for guidelines.
