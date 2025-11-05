"""Base classes for bot implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from orchestrator.protocols import BotResponse, Task


@dataclass(slots=True)
class BotMetadata:
    """Structured metadata describing bot responsibilities."""

    name: str
    mission: str
    inputs: Sequence[str]
    outputs: Sequence[str]
    kpis: Sequence[str]
    guardrails: Sequence[str]
    handoffs: Sequence[str]
    tags: Sequence[str] = field(default_factory=tuple)


class BaseBot(ABC):
    """Abstract base class for all bots."""

    metadata: BotMetadata

    def __init__(self) -> None:
        if not hasattr(self, "metadata"):
            raise ValueError("Bots must define metadata of type BotMetadata")

    @abstractmethod
    def handle_task(self, task: Task) -> BotResponse:
        """Execute the task and return a structured response."""

    def run(self, task: Task) -> BotResponse:
        """Wrapper around :meth:`handle_task` for future instrumentation."""

        return self.handle_task(task)

    def describe(self) -> Mapping[str, Sequence[str]]:
        """Return human-readable metadata about the bot."""

        return {
            "mission": [self.metadata.mission],
            "inputs": list(self.metadata.inputs),
            "outputs": list(self.metadata.outputs),
            "kpis": list(self.metadata.kpis),
            "guardrails": list(self.metadata.guardrails),
            "handoffs": list(self.metadata.handoffs),
            "tags": list(self.metadata.tags),
        }
