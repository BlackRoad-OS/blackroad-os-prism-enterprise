from __future__ import annotations

from typing import List

from .base import Agent
from ..llm.providers import NullLLM
from ..llm.runtime import ToolContext, execute_tagged_text
from ..policies import Policy
from ..proto import Msg, new
from ..tools import quantum_np as Q, viz
from ..tools.registry import default_registry


class QLM(Agent):
    """Quantum laboratory agent capable of rule-based and tool-called flows."""

    name = "qlm"

    def __init__(self, bus, policy: Policy | None = None):
        super().__init__(bus)
        self.policy = policy or Policy()
        self.llm = NullLLM()
        self.registry = default_registry()
        self.ctx = ToolContext()

    def can_handle(self, m: Msg) -> bool:
        supported = {"solve_quantum", "prove_chsh", "solve_quantum_llm", "prove_chsh_llm"}
        return m.recipient == self.name and m.kind == "task" and m.op in supported

    def _run_llm_plan(self, plan: str, sender: str, op: str) -> List[Msg]:
        text_with_tags = self.llm.run(plan, self.policy)
        stitched, trace = execute_tagged_text(text_with_tags, self.registry, self.policy, self.ctx)
        return [new(self.name, sender, "result", op, text=stitched, trace=trace)]

    def handle(self, m: Msg) -> List[Msg]:
        if m.op == "prove_chsh_llm":
            plan = '''
Compute CHSH for |Φ+> and verify violation:
<tool name="quantum_np.chsh_value_phi_plus" as="S"/>
Plot an ideal Bell histogram (00/11):
<tool name="viz.hist" args="{\"00\":0.5,\"11\":0.5}" fname="bell_hist_toolcaller.png" as="hist_path"/>
'''
            return self._run_llm_plan(plan, m.sender, m.op)

        if m.op == "solve_quantum_llm":
            plan = '''
Prepare Bell and measure 4096 shots with a plot:
<tool name="quantum_np.bell_phi_plus" as="psi"/>
<tool name="quantum_np.measure_counts" from="psi" shots="4096" as="counts"/>
<tool name="viz.hist" from="counts" fname="bell_hist_empirical_toolcaller.png" as="hist_path"/>
'''
            return self._run_llm_plan(plan, m.sender, m.op)

        if m.op == "prove_chsh":
            s = Q.chsh_value_phi_plus()
            psi = Q.bell_phi_plus()
            reduced = psi.reshape(2, 2)
            rho = reduced @ reduced.conjugate().T
            bloch = (0.0, 0.0, 0.0)
            try:
                bloch = (
                    float(2 * rho[0, 1].real),
                    float(-2 * rho[0, 1].imag),
                    float((rho[0, 0] - rho[1, 1]).real),
                )
            except Exception:  # pragma: no cover - defensive
                pass
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
                )
            ]

        if m.op == "solve_quantum":
            psi = Q.bell_phi_plus()
            counts = Q.measure_counts(psi, shots=4096)
            hist_path = viz.hist(counts, fname="bell_hist_empirical.png")
            return [
                new(
                    self.name,
                    "critic",
                    "result",
                    "solve_quantum",
                    counts=counts,
                    path=hist_path,
                )
            ]

        return []
