"""Task routing, persistence, and scheduling helpers."""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

from .exceptions import BotNotRegisteredError, TaskNotFoundError
from .lineage import LineageTracker
from .memory import MemoryLog
from .metrics import log_metric
from .policy import PolicyEngine
from .protocols import BotExecutionError, BotResponse, Task, TaskPriority
from .protocols import BotExecutionError, BotResponse, Task, TaskPriority, BaseBot
from .sec import SecRule2042Gate


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


def _parse_datetime(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


class TaskRepository:
    """Simple file-backed store for tasks."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._save({})

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if not self.path.exists():
        try:
            data = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}
        contents = self.path.read_text(encoding="utf-8").strip()
        if not contents:
            return {}
        return json.loads(contents)

    def _save(self, data: Mapping[str, Dict[str, Any]]) -> None:
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add(self, task: Task) -> None:
        data = self._load()
        data[task.id] = task.to_dict()
        self._save(data)

    def update(self, task: Task) -> None:
        data = self._load()
        if task.id not in data:
            raise TaskNotFoundError(f"Task '{task.id}' not found")
        data[task.id] = task.to_dict()
        self._save(data)

    def get(self, task_id: str) -> Task:
        payload = self._load().get(task_id)
        if payload is None:
            raise TaskNotFoundError(f"Task '{task_id}' not found")
        return self._task_from_payload(payload)

    def list(self) -> Sequence[Task]:
        return [self._task_from_payload(payload) for payload in self._load().values()]

    @staticmethod
    def _task_from_payload(payload: Mapping[str, Any]) -> Task:
        return Task(
            id=str(payload["id"]),
            goal=str(payload["goal"]),
            bot=str(payload.get("bot", "")),
            owner=payload.get("owner"),
            priority=priority_value,
            created_at=str(payload.get("created_at", datetime.utcnow().isoformat())),
            due_date=str(due_value) if due_value else None,
            priority=payload.get("priority", TaskPriority.MEDIUM.value),
            created_at=datetime.fromisoformat(str(payload["created_at"])),
            due_date=_parse_datetime(payload.get("due_date")),
            tags=tuple(payload.get("tags", [])),
            metadata=dict(payload.get("metadata", {})),
            config=dict(payload.get("config", {})),
            context=dict(payload.get("context", {})),
            status=str(payload.get("status", "pending")),
            depends_on=tuple(payload.get("depends_on", [])),
            scheduled_for=str(scheduled_value) if scheduled_value else None,
        )

    def add(self, task: Task) -> None:
        data = self._load()
        data[task.id] = task.to_dict()
        self._save(data)

    def update(self, task: Task) -> None:
        data = self._load()
        if task.id not in data:
            raise TaskNotFoundError(f"Task '{task.id}' not found")
        data[task.id] = task.to_dict()
        self._save(data)

    def get(self, task_id: str) -> Task:
        data = self._load()
        payload = data.get(task_id)
        if payload is None:
            raise TaskNotFoundError(f"Task '{task_id}' not found")
        return self._task_from_payload(payload)

    def list(self) -> Sequence[Task]:
        return tuple(self._task_from_payload(payload) for payload in self._load().values())

            scheduled_for=_parse_datetime(payload.get("scheduled_for")),
        )


@dataclass(slots=True)
class RouteContext:
    """Context for routing operations."""

    policy_engine: PolicyEngine
    memory: MemoryLog
    lineage: LineageTracker
    config: Mapping[str, object] | None = None
    approved_by: Sequence[str] | None = None
    sec_gate: SecRule2042Gate | None = None


class Router:
    """Orchestrates task routing to bots."""

    def __init__(self, registry: BotRegistry, repository: TaskRepository) -> None:
        self.registry = registry
        self.repository = repository

    def route(self, task_id: str, bot_name: str, context: RouteContext) -> BotResponse:
        task = self.repository.get(task_id)

        if context.config:
            merged_config: Dict[str, Any] = copy.deepcopy(task.config)
            merged_config.update(context.config)
            task.config = merged_config
            merged_config: Dict[str, Any] = copy.deepcopy(context.config)
            merged_config.update(task.config or {})
            task.config = merged_config

        if context.sec_gate is not None:
            context.sec_gate.enforce(task)

        bot = self.registry.get(bot_name)
        context.policy_engine.enforce(bot_name, context.approved_by)

        response = bot.run(task)
        task.status = "done" if getattr(response, "ok", False) else "failed"
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

    response = bot.run(task)
    if isinstance(response, BotResponse):
        task.status = "done" if response.ok else task.status
    else:  # pragma: no cover - legacy bot fallback
        task.status = "done"


__all__ = [
    "BotRegistry",
    "TaskRepository",
    "RouteContext",
    "Router",
    "dependencies_met",
    "route_task",
]
