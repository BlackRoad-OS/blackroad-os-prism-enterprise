"""Thermodynamic helpers for the Amundson–BlackRoad energy ledger."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional

K_BOLTZMANN = 1.380649e-23  # J/K


def spiral_entropy(a: float, theta: float, kB: float = K_BOLTZMANN) -> float:
    """Compute spiral entropy :math:`S_a = k_B a \theta` in joule per kelvin."""
@dataclass
class ThermoRecord:
    bits: float
    temperature: float
    delta_e_min: float
    seed: Optional[int] = None
    provided_energy: Optional[float] = None
    landauer_ok: Optional[bool] = None

    return kB * a * theta


def energy_increment(
    T: float,
    da: float,
    dtheta: float,
    a: float,
    theta: float,
    Omega: float = 0.0,
    kB: float = K_BOLTZMANN,
) -> float:
    """Evaluate the AM-4 discrete energy increment in joules."""

    return T * kB * (da * theta + a * dtheta) + Omega * dtheta


def landauer_min(T: float, n_bits: float, kB: float = K_BOLTZMANN) -> float:
    """Return the Landauer minimum energy for irreversible computation in joules."""

    if n_bits < 0:
        raise ValueError("n_bits must be non-negative")
    if T <= 0:
        raise ValueError("temperature must be positive")
    return kB * T * math.log(2.0) * n_bits


def landauer_floor(bits: float, temperature: float, *, k_b: float = K_BOLTZMANN) -> float:
    """Backward compatible alias returning the minimal irreversible energy."""

    return landauer_min(temperature, bits, kB=k_b)


def landauer_min(bits: float, temperature: float) -> float:
    """Alias kept for API clarity."""

    return landauer_floor(bits, temperature)


def irreversible_energy(transitions: int, temperature: float) -> float:
    """Compute the Landauer floor given a count of irreversible transitions."""

    if transitions < 0:
        raise ValueError("transitions must be non-negative")
    return landauer_floor(float(transitions), temperature)


@dataclass
class ThermoRecord:
    """Structured metadata describing an irreversible run."""

    bits: float
    temperature: float
    delta_e_min: float
    seed: Optional[int] = None
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
    n_bits: Optional[float] = None,
    Omega: float | None = None,
    da: float | None = None,
    dtheta: float | None = None,
    a: float | None = None,
    theta: float | None = None,
    energy: Optional[float] = None,
) -> Dict[str, object]:
    """Attach thermo provenance metadata and optional AM-4 ledger entries to a run."""

    effective_bits = n_bits if n_bits is not None else bits
    delta_e = landauer_min(temperature, effective_bits)
    record = ThermoRecord(bits=effective_bits, temperature=temperature, delta_e_min=delta_e, seed=seed)
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
    thermo_payload: Dict[str, object] = {
        "bits": record.bits,
        "temperature_K": record.temperature,
        "delta_e_min_J": record.delta_e_min,
        "landauer_units": "J",
        "temperature": record.temperature,
        "delta_e_min": record.delta_e_min,
        "seed": record.seed,
        "provided_energy": record.provided_energy,
        "landauer_ok": record.landauer_ok,
    }
    if record.seed is not None:
        thermo_payload["seed"] = record.seed
    if a is not None and theta is not None and da is not None and dtheta is not None:
        thermo_payload["spiral_entropy_J_per_K"] = spiral_entropy(a, theta)
        thermo_payload["energy_increment_J"] = energy_increment(
            temperature,
            da,
            dtheta,
            a,
            theta,
            Omega=Omega or 0.0,
        )
        thermo_payload["theta_work_J"] = (Omega or 0.0) * dtheta
    enriched["thermo"] = thermo_payload
    return enriched


__all__ = [
    "K_BOLTZMANN",
    "spiral_entropy",
    "energy_increment",
    "landauer_min",
    "landauer_floor",
    "irreversible_energy",
    "ThermoRecord",
    "annotate_run_with_thermo",
]
