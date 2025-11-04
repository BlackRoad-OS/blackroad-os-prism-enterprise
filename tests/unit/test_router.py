"""Unit tests for the router."""

from __future__ import annotations

import pytest

from orchestrator.exceptions import TaskNotFoundError


def test_route_treasury_task(router, task_repository, route_context, treasury_task):
    task_repository.add(treasury_task)
    route_context.approved_by = ["cfo"]
    response = router.route(treasury_task.id, "Treasury-BOT", route_context)
    assert response.ok
    assert "cash" in response.summary.lower()


def test_route_missing_task(router, route_context):
    with pytest.raises(TaskNotFoundError):
        router.route("UNKNOWN", "Treasury-BOT", route_context)
