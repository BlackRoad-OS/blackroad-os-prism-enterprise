"""Bot registry helpers for the Prism Console orchestrator."""
"""Bot registry and auto-discovery utilities."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Dict, Sequence

from orchestrator import BotRegistry
from orchestrator.protocols import BaseBot
from typing import Dict, Iterable, Iterator, Sequence, Tuple

from orchestrator import BaseBot, BotRegistry

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
BOT_REGISTRY: Dict[str, BaseBot | object] = {}


def _iter_bot_modules() -> Iterable[str]:
    """Yield module names for all bot implementations."""

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
    package_path = Path(__file__).resolve().parent
    for module_path in package_path.glob("*_bot.py"):
        if module_path.name == "simple.py":
            # ``simple.py`` hosts helpers used in fixtures rather than a bot.
            continue
        yield module_path.stem


def _instantiate_bots(module_name: str) -> Iterator[Tuple[str, BaseBot | object]]:
    """Instantiate bots from the provided module name."""

    module = import_module(f"bots.{module_name}")

    # 1. Explicit ``Bot`` export used by lightweight script-style bots.
    bot_cls = getattr(module, "Bot", None)
    if bot_cls is not None:
        bot = bot_cls()
        name = getattr(bot, "NAME", bot_cls.__name__)
        yield name, bot

    # 2. ``BaseBot`` subclasses with metadata for richer orchestration.
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if not isinstance(attr, type):
            continue
        if not issubclass(attr, BaseBot) or attr is BaseBot:
            continue
        bot_instance = attr()
        yield bot_instance.metadata.name, bot_instance


def _discover() -> None:
    for module_name in _iter_bot_modules():
        for name, bot in _instantiate_bots(module_name):
            BOT_REGISTRY[name] = bot


_discover()


def build_registry() -> BotRegistry:
    """Instantiate a :class:`BotRegistry` populated with discovered bots."""

    registry = BotRegistry()
    for bot in BOT_REGISTRY.values():
        if isinstance(bot, BaseBot):
            registry.register(bot)
    return registry


def list_bots() -> Sequence[str]:
    """Return the sorted list of discovered bot names."""

    return sorted(BOT_REGISTRY)


__all__ = ["BOT_REGISTRY", "build_registry", "list_bots"]
