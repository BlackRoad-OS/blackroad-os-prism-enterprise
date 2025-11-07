from __future__ import annotations

from typing import List

from .base import Agent
from ..proto import Msg, new
from ..tools import quantum_np as Q, viz


class QLM(Agent):
    """Rule-based quantum agent leveraging NumPy primitives."""

    name = "qlm"

    def can_handle(self, m: Msg) -> bool:
        return m.recipient == self.name and m.kind == "task" and m.op in {"solve_quantum", "prove_chsh"}

    def handle(self, m: Msg) -> List[Msg]:
        if m.op == "prove_chsh":
            s = Q.chsh_value_phi_plus()
            psi = Q.bell_phi_plus()
            reduced = psi.reshape(2, 2)
            rho = reduced @ reduced.conjugate().T
            bloch = (
                float(2 * rho[0, 1].real),
                float(-2 * rho[0, 1].imag),
                float((rho[0, 0] - rho[1, 1]).real),
            )
            bloch_path = viz.bloch(bloch, fname="bloch_q0.png")
            return [
                new(
                    self.name,
                    "critic",
                    "result",
                    "prove_chsh",
                    s=s,
                    bloch=bloch,
                    path=bloch_path,
                ),
                new(
                    self.name,
                    "archivist",
                    "log",
                    "qlm",
                    details={"op": "prove_chsh", "s": s},
                ),
            ]
        if m.op == "solve_quantum":
            psi = Q.bell_phi_plus()
            counts = Q.measure_counts(psi, shots=4096)
            viz.hist({"00": 0.5, "11": 0.5}, fname="bell_hist.png")
            hist_path = viz.hist(counts, fname="bell_hist_empirical.png")
            return [
                new(
                    self.name,
                    "critic",
                    "result",
                    "solve_quantum",
                    counts=counts,
                    path=hist_path,
                ),
                new(
                    self.name,
                    "archivist",
                    "log",
                    "qlm",
                    details={"op": "solve_quantum", "counts": counts},
                ),
            ]
        return []
