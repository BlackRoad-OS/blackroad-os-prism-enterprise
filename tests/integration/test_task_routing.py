"""Integration tests for task routing."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from bots import build_registry
from orchestrator import (
    LineageTracker,
    MemoryLog,
    PolicyEngine,
    RouteContext,
    Router,
    Task,
    TaskPriority,
    TaskRepository,
)


def _write_policy(path: Path) -> None:
    path.write_text(
        """
policies:
  treasury-bot:
    requires_approval: true
    approvers: [cfo]
"""
    )


def test_route_records_memory_and_lineage(tmp_path: Path) -> None:
    task = Task(
        id="TSK-INTEG",
        goal="Build 13-week cash forecast",
        owner="finance",
        priority=TaskPriority.HIGH,
        created_at=datetime.utcnow(),
    )
    repository = TaskRepository(tmp_path / "tasks.json")
    repository.add(task)
    router = Router(build_registry(), repository)
    approvals = tmp_path / "approvals.yaml"
    _write_policy(approvals)
    context = RouteContext(
        policy_engine=PolicyEngine.from_file(approvals),
        memory=MemoryLog(tmp_path / "memory.jsonl"),
        lineage=LineageTracker(tmp_path / "lineage.jsonl"),
        approved_by=["cfo"],
    )
    response = router.route(task.id, "Treasury-BOT", context)
    assert response.ok
    tail = context.memory.tail(1)
    assert tail and tail[0]["task"]["id"] == task.id
    assert context.lineage.events()
