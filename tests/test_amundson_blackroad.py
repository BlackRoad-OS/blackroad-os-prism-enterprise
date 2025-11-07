from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "packages"))

from amundson_blackroad.autonomy import conserved_mass, simulate_transport
from amundson_blackroad.spiral import simulate_am2
from amundson_blackroad.thermo import energy_increment, landauer_min, spiral_entropy


@pytest.mark.parametrize("steps", [250, 500])
def test_mass_conservation_within_threshold(steps: int) -> None:
    x = np.linspace(-5.0, 5.0, 512)
    A0 = np.exp(-x ** 2)
    rho = np.tanh(x)
    dt = 1e-3
    result = simulate_transport(x, A0, rho, steps, dt, mu_A=0.8)
    initial_mass = conserved_mass(x, A0)
    assert pytest.approx(initial_mass, rel=1e-3) == result["mass"]


def test_spiral_entropy_positive() -> None:
    t, a, theta, _ = simulate_am2(1.0, 1e-3, 0.3, 0.0, 0.8, 0.2, 0.4, 1.2)
    entropy = spiral_entropy(a, theta)
    assert entropy >= 0.0
    assert entropy == pytest.approx(spiral_entropy(a, theta))


def test_energy_increment_agrees_with_finite_difference() -> None:
    T = 2.0
    dt = 1e-3
    params = dict(T=T, dt=dt, a0=0.2, theta0=0.1, gamma=0.5, kappa=0.3, eta=0.4, omega0=1.1)
    t, a, theta, _ = simulate_am2(**params)
    ledger_value = energy_increment(a, theta, dt, gamma=params["gamma"], eta=params["eta"])
    finite_diff = np.trapz(params["gamma"] * a ** 2 + params["eta"] * np.abs(a * theta), dx=dt)
    assert pytest.approx(finite_diff, rel=1e-6) == ledger_value


def test_landauer_min_matches_manual() -> None:
    bits = 64
    temperature = 310.0
    expected = 1.380649e-23 * temperature * np.log(2.0) * bits
    assert pytest.approx(expected, rel=1e-12) == landauer_min(bits, temperature)
