# QLM Lab (Prism)
Quantum-aware language agents (QLMs) collaborating with classical LLM bots to solve math/physics/code tasks with verifiable artifacts.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[qiskit]
make demo  # saves artifacts/ and lineage.jsonl
```

## Safety & Policy
- No external network by default.
- Artifacts capped by policy; see prism/policies/gates/qlm_lab.rego.
- Deterministic seeds via the `QLAB_SEED` environment variable.

## Structure
- `qlm_lab/tools`: numerical, symbolic, visualization, and filesystem helpers.
- `qlm_lab/agents`: rule-based prototype agents for orchestration and critique.
- `qlm_lab/demos`: runnable experiments that produce artifacts and metrics.
- `qlm_lab/notebooks`: reproducible notebooks mirroring the demos.
- `tests`: pytest suite covering tools, policies, and agent coordination.

## Development
Run tests and lint checks before committing:
```bash
make test
make lint
```

Use `make notebooks` to execute and store evaluated notebooks with outputs saved next to the originals.
