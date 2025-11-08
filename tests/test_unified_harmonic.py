import numpy as np

from agents.blackroad_agent_framework_package5 import UnifiedHarmonicOperator


def test_unified_harmonic_action_is_finite_and_nonzero():
    op = UnifiedHarmonicOperator()
    val = op.compute_unified_action(n_points=512)
    assert isinstance(val, complex)
    assert np.isfinite(val.real)
    assert np.isfinite(val.imag)
    assert abs(val) > 0.0
