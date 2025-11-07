from __future__ import annotations

import math

import numpy as np
import pytest

from qlm_lab.tools import quantum_np as Q


def test_basis_state_and_apply_gate():
    state = Q.basis_state(2, 0)
    state = Q.apply_gate(state, Q.H, [0])
    state = Q.apply_gate(state, Q.CNOT, [0, 1])
    bell = Q.bell_phi_plus()
    assert np.allclose(state, bell)


def test_measure_counts_balanced():
    psi = Q.bell_phi_plus()
    counts = Q.measure_counts(psi, shots=2048)
    assert pytest.approx(0.5, rel=0.2) == counts["00"]
    assert pytest.approx(0.5, rel=0.2) == counts["11"]


def test_chsh_value_within_bounds():
    value = Q.chsh_value_phi_plus()
    assert 2.2 < value <= 2.9


def test_qft_matrix_unitary():
    mat = Q.qft_matrix(3)
    identity = mat.conj().T @ mat
    assert np.allclose(identity, np.eye(8))


def test_apply_qft_phase_peak():
    n = 3
    N = 2 ** n
    freq = 2
    amps = np.array([np.exp(2j * np.pi * freq * j / N) / math.sqrt(N) for j in range(N)], dtype=complex)
    spectrum = np.abs(Q.apply_qft(amps)) ** 2
    target = (N - freq) % N
    assert spectrum[target] == pytest.approx(1.0, abs=1e-6)


def test_grover_success_exceeds_baseline():
    probs = Q.grover_success_probabilities(3, 5, 5)
    baseline = 1 / 8
    assert max(probs) > 3 * baseline


def test_pauli_expectation_and_error():
    psi = Q.bell_phi_plus()
    expectation = Q.pauli_expectation(psi, "ZZ")
    assert expectation == pytest.approx(1.0)
    with pytest.raises(ValueError):
        Q.pauli_expectation(psi, "ZA")


def test_bloch_coordinates_pure_state():
    state = np.array([1, 0], dtype=complex)
    x, y, z = Q.bloch_coordinates(state)
    assert (x, y, z) == pytest.approx((0.0, 0.0, 1.0))


def test_basis_state_invalid_index():
    with pytest.raises(ValueError):
        Q.basis_state(1, 3)


def test_apply_gate_invalid_inputs():
    state = Q.basis_state(1, 0)
    with pytest.raises(ValueError):
        Q.apply_gate(state, Q.CNOT, [0])


def test_oracle_out_of_range():
    with pytest.raises(ValueError):
        Q.oracle_for_index(2, 4)
