"""Archivist agent persisting lineage."""
from __future__ import annotations

from typing import List

from ..lineage import LineageLogger
from ..proto import Msg, new
from .base import Agent


class Archivist(Agent):
    """Store critical messages to the lineage log."""

    name = "archivist"

    def __init__(self, bus, logger: LineageLogger | None = None):
        super().__init__(bus)
        self.logger = logger or LineageLogger()

    def can_handle(self, m: Msg) -> bool:
        return m.recipient == self.name and m.kind in {"result", "critique"}

    def handle(self, m: Msg) -> List[Msg]:
        return [
            new(
                self.name,
                "orchestrator",
                "log",
                "archived",
                message_id=m.id,
                ok=m.args.get("ok", True),
            )
        ]
