"""QLM Lab package bootstrap."""
from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Any, Dict

import numpy as np

QLAB_DEFAULT_SEED = 1337


def _init_seed() -> int:
    """Initialise the global random seed.

    The seed is taken from the ``QLAB_SEED`` environment variable when present,
    otherwise a deterministic default is used. The chosen seed is applied to the
    Python ``random`` module and ``numpy.random`` for reproducibility across the
    demos, tests, and agent interactions.
    """

    raw = os.environ.get("QLAB_SEED")
    try:
        seed = int(raw) if raw is not None else QLAB_DEFAULT_SEED
    except ValueError as exc:  # pragma: no cover - defensive branch
        raise ValueError("QLAB_SEED must be an integer") from exc
    random.seed(seed)
    np.random.seed(seed)
    return seed


SEED = _init_seed()


def package_info() -> Dict[str, Any]:
    """Return metadata about the package runtime state."""

    return {"seed": SEED, "root": str(Path(__file__).resolve().parent)}


__all__ = ["SEED", "package_info"]
