# Hardware Guide

1. Export `QISKIT_API_TOKEN` with your IBM Quantum token.
2. Choose a backend from `quantum_lab/qiskit_backend/backends.yaml`.
3. Use `quantum_lab.qiskit_backend.run.run_job` to submit circuits.

Without a token the toolkit defaults to Aer simulators and fake backends.
