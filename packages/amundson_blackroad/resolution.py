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
