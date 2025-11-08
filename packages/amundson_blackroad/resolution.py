"""Utilities for resolving missing Amundson inputs with units."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

K_BOLTZMANN: float = 1.380649e-23
"""Boltzmann constant in joules per kelvin (J/K)."""


@dataclass
class AmbrContext:
    """Contextual defaults for coherence resolution.

    Attributes
    ----------
    last_phi_x: float
        Last observed phase component :math:`\phi_x` in radians.
    last_phi_y: float
        Last observed phase component :math:`\phi_y` in radians.
    default_temperature_K: float
        Reference temperature in kelvin (K) for thermal defaults.
    default_r: float
        Default coherence amplitude in arbitrary units.
    """

    last_phi_x: float
    last_phi_y: float
    default_temperature_K: float = 300.0
    default_r: float = 1.0


def resolve_coherence_inputs(
    ctx: AmbrContext,
    **payload: Any,
) -> Tuple[Dict[str, float], List[str], Dict[str, str]]:
    """Resolve missing coherence inputs and explain the defaults.

    Parameters
    ----------
    ctx:
        Context providing recent phase history and thermal defaults.
    **payload:
        Arbitrary keyword inputs to be completed. Values are dimensioned as
        follows: phases in radians, amplitudes dimensionless, and temperatures
        in kelvin.

    Returns
    -------
    resolved:
        Mapping of completed inputs. Energy terms are measured in joules (J).
    missing:
        Ordered list of field names that were inferred rather than supplied.
    why:
        Explanation for each populated value, including supplied entries.
    """

    resolved: Dict[str, float] = {}
    missing: List[str] = []
    why: Dict[str, str] = {}

    # Copy provided payload while filtering out None placeholders.
    for key, value in payload.items():
        if value is not None:
            resolved[key] = value

    def _set_default(key: str, value: float, explanation: str) -> None:
        if key not in resolved:
            resolved[key] = value
            missing.append(key)
            why[key] = explanation

    _set_default("omega_0", 1.0, "Default angular frequency ω₀ = 1.0 rad/s.")
    _set_default("lambda_", 0.5, "Default coupling λ = 0.5 (dimensionless).")
    _set_default("eta", 0.2, "Default dissipation η = 0.2 (dimensionless).")
    _set_default(
        "phi_x",
        ctx.last_phi_x,
        "Phase φ_x inherited from context history (rad).",
    )
    _set_default(
        "phi_y",
        ctx.last_phi_y,
        "Phase φ_y inherited from context history (rad).",
    )
    _set_default(
        "r",
        ctx.default_r,
        "Amplitude r seeded from context default (dimensionless).",
    )
    _set_default(
        "amplitude",
        1.0,
        "Unit amplitude used when no magnitude supplied (dimensionless).",
    )

    temperature_default = ctx.default_temperature_K
    if "temperature_K" in resolved:
        temperature = resolved["temperature_K"]
    else:
        temperature = temperature_default
        _set_default(
            "temperature_K",
            temperature_default,
            "Context-provided temperature baseline (K).",
        )

    if "k_b_t" not in resolved:
        resolved["k_b_t"] = K_BOLTZMANN * float(temperature)
        missing.append("k_b_t")
        why[
            "k_b_t"
        ] = f"Computed k_B·T from temperature_K={temperature:.3f} K (J)."

    for key in resolved:
        if key not in why:
            why[key] = "Provided explicitly in payload."

    return resolved, missing, why
