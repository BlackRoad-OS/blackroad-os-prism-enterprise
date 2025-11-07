from typing import List
from ..proto import Msg


class Agent:
    """Base class for simple bus-connected agents."""

    name = "agent"

    def __init__(self, bus):
        self.bus = bus

    def can_handle(self, m: Msg) -> bool:
        return False

    def handle(self, m: Msg) -> List[Msg]:
        return []
