"""Input resolution helpers for the Amundson–BlackRoad equations."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

K_BOLTZMANN = 1.380649e-23  # J/K


@dataclass(slots=True)
class AmbrContext:
    """Mutable context that stores recently observed state."""

    last_phi_x: float = 0.0
    last_phi_y: float = 0.0
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
    *,
    omega_0: Optional[float] = None,
    lambda_: Optional[float] = None,
    eta: Optional[float] = None,
    phi_x: Optional[float] = None,
    phi_y: Optional[float] = None,
    r_x: Optional[float] = None,
    r_y: Optional[float] = None,
    k_b_t: Optional[float] = None,
    temperature_K: Optional[float] = None,
    ctx: AmbrContext = AmbrContext(),
) -> Tuple[Dict[str, float], List[str], Dict[str, str]]:
    """Resolve missing Amundson I inputs.
    ctx: AmbrContext,
    **payload: Any,
) -> Tuple[Dict[str, float], List[str], Dict[str, str]]:
    """Resolve missing coherence inputs and explain the defaults.

    Parameters
    ----------
    ctx:
        Context storing previously observed phases and defaults.  The
        resolver mutates the context when it needs to surface a default
        temperature or participation amplitude.

    Returns
    -------
    tuple
        ``(resolved_values, missing, provenance)`` where

        * ``resolved_values`` contains floats for every required field,
        * ``missing`` lists still-unresolved keys, and
        * ``provenance`` explains which values were filled implicitly.
    """

    why: Dict[str, str] = {}
    missing: List[str] = []

    if omega_0 is None:
        omega_0 = 1.0
        why["omega_0"] = "default 1.0 (baseline phase drift)"
    if lambda_ is None:
        lambda_ = 0.5
        why["lambda_"] = "default 0.5 (moderate coupling)"
    if eta is None:
        eta = 0.2
        why["eta"] = "default 0.2 (gentle damping)"

    if phi_x is None:
        phi_x = ctx.last_phi_x
        why["phi_x"] = "from context.last_phi_x"
    if phi_y is None:
        phi_y = ctx.last_phi_y
        why["phi_y"] = "from context.last_phi_y"

    if r_x is None:
        r_x = ctx.default_r
        why["r_x"] = "default unity participation"
    if r_y is None:
        r_y = ctx.default_r
        why["r_y"] = "default unity participation"

    if k_b_t is None:
        if temperature_K is None:
            temperature_K = ctx.default_temperature_K
            why["temperature_K"] = "default 300 K"
        k_b_t = K_BOLTZMANN * float(temperature_K)
        why["k_b_t"] = "computed as k_B * T"

    if not math.isfinite(k_b_t) or k_b_t < 0:
        missing.append("k_b_t")

    for name, val in dict(
        phi_x=phi_x,
        phi_y=phi_y,
        r_x=r_x,
        r_y=r_y,
        omega_0=omega_0,
        lambda_=lambda_,
        eta=eta,
    ).items():
        if not math.isfinite(float(val)):
            missing.append(name)

    resolved = dict(
        omega_0=float(omega_0),
        lambda_=float(lambda_),
        eta=float(eta),
        phi_x=float(phi_x),
        phi_y=float(phi_y),
        r_x=float(r_x),
        r_y=float(r_y),
        k_b_t=float(k_b_t),
    )
    return resolved, sorted(set(missing)), why


__all__ = ["AmbrContext", "K_BOLTZMANN", "resolve_coherence_inputs"]
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
