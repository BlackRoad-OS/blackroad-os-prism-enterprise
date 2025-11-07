from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / 'packages'))

from amundson_blackroad.autonomy import conserved_mass, simulate_transport
from amundson_blackroad.spiral import jacobian_am2, simulate_am2
from amundson_blackroad.thermo import landauer_floor


@pytest.mark.parametrize('steps', [250, 500])
def test_v1_mass_conservation(steps):
    x = np.linspace(-5.0, 5.0, 512)
    A0 = np.exp(-x**2)
    rho = np.tanh(x)
    dt = 1e-3
    result = simulate_transport(x, A0, rho, steps, dt, mu_A=0.8)
    m0 = conserved_mass(x, A0)
    m1 = float(result['mass'])
    assert pytest.approx(m0, rel=1e-3) == m1



def test_v2_linear_lift_matches_analytic():
    gamma = 0.8
    eta = 0.2
    kappa = 0.1
    omega0 = 1.5
    a0 = 0.3
    t, a, theta, _ = simulate_am2(
        1.0,
        1e-3,
        a0,
        0.0,
        gamma,
        kappa,
        eta,
        omega0,
        phi=lambda amp: amp,
        lift_fn=lambda a_val, _theta: a_val,
    )
    expected = a0 * np.exp((eta - gamma) * t)
    assert np.allclose(a, expected, atol=1e-3)
    numerical_frequency = np.gradient(theta, t)
    assert np.allclose(numerical_frequency, omega0 + kappa * a, atol=1e-3)



def test_v3_landauer_floor_positive():
    bits = 128
    temperature = 310.0
    energy = landauer_floor(bits, temperature)
    assert energy > 0
    manual = 1.380649e-23 * temperature * np.log(2.0) * bits
    assert pytest.approx(manual, rel=1e-12) == energy



def test_v4_jacobian_stability():
    gamma = 1.0
    eta = 0.2
    kappa = 0.4
    omega0 = 1.2
    J = jacobian_am2(
        0.0,
        0.0,
        gamma,
        kappa,
        eta,
        omega0,
        phi=lambda amp: amp,
        lift_fn=lambda a_val, _theta: a_val,
        eps=1e-6,
    )
    eigenvalues = np.linalg.eigvals(J)
    assert np.all(eigenvalues.real <= 1e-8)
    assert np.isclose(eigenvalues.max().real, 0.0, atol=1e-8)
    assert eigenvalues.min().real <= 0.0
