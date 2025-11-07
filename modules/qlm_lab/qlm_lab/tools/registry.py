from __future__ import annotations

"""Tool registry for mapping tag names to callables."""

from typing import Any, Callable, Dict

from . import la
from . import math_cas
from . import quantum_np as Q
from . import viz as V


class ToolRegistry:
    """Name→callable registry for LLM tool-calling."""

    def __init__(self) -> None:
        self._map: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        """Register ``fn`` under ``name``."""

        self._map[name] = fn

    def get(self, name: str) -> Callable[..., Any]:
        """Return the callable registered for ``name``."""

        if name not in self._map:
            raise KeyError(f"Unknown tool '{name}'")
        return self._map[name]


def default_registry() -> ToolRegistry:
    """Populate a registry with the standard QLM tools."""

    reg = ToolRegistry()
    reg.register("quantum_np.bell_phi_plus", Q.bell_phi_plus)
    reg.register("quantum_np.measure_counts", Q.measure_counts)
    reg.register("quantum_np.chsh_value_phi_plus", Q.chsh_value_phi_plus)
    reg.register("quantum_np.qft_matrix", Q.qft_matrix)
    reg.register("viz.hist", V.hist)
    if hasattr(la, "eig"):
        reg.register("la.eig", getattr(la, "eig"))
    if hasattr(math_cas, "simplify"):
        reg.register("math_cas.simplify", getattr(math_cas, "simplify"))
    return reg


__all__ = ["ToolRegistry", "default_registry"]
