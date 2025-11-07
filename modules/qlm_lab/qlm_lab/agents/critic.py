"""Critic agent enforcing policy gates."""
from __future__ import annotations

from typing import List

from ..policies import chsh_within_bounds
from ..proto import Msg, new
from .base import Agent


class Critic(Agent):
    """Validate scientific and code results against thresholds."""

    name = "critic"

    def can_handle(self, m: Msg) -> bool:
        return m.recipient == self.name and m.kind == "result"

    def handle(self, m: Msg) -> List[Msg]:
        notes: List[str] = []
        ok = True
        if m.op == "prove_chsh":
            s = float(m.args.get("s", 0.0))
            ok = chsh_within_bounds(s)
            notes.append(f"CHSH={s:.3f}")
        elif m.op == "solve_quantum":
            counts = m.args.get("counts", {})
            target = 0.5
            for bit in ("00", "11"):
                prob = counts.get(bit, 0.0)
                ok = ok and abs(prob - target) < 0.1
            notes.append("Bell sample balance")
        elif m.op == "pauli_expectation":
            expectation = float(m.args.get("expectation", 0.0))
            target = float(m.args.get("target", 0.0))
            ok = abs(expectation - target) < 1e-6
            notes.append(f"⟨ZZ⟩={expectation:.3f}")
        return [
            new(
                self.name,
                "archivist",
                "critique",
                m.op,
                ok=ok,
                notes=notes,
                source=m.sender,
            )
        ]
