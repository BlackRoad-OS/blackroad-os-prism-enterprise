"""Thermodynamic helpers anchored to the Codex Landauer floor."""

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


def landauer_floor(bits: float, temperature: float, *, k_b: float = K_BOLTZMANN) -> float:
    """Return the minimal energy dissipation for irreversible computation."""

    if bits < 0:
        raise ValueError("bits must be non-negative")
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    return k_b * temperature * np.log(2.0) * bits


def irreversible_energy(transitions: int, temperature: float) -> float:
    """Compute the floor given a count of irreversible transitions."""

    if transitions < 0:
        raise ValueError("transitions must be non-negative")
    return landauer_floor(float(transitions), temperature)


def annotate_run_with_thermo(
    payload: Dict[str, object],
    *,
    bits: float,
    temperature: float,
    seed: Optional[int] = None,
) -> Dict[str, object]:
    """Attach thermo provenance metadata to a run payload."""

    delta_e = landauer_floor(bits, temperature)
    record = ThermoRecord(bits=bits, temperature=temperature, delta_e_min=delta_e, seed=seed)
    enriched = dict(payload)
    enriched["thermo"] = {
        "bits": record.bits,
        "temperature": record.temperature,
        "delta_e_min": record.delta_e_min,
        "seed": record.seed,
    }
    return enriched
