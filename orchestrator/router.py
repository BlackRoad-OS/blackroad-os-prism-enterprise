"""Task routing, persistence, and scheduling helpers."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .base import BaseBot
from .exceptions import BotNotRegisteredError, TaskNotFoundError
from .lineage import LineageTracker
from .memory import MemoryLog
from .metrics import log_metric
from .policy import PolicyEngine
from .protocols import BotExecutionError, BotResponse, Task


class BotRegistry:
    """Registry of available bots."""

    def __init__(self) -> None:
        self._bots: Dict[str, BaseBot] = {}

    def register(self, bot: BaseBot) -> None:
        self._bots[bot.metadata.name] = bot

    def get(self, name: str) -> BaseBot:
        try:
            return self._bots[name]
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise BotNotRegisteredError(f"Bot '{name}' is not registered") from exc

    def list(self) -> Sequence[BaseBot]:
        return tuple(self._bots.values())


class TaskRepository:
    """Simple file-backed store for tasks."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({})

    def _load(self) -> Dict[str, Dict[str, Any]]:
        data = self.path.read_text(encoding="utf-8") if self.path.exists() else ""
        if not data.strip():
            return {}
        return json.loads(data)

    def _save(self, data: Mapping[str, Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add(self, task: Task) -> None:
        data = self._load()
        data[task.id] = task.to_dict()
        self._save(data)

    def get(self, task_id: str) -> Task:
        data = self._load()
        payload = data.get(task_id)
        if not payload:
            raise TaskNotFoundError(f"Task '{task_id}' not found")
        return Task(**payload)

    def list(self) -> Sequence[Task]:
        data = self._load()
        return tuple(Task(**payload) for payload in data.values())

    def update(self, task: Task) -> None:
        data = self._load()
        if task.id not in data:
            raise TaskNotFoundError(f"Task '{task.id}' not found")
        data[task.id] = task.to_dict()
        self._save(data)


@dataclass(slots=True)
class RouteContext:
    """Context for routing operations."""

    policy_engine: PolicyEngine
    memory: MemoryLog
    lineage: LineageTracker
    config: Mapping[str, object] | None = None
    approved_by: Sequence[str] | None = None


class Router:
    """Orchestrates task routing to bots."""

    def __init__(self, registry: BotRegistry, repository: TaskRepository):
        self.registry = registry
        self.repository = repository

    def route(self, task_id: str, bot_name: str, context: RouteContext) -> BotResponse:
        task = self.repository.get(task_id)
        if context.config:
            merged_config: Dict[str, Any] = copy.deepcopy(context.config)
            merged_config.update(task.config)
            task.config = merged_config
        bot = self.registry.get(bot_name)
        context.policy_engine.enforce(bot_name, context.approved_by)
        response = bot.run(task)
        task.status = "done" if response.ok else "failed"
        self.repository.update(task)
        context.memory.append(task, bot.metadata.name, response)
        context.lineage.record(task, bot.metadata.name, response)
        return response


def dependencies_met(task: Task, tasks: Sequence[Task]) -> bool:
    """Check whether a task's dependencies are satisfied."""

    done_ids = {t.id for t in tasks if t.status == "done"}
    return all(dep in done_ids for dep in task.depends_on)


def route_task(task: Task, tasks: Sequence[Task]) -> None:
    """Route an individual scheduled task using the global bot registry."""

    from bots import BOT_REGISTRY  # Imported lazily to avoid circular dependency

    if not dependencies_met(task, tasks):
        log_metric("dependency_block", task.id)
        raise BotExecutionError("dependencies_not_met")

    bot = BOT_REGISTRY.get(task.bot or "")
    if bot is None:
        log_metric("bot_not_found", task.id)
        raise BotExecutionError("bot_not_found")

    bot.run(task)
    task.status = "done"
    log_metric("scheduled_run", task.id)


__all__ = [
    "BotRegistry",
    "TaskRepository",
    "RouteContext",
    "Router",
    "dependencies_met",
    "route_task",
]
