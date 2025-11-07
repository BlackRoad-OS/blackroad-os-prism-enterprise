"""Core kernels for the Amundson-BlackRoad simulations."""

from .spiral import (
    simulate_am2,
    am2_step,
    field_lift,
    jacobian_am2,
)
from .autonomy import (
    step_transport,
    simulate_transport,
    conserved_mass,
    compute_flux,
    trust_field_step,
)
from .coupling import curvature_source, couple_curvature_response
from .thermo import landauer_floor, irreversible_energy, annotate_run_with_thermo

__all__ = [
    "simulate_am2",
    "am2_step",
    "field_lift",
    "jacobian_am2",
    "step_transport",
    "simulate_transport",
    "conserved_mass",
    "compute_flux",
    "trust_field_step",
    "curvature_source",
    "couple_curvature_response",
    "landauer_floor",
    "irreversible_energy",
    "annotate_run_with_thermo",
]
