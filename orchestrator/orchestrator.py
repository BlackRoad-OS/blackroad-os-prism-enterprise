import inspect
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Type

from bots import available_bots
from finance import costing
from tools import storage

from .base import BaseBot, assert_guardrails
from .protocols import BotResponse, Task
from .protocols import Task, BotResponse
from .base import BaseBot, assert_guardrails
from tools import storage
from bots import available_bots

_memory_path = Path(__file__).resolve().with_name("memory.jsonl")
_current_doc = ""


def red_team(response: BotResponse) -> None:
    """Basic red team checks on a response."""
    if not response.summary.strip():
        raise AssertionError("Summary missing")
    if not response.risks:
        raise AssertionError("Risks required")
    if "KPIS" in _current_doc.upper() and "KPI" not in response.summary.upper():
        raise AssertionError("KPIs not referenced")


def route(task: Task, bot_name: str) -> BotResponse:
    """Route a task to the named bot and log the interaction."""
    registry: Dict[str, Type[BaseBot]] = available_bots()
    if bot_name not in registry:
        raise ValueError(f"Unknown bot: {bot_name}")
    bot = registry[bot_name]()

    global _current_doc
    _current_doc = inspect.getdoc(bot) or ""

    response = bot.run(task)
    assert_guardrails(response)
    red_team(response)

    record = {
        "ts": datetime.utcnow().isoformat(),
        "task": task.model_dump(mode="json"),
        "bot": bot_name,
        "response": response.model_dump(mode="json"),
    }
    storage.write(str(_memory_path), record)
    costing.log(bot_name, user=os.getenv("PRISM_USER"), tenant=os.getenv("PRISM_TENANT"))
    return response
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from config.settings import settings
from tools.storage import write_json, write_text

from .base import BotResponse, Task
from .errors import BotExecutionError
from .logging import log
from .metrics import record
from .registry import get


def create_task(goal: str, context: dict | None = None) -> Task:
    task = Task(id=str(uuid4()), goal=goal, context=context or {})
    record("task_created", task_id=task.id)
    return task


def route_task(task: Task, bot_name: str) -> BotResponse:
    bot = get(bot_name)
    record("task_routed", task_id=task.id, bot=bot_name)
    log({"event": "task_routed", "task_id": task.id, "bot": bot_name})
    try:
        resp = bot.run(task)
    except Exception as exc:  # pragma: no cover - delegated
        record("bot_failure", task_id=task.id, bot=bot_name)
        raise BotExecutionError(bot=bot_name, task_id=task.id, reason=str(exc)) from exc
    if not resp.summary or bot_name not in resp.summary:
        raise BotExecutionError(bot=bot_name, task_id=task.id, reason="invalid summary")
    if not resp.risks:
        raise BotExecutionError(bot=bot_name, task_id=task.id, reason="risks missing")
    record("bot_success", task_id=task.id, bot=bot_name)
    artifact_dir = Path(settings.ARTIFACTS_DIR) / task.id
    write_json(artifact_dir / f"{bot_name.lower()}_response.json", asdict(resp))
    write_text(artifact_dir / f"{bot_name.lower()}_summary.md", resp.summary)
    return resp
