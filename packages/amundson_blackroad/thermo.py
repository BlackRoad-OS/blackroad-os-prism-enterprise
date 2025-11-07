"""Thermodynamic helpers for the Amundson–BlackRoad energy ledger."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

K_BOLTZMANN = 1.380649e-23  # J/K


@dataclass
class ThermoRecord:
    bits: float
    temperature: float
    delta_e_min: float
    seed: Optional[int] = None
    provided_energy: Optional[float] = None
    landauer_ok: Optional[bool] = None


def landauer_floor(bits: float, temperature: float, *, k_b: float = K_BOLTZMANN) -> float:
    """Return the minimal energy dissipation for irreversible computation."""

    if bits < 0:
        raise ValueError("bits must be non-negative")
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    return k_b * temperature * np.log(2.0) * bits


def landauer_min(bits: float, temperature: float) -> float:
    """Alias kept for API clarity."""

    return landauer_floor(bits, temperature)


def irreversible_energy(transitions: int, temperature: float) -> float:
    """Compute the floor given a count of irreversible transitions."""

    if transitions < 0:
        raise ValueError("transitions must be non-negative")
    return landauer_floor(float(transitions), temperature)


def spiral_entropy(a: np.ndarray, theta: np.ndarray) -> float:
    """Return a Shannon-style entropy for the spiral state."""

    amplitude_energy = np.abs(a) ** 2 + np.abs(theta) ** 2
    total = float(np.sum(amplitude_energy))
    if total <= 0.0:
        return 0.0
    probabilities = amplitude_energy / total
    mask = probabilities > 0
    entropy = -float(np.sum(probabilities[mask] * np.log(probabilities[mask])))
    return entropy


def energy_increment(
    a: np.ndarray,
    theta: np.ndarray,
    dt: float,
    *,
    gamma: float,
    eta: float,
) -> float:
    """Numerically integrate the incremental AM-4 energy ledger."""

    if dt <= 0:
        raise ValueError("dt must be positive")
    a_safe = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
    theta_safe = np.nan_to_num(theta, nan=0.0, posinf=0.0, neginf=0.0)
    dissipation = gamma * np.square(a_safe)
    coupling = eta * np.abs(a_safe * theta_safe)
    integrand = dissipation + coupling
    return float(np.trapz(integrand, dx=dt))


def annotate_run_with_thermo(
    payload: Dict[str, object],
    *,
    bits: float,
    temperature: float,
    seed: Optional[int] = None,
    energy: Optional[float] = None,
) -> Dict[str, object]:
    """Attach thermo provenance metadata to a run payload."""

    delta_e = landauer_floor(bits, temperature)
    record = ThermoRecord(
        bits=bits,
        temperature=temperature,
        delta_e_min=delta_e,
        seed=seed,
        provided_energy=energy,
        landauer_ok=None if energy is None else energy >= delta_e,
    )
    enriched = dict(payload)
    enriched["thermo"] = {
        "bits": record.bits,
        "temperature": record.temperature,
        "delta_e_min": record.delta_e_min,
        "seed": record.seed,
        "provided_energy": record.provided_energy,
        "landauer_ok": record.landauer_ok,
    }
    return enriched
