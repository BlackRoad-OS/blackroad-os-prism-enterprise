"""Core data structures for the Prism orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence


class TaskPriority(str, Enum):
    """Prioritisation levels supported by the orchestrator."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(slots=True)
class Task:
    """Normalized task representation."""

    id: str
    goal: str
    owner: str
    priority: TaskPriority
    created_at: datetime
    due_date: Optional[datetime] = None
    tags: Sequence[str] = field(default_factory=tuple)
    metadata: MutableMapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a serialisable dictionary."""

        payload: Dict[str, Any] = {
            "id": self.id,
            "goal": self.goal,
            "owner": self.owner,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "tags": list(self.tags),
            "metadata": dict(self.metadata),
        }
        if self.due_date:
            payload["due_date"] = self.due_date.isoformat()
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
