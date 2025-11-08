import math
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "packages"))

from amundson_blackroad.resolution import AmbrContext, K_BOLTZMANN, resolve_coherence_inputs


def test_defaults_and_units() -> None:
    values, missing, why = resolve_coherence_inputs()
    assert missing == []
    assert "k_b_t" in why and "omega_0" in why
    expected = 300.0 * K_BOLTZMANN
    assert math.isclose(values["k_b_t"], expected, rel_tol=1e-12)


def test_context_fills_phases() -> None:
    ctx = AmbrContext(last_phi_x=0.3, last_phi_y=1.1)
    values, missing, _ = resolve_coherence_inputs(ctx=ctx)
    assert missing == []
    assert values["phi_x"] == 0.3
    assert values["phi_y"] == 1.1
