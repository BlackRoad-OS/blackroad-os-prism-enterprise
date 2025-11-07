"""Simple rule-based planner agent."""
from __future__ import annotations

from typing import List

from ..proto import Msg, new
from .base import Agent


class Planner(Agent):
    """Dispatch follow-up tasks to specialist agents."""

    name = "planner"

    def can_handle(self, m: Msg) -> bool:
        return m.recipient == self.name and m.kind == "task" and m.op == "start"

    def handle(self, m: Msg) -> List[Msg]:
        goal = m.args.get("goal", "")
        return [
            new(self.name, "researcher", "task", "gather_context", goal=goal),
            new(self.name, "qlm", "task", "prove_chsh"),
            new(self.name, "qlm", "task", "solve_quantum"),
            new(self.name, "coder", "task", "implement_pauli"),
        ]
