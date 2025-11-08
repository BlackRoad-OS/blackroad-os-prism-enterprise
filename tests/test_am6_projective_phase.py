"""Tests for the Amundson VI projective phase mapping."""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from types import ModuleType

MODULE_DIR = Path(__file__).resolve().parents[1] / "packages" / "amundson_blackroad"
MODULE_PATH = MODULE_DIR / "projective.py"

PARENT_NAME = "amundson_blackroad"
if PARENT_NAME not in sys.modules:
    package = ModuleType(PARENT_NAME)
    package.__path__ = [str(MODULE_DIR)]
    sys.modules[PARENT_NAME] = package

SPEC = importlib.util.spec_from_file_location(f"{PARENT_NAME}.projective", MODULE_PATH)
assert SPEC and SPEC.loader
projective = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = projective
SPEC.loader.exec_module(projective)

u_from_theta = projective.u_from_theta
theta_from_u = projective.theta_from_u
projective_am2_step = projective.projective_am2_step


def test_projective_round_trip_near_pi_over_two() -> None:
    """u = tan(theta/2) remains well-behaved near π/2."""

    theta = math.pi / 2 - 1e-9
    u = u_from_theta(theta)
    theta_back = theta_from_u(u)
    assert math.isclose(theta_back, theta, rel_tol=0.0, abs_tol=1e-9)


def test_projective_derivative_stays_finite() -> None:
    """The projective derivative does not diverge at the polar seam."""

    theta = math.pi / 2 - 1e-6
    u = u_from_theta(theta)
    a_dot, u_dot, theta_dot, _ = projective_am2_step(
        a=0.4, u=u, gamma=0.2, kappa=0.3, eta=0.5, omega0=1.2
    )

    assert math.isfinite(u_dot)
    assert math.isfinite(theta_dot)
    assert abs(math.tan(theta)) > 1e6  # highlight singular original coordinate
    assert abs(u) < 10.0  # Projective coordinate stays bounded
    assert abs(a_dot) < 10.0
