from __future__ import annotations

from typing import List

from .base import Agent
from ..proto import Msg, new
from ..tools import quantum_np as Q, viz
from ..policies import Policy
from ..llm import ToolContext, Toolformer, execute_tagged_text
from ..cache.prompt_cache import get as cache_get, put as cache_put
from ..tools.registry import default_registry


class QLM(Agent):
    """Rule-based quantum agent leveraging NumPy primitives."""

    name = "qlm"

    def __init__(self, bus, policy: Policy | None = None, registry=None):
        super().__init__(bus)
        self.policy = policy or Policy()
        self.registry = registry or default_registry()
        self.toolformer = Toolformer()
        self.ctx = ToolContext()

    def can_handle(self, m: Msg) -> bool:
        return (
            m.recipient == self.name
            and m.kind == "task"
            and m.op in {"solve_quantum", "prove_chsh", "solve_freeform", "prove_freeform"}
        )

    def handle(self, m: Msg) -> List[Msg]:
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
        if m.op in {"solve_freeform", "prove_freeform"}:
            user_prompt: str = m.args.get("prompt", "")
            hits = cache_get(user_prompt)
            if hits:
                plan_text = hits[0].plan_text
                source = "cache"
            else:
                plan = self.toolformer.generate(user_prompt)
                plan_text, source = plan.text_with_tags, plan.source
            before = set(self.ctx.artifacts)
            stitched, trace = execute_tagged_text(plan_text, self.registry, self.policy, self.ctx)
            new_artifacts = [path for path in self.ctx.artifacts if path not in before]
            cache_put(user_prompt, plan_text, artifacts=new_artifacts, source=source)
            return [
                new(
                    self.name,
                    m.sender,
                    "result",
                    m.op,
                    text=stitched,
                    trace=trace,
                    source=source,
                )
            ]
        return []
