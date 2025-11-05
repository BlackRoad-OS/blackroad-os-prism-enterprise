"""Command line interface for the Prism Console."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import typer

from bots import build_registry
from config.models import ConfigurationBundle
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
from orchestrator.logging_config import setup_logging

app = typer.Typer(help="BlackRoad Prism Console")
bot_app = typer.Typer(help="Bot commands")
task_app = typer.Typer(help="Task management")
policy_app = typer.Typer(help="Policy operations")
config_app = typer.Typer(help="Configuration utilities")

app.add_typer(bot_app, name="bot")
app.add_typer(task_app, name="task")
app.add_typer(policy_app, name="policy")
app.add_typer(config_app, name="config")

TASK_STORE = Path("artifacts/tasks.json")
LINEAGE_LOG = Path("artifacts/lineage.jsonl")
APPROVALS_PATH = Path("config/approvals.yaml")


def _load_router() -> Router:
    registry = build_registry()
    repository = TaskRepository(TASK_STORE)
    return Router(registry=registry, repository=repository)


def _load_route_context(approved_by: Iterable[str] | None = None) -> RouteContext:
    policy_engine = PolicyEngine.from_file(APPROVALS_PATH)
    memory = MemoryLog()
    lineage = LineageTracker(LINEAGE_LOG)
    # Load configuration bundle
    bundle = ConfigurationBundle.from_files(Path("config"))
    config_dict = {
        "finance": {
            "treasury": {
                "cash_floor": bundle.treasury.cash_floor,
                "hedge_policies": bundle.treasury.hedge_policies,
            }
        },
        "supply": {
            "sop": {
                "planning_horizon_weeks": bundle.sop.planning_horizon_weeks,
                "inventory_targets": [t.model_dump() for t in bundle.sop.inventory_targets],
                "logistics_partners": [p.model_dump() for p in bundle.sop.logistics_partners],
            }
        },
    }
    return RouteContext(
        policy_engine=policy_engine,
        memory=memory,
        lineage=lineage,
        config=config_dict,
        approved_by=list(approved_by or []),
    )


def _parse_priority(priority: str) -> TaskPriority:
    try:
        return TaskPriority(priority.lower())
    except ValueError as exc:
        raise typer.BadParameter("Priority must be low, medium, or high") from exc


def _generate_task_id() -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    return f"TSK-{timestamp}"


@app.callback()
def _configure(log_level: str = typer.Option("info", help="Logging level")) -> None:
    """Initialise logging before executing commands."""

    setup_logging(log_level)


@bot_app.command("list")
def list_command(verbose: bool = typer.Option(False, help="Show metadata for each bot")) -> None:
    """List available bots."""

    registry = build_registry()
    for bot in registry.list():
        typer.echo(f"- {bot.metadata.name}")
        if verbose:
            for field, values in bot.describe().items():
                joined = ", ".join(values)
                typer.echo(f"    {field}: {joined}")


@task_app.command("create")
def create_task(
    goal: str = typer.Option(..., help="Goal description for the task"),
    owner: str = typer.Option(..., help="Owner or requesting team"),
    priority: str = typer.Option("medium", help="Task priority"),
    due_date: Optional[str] = typer.Option(None, help="Optional due date (YYYY-MM-DD)"),
    tag: List[str] = typer.Option([], help="Tag to attach to the task", show_default=False),
    metadata: List[str] = typer.Option(
        [], help="Additional metadata as key=value", show_default=False
    ),
) -> None:
    """Create a new task in the repository."""

    repository = TaskRepository(TASK_STORE)
    task_id = _generate_task_id()
    parsed_due: Optional[datetime] = None
    if due_date:
        try:
            parsed_due = datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError as exc:
            raise typer.BadParameter("Due date must be YYYY-MM-DD") from exc
    extra: Dict[str, str] = {}
    for entry in metadata:
        if "=" not in entry:
            raise typer.BadParameter("Metadata must be provided as key=value")
        key, value = entry.split("=", 1)
        extra[key] = value

    task = Task(
        id=task_id,
        goal=goal,
        owner=owner,
        priority=_parse_priority(priority),
        created_at=datetime.utcnow(),
        due_date=parsed_due,
        tags=tuple(tag),
        metadata=extra,
    )
    repository.add(task)
    typer.echo(f"Created task {task.id}")


@task_app.command("route")
def route_task(
    task_id: str = typer.Option(..., "--id", help="Task identifier"),
    bot: str = typer.Option(..., help="Bot name"),
    approved_by: List[str] = typer.Option([], help="Approver identifiers", show_default=False),
) -> None:
    """Route a task to a bot."""

    router = _load_router()
    context = _load_route_context(approved_by)
    response = router.route(task_id=task_id, bot_name=bot, context=context)
    typer.echo(f"Bot response: {response.summary}")


@task_app.command("history")
def task_history(task_id: str = typer.Option(..., "--id", help="Task identifier")) -> None:
    """Show memory log entries for a task."""

    memory = MemoryLog()
    entries = [entry for entry in memory.tail(limit=50) if entry["task"]["id"] == task_id]
    if not entries:
        typer.echo("No history found for task")
        return
    for entry in entries:
        typer.echo(f"{entry['timestamp']}: {entry['response']['summary']}")


@policy_app.command("list")
def list_policies() -> None:
    """Display loaded policies."""

    engine = PolicyEngine.from_file(APPROVALS_PATH)
    rules = engine.list_policies()
    if not rules:
        typer.echo("No policies configured")
        return
    for name, rule in rules.items():
        approvers = ", ".join(rule.approvers)
        typer.echo(
            f"{name}: requires_approval={rule.requires_approval}, approvers={approvers}"
        )


@config_app.command("validate")
def validate_config() -> None:
    """Validate configuration files against the schema."""

    bundle = ConfigurationBundle.from_files(Path("config"))
    bundle.validate()
    typer.echo("Configuration is valid")


def main() -> None:
    """Entrypoint for CLI execution."""

    app()


if __name__ == "__main__":
    main()
