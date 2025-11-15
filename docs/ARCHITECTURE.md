# Architecture

BlackRoad Prism Console orchestrates enterprise bots through a layered control plane.

```
┌─────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Console │ ─▶ │ Orchestrator    │ ─▶ │ Bots            │
└─────────┘     └─────────────────┘     └─────────────────┘
                      │                         │
                      ▼                         ▼
               Policy Enforcement        Operational Systems
                      │
                      ▼
               memory.jsonl (audit log)
```

## Components

### Console
Interactive CLI used by operators to list bots, create tasks, route work, and inspect
history. Implemented with [Typer](https://typer.tiangolo.com/) for consistent UX.

### Orchestrator
Responsible for:

- Validating tasks and matching them to registered bots
- Enforcing approval policies and guardrails
- Persisting append-only memory records with cryptographic signatures
- Tracking data lineage across bot handoffs
- Triggering redaction for PII before storage

### Bots
Bots inherit from `orchestrator.base.BaseBot`. Each bot exposes mission metadata,
required inputs, produced outputs, KPIs, guardrails, and expected handoffs. Bots return
structured `BotResponse` objects and never interact with external systems directly in
this repository.

### Memory & Audit Trail
`memory.jsonl` stores every orchestrated event as structured JSON. Each entry contains
hash-linked signatures. The append-only log enables offline verification of the audit
trail.

### Data Flow

1. Operator creates a task through the console.
2. Task is validated via Pydantic models and stored in the task registry.
3. Operator routes the task to a bot.
4. Orchestrator enforces policy, executes the bot, and logs the result to memory.
5. Redaction rules remove or tokenise PII before persistence.
6. Lineage metadata links tasks, bots, and outputs for downstream traceability.

## Deployment Topology

The console is a Python application that can be executed locally or packaged into a
container. Integration with the optional Prism web UI happens through the same
orchestrator APIs. Deployment guidance is documented in [docs/DEPLOYMENT.md](DEPLOYMENT.md).

## Mathematical Assurance Topology

For a system-level view of how linear algebra, graph theory, logic, cryptography, and
other mathematical disciplines support the architecture, see the
[Math Topology Map](math_topology_map.md). Use it during design reviews to confirm that
new features inherit the correct assurance model and to guide audit conversations about
the controls embedded in each subsystem.

## Extensibility

- **Bots**: Implement additional bots by extending the base class.
- **Policies**: Custom policies can be added by subclassing `BasePolicy`.
- **Connectors**: External system adapters should live in dedicated repositories and be
  called via well-defined interfaces.

## Future Enhancements

- Distributed queue support for high-volume task routing
- Signed bot packages for supply chain attestation
- Rich lineage visualisation via the Prism UI
