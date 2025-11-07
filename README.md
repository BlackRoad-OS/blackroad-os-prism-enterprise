# Quantum Lab

A production-grade quantum computing teaching lab featuring a NumPy simulator, Qiskit hardware wrappers, visualizations, and pedagogy notes.

## Quickstart

```bash
make setup
make demo
```

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

See `quantum_lab/pedagogy/unsolved/` for mini-essays connecting demos to enduring mathematical challenges.
