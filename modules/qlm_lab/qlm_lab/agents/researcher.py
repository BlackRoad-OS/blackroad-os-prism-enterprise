"""Research helper agent."""
from __future__ import annotations

from typing import List

from ..proto import Msg, new
from ..tools import math_cas
from .base import Agent


class Researcher(Agent):
    """Collect analytical facts supporting the main workflow."""

    name = "researcher"

    def can_handle(self, m: Msg) -> bool:
        return m.recipient == self.name and m.kind == "task" and m.op == "gather_context"

    def handle(self, m: Msg) -> List[Msg]:
        goal = m.args.get("goal", "")
        simpl = math_cas.simplify_expr("sin(x)**2 + cos(x)**2", symbols=["x"])
        series = str(math_cas.series_expand("exp(I*x)", "x", about=0, order=4))
        return [
            new(
                self.name,
                "archivist",
                "result",
                "context",
                goal=goal,
                simplification=str(simpl),
                series=series,
            )
        ]
