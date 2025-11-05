"""Task routing and bot execution."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Mapping, Sequence

from orchestrator.base import BaseBot
from orchestrator.exceptions import BotNotRegisteredError, TaskNotFoundError
from orchestrator.lineage import LineageTracker
from orchestrator.memory import MemoryLog
from orchestrator.policy import PolicyEngine
from orchestrator.protocols import BotResponse, Task, TaskPriority


class BotRegistry:
    """Registry of available bots."""

    def __init__(self) -> None:
        self._bots: Dict[str, BaseBot] = {}

    def register(self, bot: BaseBot) -> None:
        self._bots[bot.metadata.name] = bot

    def get(self, name: str) -> BaseBot:
        try:
            return self._bots[name]
        except KeyError as exc:
            raise BotNotRegisteredError(f"Bot '{name}' is not registered") from exc

    def list(self) -> Sequence[BaseBot]:
        return tuple(self._bots.values())


class TaskRepository:
    """File-backed store for tasks."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({}), encoding="utf-8")

    def _load(self) -> Dict[str, dict[str, object]]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: Mapping[str, dict[str, object]]) -> None:
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
        due_value = payload.get("due_date")
        return Task(
            id=payload["id"],
            goal=payload["goal"],
            owner=payload["owner"],
            priority=TaskPriority(payload["priority"]),
            created_at=datetime.fromisoformat(payload["created_at"]),
            due_date=datetime.fromisoformat(due_value) if due_value else None,
            tags=tuple(payload.get("tags", [])),
            metadata=dict(payload.get("metadata", {})),
            config=dict(payload.get("config", {})),
        )

    def list(self) -> Sequence[Task]:
        data = self._load()
        tasks = []
        for payload in data.values():
            due_value = payload.get("due_date")
            tasks.append(
                Task(
                    id=payload["id"],
                    goal=payload["goal"],
                    owner=payload["owner"],
                    priority=TaskPriority(payload["priority"]),
                    created_at=datetime.fromisoformat(payload["created_at"]),
                    due_date=datetime.fromisoformat(due_value) if due_value else None,
                    tags=tuple(payload.get("tags", [])),
                    metadata=dict(payload.get("metadata", {})),
                    config=dict(payload.get("config", {})),
                )
            )
        return tasks


@dataclass(slots=True)
class RouteContext:
    """Context for routing operations."""

    policy_engine: PolicyEngine
    memory: MemoryLog
    lineage: LineageTracker
    config: Mapping[str, object] = None
    approved_by: Sequence[str] | None = None


class Router:
    """Orchestrates task routing to bots."""

    def __init__(self, registry: BotRegistry, repository: TaskRepository):
        self.registry = registry
        self.repository = repository

    def route(self, task_id: str, bot_name: str, context: RouteContext) -> BotResponse:
        task = self.repository.get(task_id)
        # Merge context config into task config if provided
        if context.config:
            task.config = dict(context.config)
        bot = self.registry.get(bot_name)
        context.policy_engine.enforce(bot_name, context.approved_by)
        response = bot.run(task)
        context.memory.append(task, bot.metadata.name, response)
        context.lineage.record(task, bot.metadata.name, response)
        return response
"""Routing helpers for executing tasks with bots."""

from __future__ import annotations

from typing import List

from .metrics import log_metric
from .protocols import BotExecutionError, Task


def dependencies_met(task: Task, tasks: List[Task]) -> bool:
    done_ids = {t.id for t in tasks if t.status == "done"}
    return all(dep in done_ids for dep in task.depends_on)


def route_task(task: Task, tasks: List[Task]) -> None:
    from bots import BOT_REGISTRY

    if not dependencies_met(task, tasks):
        log_metric("dependency_block", task.id)
        raise BotExecutionError("dependencies_not_met")

    bot = BOT_REGISTRY.get(task.bot)
    if bot is None:
        raise BotExecutionError("bot_not_found")

    bot.run(task)
    task.status = "done"
    log_metric("scheduled_run", task.id)

