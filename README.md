# QLM Lab

QLM Lab is a lightweight environment for experimenting with quantum-aware
language model agents. A Quantum Language Model (QLM) combines deterministic
rule-based reasoning with structured access to quantum simulation tools to
produce verifiable artefacts such as plots, metrics, and tests.

## Quickstart

```bash
make setup
make demo
```

The demo command executes four agent-driven scenarios covering Bell inequality
violation, Grover search, phase estimation, and code generation with automated
tests. Generated plots are stored under `artifacts/` and lineage is appended to
`artifacts/lineage.jsonl`.

## Safety and Policy

The lab enforces policy-as-code constraints via `qlm_lab.policies.PolicyGuard`.
Network access is disabled by default, artifacts are restricted to a configurable
size budget, and all tool calls are logged through the lineage subsystem.

## Path to Hardware

The current implementation uses a NumPy-based simulator. To connect to Qiskit
hardware provide `QISKIT_API_TOKEN` in the environment and extend the
`quantum_qiskit` tool. The policy guard allows enabling network access only when
a valid token is present.

## Gallery

![Bloch sphere](artifacts/bloch_q0.png)

![Bell histogram](artifacts/bell_hist.png)

![Grover success curve](artifacts/grover_curve.png)
