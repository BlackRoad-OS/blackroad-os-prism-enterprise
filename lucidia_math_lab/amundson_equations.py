"""Amundson coherence, energy, and learning equations.

This module encodes the first entry in the proposed Amundson
series—*Amundson I: The Coherence Gradient Equation*—and
provides scaffolding for the follow-up energy and learning
laws.  The implementation mirrors the conversation blueprint:
phase accelerates with connection and slows with decoherence.

The key constructs follow the original exposition:

* :class:`AmundsonCoherenceModel` captures the differential
  dynamics

  .. math::

     \frac{d\phi}{dt} = \omega_0 + \lambda C(x, y) - \eta E_\phi

  where ``C`` measures cosine coherence and ``E`` denotes the
  decoherence energy penalty.

* :func:`coherence` isolates the cosine alignment term
  :math:`C(x, y)=\cos(\phi_x-\phi_y)`.

* :func:`decoherence_energy` implements the thermal energy
  penalty :math:`E_\phi = k_B T \, \lambda \, r_x r_y (1-\cos(\phi_x-\phi_y))`.

* :func:`phase_derivative` exposes the coherence gradient as a
  reusable utility.

Placeholders for **Amundson II** and **Amundson III** are
included so future work can extend the energy balance and
learning formulations in situ.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol


def coherence(phi_x: float, phi_y: float) -> float:
    """Return the cosine coherence term :math:`C(x, y)`.

    Parameters
    ----------
    phi_x, phi_y:
        Phases whose alignment is being measured.
    """

    return math.cos(phi_x - phi_y)


def decoherence_energy(
    *,
    phi_x: float,
    phi_y: float,
    r_x: float,
    r_y: float,
    lambda_: float,
    k_b_t: float,
) -> float:
    """Compute the decoherence energy :math:`E_\phi`.

    Parameters mirror the seed formulation: ``r_x`` and ``r_y``
    are participation amplitudes, ``lambda_`` controls coupling,
    and ``k_b_t`` is the thermal scale :math:`k_B T`.
    """

    return k_b_t * lambda_ * r_x * r_y * (1.0 - coherence(phi_x, phi_y))


def phase_derivative(
    *,
    omega_0: float,
    lambda_: float,
    eta: float,
    phi_x: float,
    phi_y: float,
    r_x: float,
    r_y: float,
    k_b_t: float,
) -> float:
    """Evaluate the Amundson I coherence gradient equation.

    This function computes :math:`\frac{d\phi}{dt}` from the
    provided state, matching the proposed dynamic:

    .. math::

       \omega_0 + \lambda\,C(x,y) - \eta\,E_\phi
    """

    c_term = coherence(phi_x, phi_y)
    energy = decoherence_energy(
        phi_x=phi_x,
        phi_y=phi_y,
        r_x=r_x,
        r_y=r_y,
        lambda_=lambda_,
        k_b_t=k_b_t,
    )
    return omega_0 + lambda_ * c_term - eta * energy


class SupportsPhaseUpdate(Protocol):
    """Protocol for objects that can consume phase derivatives."""

    def update_phase(self, d_phi_dt: float) -> None:  # pragma: no cover - protocol signature
        """Apply the derivative to internal state."""


@dataclass(slots=True)
class AmundsonCoherenceModel:
    """Stateful helper implementing Amundson I dynamics."""

    omega_0: float
    lambda_: float
    eta: float
    k_b_t: float

    def dphi_dt(
        self,
        *,
        phi_x: float,
        phi_y: float,
        r_x: float,
        r_y: float,
    ) -> float:
        """Return the instantaneous phase derivative."""

        return phase_derivative(
            omega_0=self.omega_0,
            lambda_=self.lambda_,
            eta=self.eta,
            phi_x=phi_x,
            phi_y=phi_y,
            r_x=r_x,
            r_y=r_y,
            k_b_t=self.k_b_t,
        )

    def evolve(self, system: SupportsPhaseUpdate, **state: float) -> float:
        """Evaluate the derivative and forward it to *system*.

        The method is intentionally lightweight: it returns the
        derivative so callers can both inspect and apply it.
        """

        derivative = self.dphi_dt(**state)
        system.update_phase(derivative)
        return derivative


def amundson_energy_balance(*, energy: float, dissipation: float) -> float:
    """Placeholder for Amundson II energy balance law.

    The energy balance law will govern :math:`\frac{dE_\phi}{dt}`
    so that systems can explicitly track how coherence work
    converts into thermal losses.  The exact formulation is left
    open for future refinement.
    """

    # TODO: Implement once the energy balance derivation is specified.
    raise NotImplementedError("Amundson II energy balance has not been derived yet.")


def amundson_learning_update(*, gradient: float, weights: float) -> float:
    """Placeholder for Amundson III learning law.

    Amundson III will translate coherence gradients into weight
    updates, providing a physicalized backpropagation rule.  The
    returned value is expected to be a delta for the weights once
    the learning equation is finalized.
    """

    # TODO: Implement once the learning dynamics are formally defined.
    raise NotImplementedError("Amundson III learning dynamics are pending design.")
