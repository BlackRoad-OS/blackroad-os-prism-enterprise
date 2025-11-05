"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

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


@pytest.fixture()
def task_repository(tmp_path: Path) -> TaskRepository:
    return TaskRepository(tmp_path / "tasks.json")


@pytest.fixture()
def policy_file(tmp_path: Path) -> Path:
    approvals = tmp_path / "approvals.yaml"
    approvals.write_text(
        """
policies:
  treasury-bot:
    requires_approval: true
    approvers: [cfo]
  close-bot:
    requires_approval: false
  s&op-bot:
    requires_approval: false
"""
    )
    return approvals


@pytest.fixture()
def policy_engine(policy_file: Path) -> PolicyEngine:
    return PolicyEngine.from_file(policy_file)


@pytest.fixture()
def route_context(tmp_path: Path, policy_engine: PolicyEngine) -> RouteContext:
    memory = MemoryLog(tmp_path / "memory.jsonl")
    lineage = LineageTracker(tmp_path / "lineage.jsonl")
    return RouteContext(policy_engine=policy_engine, memory=memory, lineage=lineage, approved_by=[])


@pytest.fixture()
def router(task_repository: TaskRepository) -> Router:
    registry = build_registry()
    return Router(registry=registry, repository=task_repository)


@pytest.fixture()
def treasury_task() -> Task:
    return Task(
        id="TSK-TEST",
        goal="Build 13-week cash forecast",
        owner="finance.ops",
        priority=TaskPriority.HIGH,
        created_at=datetime.utcnow(),
        tags=("treasury",),
        metadata={"region": "NA"},
    )
