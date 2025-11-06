"""Bot registry helpers for the Prism Console orchestrator."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Dict, Sequence

from orchestrator import BotRegistry
from orchestrator.protocols import BaseBot

from .close_bot import CloseBot
from .sop_bot import SopBot
from .treasury_bot import TreasuryBot

__all__ = ["build_registry", "list_bots", "BOT_REGISTRY"]

BOT_REGISTRY: Dict[str, BaseBot] = {}


def build_registry() -> BotRegistry:
    """Instantiate all known bots and register them with the orchestrator."""

    registry = BotRegistry()
    for bot_cls in (TreasuryBot, CloseBot, SopBot):
        registry.register(bot_cls())
    for bot in BOT_REGISTRY.values():
        registry.register(bot)
    return registry


def list_bots() -> Sequence[str]:
    """Return the names of every registered bot."""

    registry = build_registry()
    return [bot.metadata.name for bot in registry.list()]


def _discover() -> None:
    """Auto-discover any additional bots defined in this package."""

    pkg_path = Path(__file__).parent
    for module_path in pkg_path.glob("*_bot.py"):
        module = import_module(f"bots.{module_path.stem}")
        bot_cls = getattr(module, "Bot", None)
        if bot_cls is None:
            continue
        bot: BaseBot = bot_cls()
        BOT_REGISTRY[bot.NAME] = bot


_discover()
