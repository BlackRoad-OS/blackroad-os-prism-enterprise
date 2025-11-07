"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:  # pragma: no cover - import-time typing only
    from bots import build_registry as BuildRegistryFunc
    from orchestrator import (
        LineageTracker,
        MemoryLog,
        PolicyEngine,
        RouteContext,
        Router,
        SecRule2042Gate,
        Task,
        TaskPriority,
        TaskRepository,
    )


def _load_orchestrator_modules():
    try:
        from bots import build_registry  # type: ignore
        from orchestrator import (  # type: ignore
            LineageTracker,
            MemoryLog,
            PolicyEngine,
            RouteContext,
            Router,
            SecRule2042Gate,
            Task,
            TaskPriority,
            TaskRepository,
        )
    except Exception as exc:  # pragma: no cover - infrastructure guard
        pytest.skip(f"orchestrator stack unavailable: {exc}")
    return (
        build_registry,
        LineageTracker,
        MemoryLog,
        PolicyEngine,
        RouteContext,
        Router,
        SecRule2042Gate,
        Task,
        TaskPriority,
        TaskRepository,
    )


@pytest.fixture()
def task_repository(tmp_path: Path) -> TaskRepository:
    _, _, _, _, _, _, _, _, _, TaskRepository = _load_orchestrator_modules()
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
    _, _, _, PolicyEngine, _, _, _, _, _, _ = _load_orchestrator_modules()
    return PolicyEngine.from_file(policy_file)


@pytest.fixture()
def route_context(tmp_path: Path, policy_engine: PolicyEngine) -> RouteContext:
    _, LineageTracker, MemoryLog, _, RouteContext, _, SecRule2042Gate, _, _, _ = _load_orchestrator_modules()
    memory = MemoryLog(tmp_path / "memory.jsonl")
    lineage = LineageTracker(tmp_path / "lineage.jsonl")
    sec_gate = SecRule2042Gate()
    return RouteContext(
        policy_engine=policy_engine,
        memory=memory,
        lineage=lineage,
        approved_by=[],
        sec_gate=sec_gate,
    )


@pytest.fixture()
def router(task_repository: TaskRepository) -> Router:
    build_registry, _, _, _, _, Router, _, _, _, _ = _load_orchestrator_modules()
    registry = build_registry()
    return Router(registry=registry, repository=task_repository)


@pytest.fixture()
def treasury_task() -> Task:
    _, _, _, _, _, _, _, Task, TaskPriority, _ = _load_orchestrator_modules()
    return Task(
        id="TSK-TEST",
        goal="Build 13-week cash forecast",
        owner="finance.ops",
        priority=TaskPriority.HIGH,
        created_at=datetime.utcnow(),
        tags=("treasury",),
        metadata={"region": "NA"},
    )
