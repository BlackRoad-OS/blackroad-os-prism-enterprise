"""Shared typing contracts for Prism Console bots and tasks."""
"""Core data structures shared across orchestrator components."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Protocol, Sequence, runtime_checkable
from typing import Any, Dict, List, Mapping, MutableMapping, Optional, Sequence


class TaskPriority(str, Enum):
    """Prioritisation levels supported by the orchestrator."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(slots=True)
class Task:
    """Normalised representation of a unit of work handled by bots."""

    id: str
    goal: str
    owner: Optional[str] = None
    """Normalised task representation used by bots and the router."""

    id: str
    goal: str
    bot: str = ""
    owner: str = ""
    priority: TaskPriority | str = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    tags: Sequence[str] = field(default_factory=tuple)
    metadata: MutableMapping[str, Any] | None = None
    config: MutableMapping[str, Any] | None = None
    bot: Optional[str] = None
    context: MutableMapping[str, Any] | None = None
    status: str = "pending"
    depends_on: Sequence[str] = field(default_factory=tuple)
    metadata: MutableMapping[str, Any] = field(default_factory=dict)
    config: Mapping[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    depends_on: List[str] = field(default_factory=list)
    scheduled_for: Optional[datetime] = None

    def __post_init__(self) -> None:
        if isinstance(self.priority, str):
            self.priority = TaskPriority(self.priority.lower())
        if self.metadata is None:
            self.metadata = {}
        if self.config is None:
            self.config = {}
        if self.context is None:
            self.context = {}
        self.tags = tuple(self.tags)
        self.depends_on = tuple(self.depends_on)
        if not isinstance(self.tags, tuple):
            self.tags = tuple(self.tags)
        if not isinstance(self.metadata, MutableMapping):
            self.metadata = dict(self.metadata)
        if not isinstance(self.config, Mapping):
            self.config = dict(self.config)
        if not isinstance(self.context, dict):
            self.context = dict(self.context)
        if not isinstance(self.depends_on, list):
            self.depends_on = list(self.depends_on)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the task for persistence or transport."""

        payload: Dict[str, Any] = {
            "id": self.id,
            "goal": self.goal,
            "bot": self.bot,
            "owner": self.owner,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
            "config": dict(self.config),
            "context": dict(self.context),
            "status": self.status,
            "depends_on": list(self.depends_on),
        }
        if self.due_date:
            payload["due_date"] = self.due_date.isoformat()
        if self.scheduled_for:
            payload["scheduled_for"] = self.scheduled_for.isoformat()
        if self.bot:
            payload["bot"] = self.bot
        if self.context:
            payload["context"] = dict(self.context)
        return payload


@dataclass(slots=True)
class BotResponse:
    """Structured response returned by bots."""

    task_id: str
    summary: str
    steps: Sequence[str]
    data: Mapping[str, Any]
    risks: Sequence[str]
    artifacts: Sequence[str]
    next_actions: Sequence[str]
    ok: bool = True
    metrics: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON serialisable representation of the response."""

        return {
            "task_id": self.task_id,
            "summary": self.summary,
            "steps": list(self.steps),
            "data": dict(self.data),
            "risks": list(self.risks),
            "artifacts": list(self.artifacts),
            "next_actions": list(self.next_actions),
            "ok": self.ok,
            "metrics": dict(self.metrics),
        }


@dataclass(slots=True)
class MemoryRecord:
    """Entry stored in the append-only audit log."""

    timestamp: datetime
    task: Task
    bot: str
    response: BotResponse
    signature: str
    previous_hash: Optional[str]
    hash: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the record for JSON logging."""

        return {
            "timestamp": self.timestamp.isoformat(),
            "task": self.task.to_dict(),
            "bot": self.bot,
            "response": self.response.to_dict(),
            "signature": self.signature,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
        }


class BotExecutionError(Exception):
    """Raised when a bot cannot execute a task."""

    def __init__(self, reason: str, details: Any | None = None):
        super().__init__(reason)
        self.reason = reason
        self.details = details


@runtime_checkable
class BaseBot(Protocol):
    """Protocol describing the runtime contract for bots."""

    NAME: str
    SUPPORTED_TASKS: List[str]

    def run(self, task: Task) -> Any:  # pragma: no cover - implementation specific
        ...
__all__ = [
    "TaskPriority",
    "Task",
    "BotResponse",
    "MemoryRecord",
    "BotExecutionError",
]
