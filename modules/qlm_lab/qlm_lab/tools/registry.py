"""Tool registry helpers for the Toolformer runtime."""
from __future__ import annotations

from typing import Dict, Callable, Any

from . import quantum_np, viz

Registry = Dict[str, Callable[..., Any]]


def default_registry() -> Registry:
    """Return the default mapping from tag names to callables."""

    return {
        "quantum_np.bell_phi_plus": quantum_np.bell_phi_plus,
        "quantum_np.measure_counts": quantum_np.measure_counts,
        "quantum_np.chsh_value_phi_plus": quantum_np.chsh_value_phi_plus,
        "quantum_np.qft_matrix": quantum_np.qft_matrix,
        "viz.hist": viz.hist,
        "viz.bloch": viz.bloch,
        "viz.ascii_circuit": viz.ascii_circuit,
    }


__all__ = ["default_registry", "Registry"]
