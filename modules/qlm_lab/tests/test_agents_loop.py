from __future__ import annotations

from pathlib import Path

import pytest

from qlm_lab.agents.orchestrator import Orchestrator
from qlm_lab.lineage import LineageLogger


def test_orchestrator_executes_workflow(tmp_path: Path):
    logger = LineageLogger(path=tmp_path / "lineage.jsonl")
    orchestrator = Orchestrator(logger=logger)
    results = orchestrator.run("verify bell state", message_budget=64)
    assert any(msg.op == "solve_quantum" for msg in results)
    assert logger.path.exists()
    log_lines = logger.path.read_text().strip().splitlines()
    assert log_lines, "lineage log should not be empty"


def test_orchestrator_budget_guard(tmp_path: Path):
    logger = LineageLogger(path=tmp_path / "lineage.jsonl")
    orchestrator = Orchestrator(logger=logger)
    with pytest.raises(RuntimeError):
        orchestrator.run("unreachable", message_budget=0)
