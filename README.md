<<<<<<< Updated upstream
# QLM Lab

QLM Lab is a lightweight environment for experimenting with quantum-aware
language model agents. A Quantum Language Model (QLM) combines deterministic
rule-based reasoning with structured access to quantum simulation tools to
produce verifiable artefacts such as plots, metrics, and tests.
=======
# Quantum Lab

A production-grade quantum computing teaching lab featuring a NumPy simulator, Qiskit hardware wrappers, visualizations, and pedagogy notes.
>>>>>>> Stashed changes

## Quickstart

```bash
make setup
make demo
```

<<<<<<< Updated upstream
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
=======
## Feature Matrix

| Capability | Local Simulator | Qiskit Backends |
| --- | --- | --- |
| Statevector simulation | ✅ | ✅ |
| Noise channels | ✅ | ✅ (through backend models) |
| Circuit visualization | ✅ | ✅ |
| Hardware execution | ❌ | ✅ (token required) |

## Artifacts

Running `make demo` produces:

- `artifacts/bell_hist.png`
- `artifacts/bloch_example.png`
- `artifacts/grover_success.png`

## Pedagogy Path

1. `notebooks/01_qubit_basics.ipynb` — single qubits and Bloch sphere.
2. `notebooks/02_entanglement_bell.ipynb` — Bell states and CHSH violations.
3. `notebooks/03_qft_and_phase.ipynb` — Fourier transforms and phase estimation.
4. `notebooks/04_grover_vs_random.ipynb` — search speed-ups.
5. `notebooks/05_noise_and_mitigation.ipynb` — compare ideal vs noisy evolutions.
6. `notebooks/06_qiskit_hardware_roundtrip.ipynb` — simulator to hardware handoff.

## Hardware Access

Set the `QISKIT_API_TOKEN` environment variable before using IBM hardware. Without a token the tooling defaults to Aer simulators and fake backends.

## Unsolved Problems Notes

<<<<<<< main
## i18n & Themes
Translate messages with `i18n.translate.t` and run the TUI with `--theme light|dark`.

### Bot family demo

The repository now ships with a tiny in-memory bus and a handful of cooperating bots that
demonstrate planning, execution, and artifact logging. Activate a virtual environment, install
the project in editable mode, and run the orchestrator entrypoint:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python orchestrator/run_demo.py
```

You should see a Bell pair histogram saved to `artifacts/bell_hist.png` alongside a
`lineage.jsonl` log describing the exchanged messages.
=======
See `quantum_lab/pedagogy/unsolved/` for mini-essays connecting demos to enduring mathematical challenges.
>>>>>>> origin/codex/refactor-and-upgrade-quantum-math-teaching-lab
>>>>>>> Stashed changes
