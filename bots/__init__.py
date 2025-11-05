"""Bot registry for Prism Console."""

from __future__ import annotations

from typing import Sequence

from orchestrator import BotRegistry

from .close_bot import CloseBot
from .sop_bot import SopBot
from .treasury_bot import TreasuryBot


def build_registry() -> BotRegistry:
    """Instantiate all bots and register them."""

    registry = BotRegistry()
    for bot_cls in (TreasuryBot, CloseBot, SopBot):
        registry.register(bot_cls())
    return registry


def list_bots() -> Sequence[str]:
    """Return the names of all registered bots."""

    registry = build_registry()
    return [bot.metadata.name for bot in registry.list()]
