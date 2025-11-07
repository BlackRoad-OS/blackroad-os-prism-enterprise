"""Orchestrator wiring planner, quantum, and critic agents."""
from __future__ import annotations

from typing import Dict, List

from ..bus import Bus
from ..lineage import LineageLogger
from ..proto import Msg, new
from .archivist import Archivist
from .base import Agent
from .coder import Coder
from .critic import Critic
from .planner import Planner
from .qlm import QLM
from .researcher import Researcher


class Orchestrator:
    """Event-loop driving the rule-based agents on an in-memory bus."""

    name = "orchestrator"

    def __init__(self, bus: Bus | None = None, logger: LineageLogger | None = None):
        self.bus = bus or Bus()
        self.logger = logger or LineageLogger()
        self.message_budget = 0
        self.results: List[Msg] = []
        self.agent_map: Dict[str, Agent] = {}
        self.bus.subscribe(self._on_message)
        self._register_default_agents()

    def _register_default_agents(self) -> None:
        agents: List[Agent] = [
            Planner(self.bus),
            Researcher(self.bus),
            QLM(self.bus),
            Coder(self.bus),
            Critic(self.bus),
            Archivist(self.bus, logger=self.logger),
        ]
        for agent in agents:
            self.agent_map[agent.name] = agent

    def _send(self, message: Msg) -> None:
        if self.message_budget <= 0:
            raise RuntimeError("Message budget exhausted")
        self.message_budget -= 1
        self.bus.publish(message)

    def _on_message(self, message: Msg) -> None:
        self.logger.log(message, note=f"bus:{message.kind}:{message.op}")
        if message.kind == "result":
            self.results.append(message)
        target = self.agent_map.get(message.recipient)
        if not target:
            return
        if not target.can_handle(message):
            return
        responses = target.handle(message)
        for response in responses:
            self._send(response)

    def run(self, goal: str, message_budget: int = 32) -> List[Msg]:
        """Execute the workflow for ``goal`` and return result messages."""

        self.results.clear()
        self.message_budget = message_budget
        self._send(new(self.name, "planner", "task", "start", goal=goal))
        return list(self.results)


__all__ = ["Orchestrator"]
