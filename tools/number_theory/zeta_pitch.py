"""Utilities for sampling the Amundson pitch of the Riemann zeta function.

The *pitch* associated to a complex trajectory describes the ratio between
radial growth and angular sweep of the image curve.  For an analytic function
``f`` evaluated along the critical line ``s(t) = 1/2 + i t`` we can express the
pitch purely in terms of the logarithmic derivative of ``f``:

.. math::

    c_f(t) = \frac{\mathrm d \ln |f(s(t))| / \mathrm d t}{\mathrm d \arg f(s(t)) / \mathrm d t}.

This module provides helpers to evaluate ``c_f`` for the Riemann zeta function
``ζ`` using modest numerical precision.  The implementation relies only on
``mpmath`` and Matplotlib (for optional plotting).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

import csv
import math

import mpmath as mp

try:  # Optional plotting dependency.
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - matplotlib is optional.
    plt = None


@dataclass(frozen=True)
class ZetaPitchSample:
    """Container for a single ``ζ`` pitch measurement."""

    t: float
    zeta: complex
    log_derivative: complex
    pitch: float

    @property
    def magnitude(self) -> float:
        """Return ``|ζ(1/2 + i t)|``."""

        return abs(self.zeta)

    @property
    def phase(self) -> float:
        """Return ``arg ζ(1/2 + i t)`` using the principal branch."""

        return math.atan2(self.zeta.imag, self.zeta.real)


def _zeta_at(t: float) -> complex:
    """Evaluate ``ζ`` on the critical line with high precision."""

    return complex(mp.zeta(0.5 + t * 1j))


def _zeta_time_derivative(t: float, h: float) -> complex:
    """Finite-difference approximation of ``dζ/dt`` along the critical line."""

    s_plus = 0.5 + 1j * (t + h)
    s_minus = 0.5 + 1j * (t - h)
    z_plus = mp.zeta(s_plus)
    z_minus = mp.zeta(s_minus)
    return complex((z_plus - z_minus) / (2 * h))


def _pitch_from_values(zeta_val: complex, d_zeta_dt: complex) -> float:
    """Compute the Amundson pitch from ``ζ`` and its time derivative."""

    if zeta_val == 0:
        return math.inf

    log_derivative = d_zeta_dt / zeta_val
    # Along ``s = 1/2 + i t`` we have ``d/dt log ζ = log_derivative``.
    numerator = log_derivative.real
    denominator = log_derivative.imag
    if denominator == 0:
        return math.inf if numerator > 0 else -math.inf
    return numerator / denominator


def sample_zeta_pitch(
    t_values: Sequence[float], *,
    h: float = 1e-4,
    mp_dps: int = 80,
) -> List[ZetaPitchSample]:
    """Evaluate ``c_ζ(t)`` for the provided ``t`` values.

    Args:
        t_values: Iterable of ordinates on the critical line.
        h: Step used for the symmetric finite difference in ``t``.
        mp_dps: Decimal precision forwarded to ``mpmath``.

    Returns:
        A list of :class:`ZetaPitchSample` entries ordered as ``t_values``.
    """

    mp.mp.dps = mp_dps
    samples: List[ZetaPitchSample] = []
    for t in t_values:
        zeta_val = _zeta_at(t)
        d_zeta_dt = _zeta_time_derivative(t, h)
        log_derivative = d_zeta_dt / zeta_val if zeta_val != 0 else complex("nan")
        pitch = _pitch_from_values(zeta_val, d_zeta_dt)
        samples.append(
            ZetaPitchSample(
                t=float(t),
                zeta=zeta_val,
                log_derivative=log_derivative,
                pitch=pitch,
            )
        )
    return samples


def sample_interval(
    t_start: float,
    t_end: float,
    *,
    num_points: int,
    h: float = 1e-4,
    mp_dps: int = 80,
) -> List[ZetaPitchSample]:
    """Convenience wrapper to sample a uniform grid on ``[t_start, t_end]``."""

    if num_points < 2:
        raise ValueError("num_points must be at least 2 to define a grid")
    spacing = (t_end - t_start) / (num_points - 1)
    grid = [t_start + i * spacing for i in range(num_points)]
    return sample_zeta_pitch(grid, h=h, mp_dps=mp_dps)


def write_csv(samples: Iterable[ZetaPitchSample], path: Path | str) -> None:
    """Persist ``ζ`` pitch samples to ``path`` as CSV."""

    fieldnames = ["t", "real", "imag", "log_derivative_real", "log_derivative_imag", "pitch"]
    with Path(path).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for sample in samples:
            writer.writerow(
                {
                    "t": sample.t,
                    "real": sample.zeta.real,
                    "imag": sample.zeta.imag,
                    "log_derivative_real": sample.log_derivative.real,
                    "log_derivative_imag": sample.log_derivative.imag,
                    "pitch": sample.pitch,
                }
            )


def plot_pitch(samples: Sequence[ZetaPitchSample], *, path: Path | str | None = None) -> None:
    """Plot ``c_ζ(t)`` for visual inspection.

    The plot shows the pitch together with the magnitude of ``ζ``.  When
    ``path`` is ``None`` a window is displayed (if Matplotlib is available).
    Otherwise the plot is saved to ``path``.
    """

    if plt is None:  # pragma: no cover - plotting is optional.
        raise RuntimeError("Matplotlib is required for plotting but is not available")

    ts = [sample.t for sample in samples]
    pitches = [sample.pitch for sample in samples]
    magnitudes = [sample.magnitude for sample in samples]

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.set_title("Amundson pitch of ζ(1/2 + i t)")
    ax1.set_xlabel("t")
    ax1.set_ylabel("c_ζ(t)", color="tab:blue")
    ax1.plot(ts, pitches, color="tab:blue", label="pitch")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("|ζ|")
    ax2.plot(ts, magnitudes, color="tab:orange", alpha=0.6, label="|ζ|")

    fig.tight_layout()
    if path is None:
        plt.show()
    else:
        fig.savefig(path)
    plt.close(fig)


__all__ = [
    "ZetaPitchSample",
    "sample_zeta_pitch",
    "sample_interval",
    "write_csv",
    "plot_pitch",
]
