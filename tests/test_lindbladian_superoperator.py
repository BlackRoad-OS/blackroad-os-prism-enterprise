import numpy as np

from agents.blackroad_agent_framework_package5 import LindbladianSuperoperator


def is_hermitian(A: np.ndarray, tol: float = 1e-10) -> bool:
    return np.allclose(A, A.conj().T, atol=tol)


def test_gksl_dissipator_hermitian_derivative():
    L = LindbladianSuperoperator(n_dim=2)
    # Single Lindblad operator: sigma_minus
    sigma_minus = np.array([[0, 1], [0, 0]], dtype=complex)
    L.add_lindblad_operator(sigma_minus, gamma=0.1)
    # Start from excited state density matrix
    rho = np.array([[0, 0], [0, 1]], dtype=complex)
    D = L.lindblad_dissipator(rho)
    assert D.shape == (2, 2)
    assert is_hermitian(D), "GKSL dissipator should yield Hermitian dρ/dt"
