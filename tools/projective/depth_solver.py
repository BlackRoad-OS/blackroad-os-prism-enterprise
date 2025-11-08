"""Perspective depth solver utilities."""

from __future__ import annotations

import argparse
from typing import Sequence


def depth_from_rail(
    z_a: float,
    z_b: float,
    s_a: float,
    s_b: float,
    s_c: float,
) -> float:
    """Return the physical depth of point ``C`` along a perspective rail.

    Parameters
    ----------
    z_a, z_b:
        Known scene depths (``Z_A`` and ``Z_B``) for two reference marks ``A`` and
        ``B`` positioned along the same receding rail.
    s_a, s_b, s_c:
        Measured coordinates on the drawing (``s(A)``, ``s(B)``, ``s(C)``) taken
        along the straight line that represents the rail.

    The computation follows the closed-form projective relation::

        alpha = (s_a - s_c) / (s_b - s_c)
        Z_C = (alpha * Z_B - Z_A) / (alpha - 1)

    Returns
    -------
    float
        The recovered depth ``Z_C`` for the target point ``C``.

    Raises
    ------
    ValueError
        If any intermediate denominator is zero, indicating a degenerate
        configuration of sample points.
    """

    denom_sb_sc = s_b - s_c
    if denom_sb_sc == 0:
        raise ValueError("s(B) and s(C) must be distinct to define the cross-ratio")

    alpha = (s_a - s_c) / denom_sb_sc
    denom_alpha = alpha - 1.0
    if denom_alpha == 0:
        raise ValueError("alpha must not equal 1; choose reference points spanning C")

    return (alpha * z_b - z_a) / denom_alpha


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compute the depth of a perspective point along a rail using the "
            "cross-ratio relation with the far point at infinity."
        )
    )
    parser.add_argument(
        "depths",
        nargs=2,
        metavar=("Z_A", "Z_B"),
        type=float,
        help="Known physical depths for reference marks A and B.",
    )
    parser.add_argument(
        "coords",
        nargs=3,
        metavar=("sA", "sB", "sC"),
        type=float,
        help="Measured drawing coordinates along the rail for A, B, and target C.",
    )

    args = parser.parse_args(argv)
    z_a, z_b = args.depths
    s_a, s_b, s_c = args.coords

    z_c = depth_from_rail(z_a, z_b, s_a, s_b, s_c)
    print(f"Z_C={z_c}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
