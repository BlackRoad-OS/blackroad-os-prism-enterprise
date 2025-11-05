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
"""Bot registry and auto-discovery."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Dict

from orchestrator.protocols import BaseBot

BOT_REGISTRY: Dict[str, BaseBot] = {}


def _discover() -> None:
    pkg_path = Path(__file__).parent
    for mod in pkg_path.glob("*_bot.py"):
        module = import_module(f"bots.{mod.stem}")
        bot_cls = getattr(module, "Bot", None)
        if bot_cls is None:
            continue
        bot: BaseBot = bot_cls()
        BOT_REGISTRY[bot.NAME] = bot


_discover()

__all__ = ["BOT_REGISTRY"]

