"""Core kernels for the Amundson-BlackRoad simulations."""

from .spiral import (
    simulate_am2,
    am2_step,
    field_lift,
    jacobian_am2,
    fixed_point_stability,
    StabilityReport,
)
from .autonomy import (
    step_transport,
    simulate_transport,
    conserved_mass,
    compute_flux,
    trust_field_step,
)
from .coupling import curvature_source, couple_curvature_response
from .curvature import simulate_a_field
from .thermo import (
    K_BOLTZMANN,
    spiral_entropy,
    energy_increment,
    landauer_min,
    landauer_floor,
    irreversible_energy,
    annotate_run_with_thermo,
)

__all__ = [
    "simulate_am2",
    "am2_step",
    "field_lift",
    "jacobian_am2",
    "fixed_point_stability",
    "StabilityReport",
    "step_transport",
    "simulate_transport",
    "conserved_mass",
    "compute_flux",
    "trust_field_step",
    "curvature_source",
    "couple_curvature_response",
    "simulate_a_field",
    "K_BOLTZMANN",
    "spiral_entropy",
    "energy_increment",
    "landauer_min",
    "landauer_floor",
    "irreversible_energy",
    "annotate_run_with_thermo",
]
