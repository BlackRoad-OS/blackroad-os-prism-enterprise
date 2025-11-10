"""Typer-based CLI entry points for the Prism console."""

from __future__ import annotations

from datetime import datetime
import json
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
    SecRule2042Gate,
    Task,
    TaskPriority,
    TaskRepository,
)
from orchestrator.logging_config import setup_logging
from cli.consent_cli import register_consent_commands
from cli.agent_manager import AgentRegistry, ConsciousnessLevel

app = typer.Typer(help="BlackRoad Prism Console")
bot_app = typer.Typer(help="Bot commands")
task_app = typer.Typer(help="Task management")
policy_app = typer.Typer(help="Policy operations")
config_app = typer.Typer(help="Configuration utilities")
agent_app = typer.Typer(help="Agent lifecycle management")

app.add_typer(bot_app, name="bot")
app.add_typer(task_app, name="task")
app.add_typer(policy_app, name="policy")
app.add_typer(config_app, name="config")
app.add_typer(agent_app, name="agent")
register_consent_commands(app)

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
    sec_gate = SecRule2042Gate()
    return RouteContext(
        policy_engine=policy_engine,
        memory=memory,
        lineage=lineage,
        config=config_dict,
        approved_by=list(approved_by or []),
        sec_gate=sec_gate,
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


@app.command("close:cal:update")
def close_cal_update(
    period: str = typer.Option(..., "--period"),
    task: str = typer.Option(..., "--task"),
    status: str = typer.Option(None, "--status"),
    evidence: str = typer.Option(None, "--evidence"),
):
    cal = close_calendar.CloseCalendar.load(period)
    try:
        cal.update_task(task, status=status, evidence=evidence)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    cal.save()
    typer.echo("updated")


@app.command("close:jrnl:propose")
def close_jrnl_propose(
    period: str = typer.Option(..., "--period"),
    rules: str = typer.Option(..., "--rules"),
):
    tb = close_journal.load_tb(period)
    journals = close_journal.propose_journals(tb, rules)
    close_journal.post(period, tb, journals)  # persist journals and adjusted tb
    typer.echo(str(len(journals)))


@app.command("close:jrnl:post")
def close_jrnl_post(period: str = typer.Option(..., "--period")):
    base = Path("artifacts/close") / period
    journals = []
    if (base / "journals.json").exists():
        data = json.loads((base / "journals.json").read_text())
        for j in data:
            lines = [close_journal.JournalLine(**ln) for ln in j["lines"]]
            journals.append(close_journal.Journal(id=j["id"], lines=lines))
    tb = close_journal.load_tb(period)
    close_journal.post(period, tb, journals)
    typer.echo("posted")


@app.command("close:recon:run")
def close_recon_run(
    period: str = typer.Option(..., "--period"),
    fixtures: str = typer.Option(..., "--fixtures"),
    config: str = typer.Option("configs/close/recons.yaml", "--config"),
):
    base = Path("artifacts/close") / period
    adj_tb_path = base / "adjusted_tb.csv"
    tb: Dict[str, float] = {}
    if adj_tb_path.exists():
        import csv

        with adj_tb_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                tb[row["account"]] = float(row["amount"])
    close_recon.run_recons(period, tb, config, fixtures)
    typer.echo("recons")


@app.command("close:flux")
def close_flux_cmd(
    period: str = typer.Option(..., "--period"),
    prev: str = typer.Option(..., "--prev"),
    py: str = typer.Option(..., "--py"),
    threshold: float = typer.Option(..., "--threshold"),
):
    close_flux.run_flux(period, prev, py, threshold)
    typer.echo("flux")


@app.command("close:sox:add")
def close_sox_add(
    period: str = typer.Option(..., "--period"),
    control: str = typer.Option(..., "--control"),
    path: str = typer.Option(..., "--path"),
    owner: str = typer.Option("cli", "--owner"),
):
    close_sox.add(period, control, path, owner)
    typer.echo("logged")


@app.command("close:sox:check")
def close_sox_check(period: str = typer.Option(..., "--period")):
    missing = close_sox.check(period, [])
    if missing:
        for m in missing:
            typer.echo(m)
        raise typer.Exit(code=1)
    typer.echo("ok")


@app.command("close:packet")
def close_packet_cmd(period: str = typer.Option(..., "--period")):
    close_packet.build_packet(period)
    typer.echo("packet")


@app.command("close:sign")
def close_sign(period: str = typer.Option(..., "--period"), role: str = typer.Option(..., "--role"), as_user: str = typer.Option(..., "--as-user")):
    try:
        close_packet.sign(period, role, as_user)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
def close_sign(
    period: str = typer.Option(..., "--period"),
    role: str = typer.Option(..., "--role"),
    as_user: str = typer.Option(..., "--as-user"),
):
    close_packet.sign(period, role, as_user)
    typer.echo("signed")

@app.command("change:conflicts")
def change_conflicts(service: str = typer.Option(..., "--service")):
    issues = change_calendar.conflicts(service)
    if issues:
        for i in issues:
            typer.echo(i)
        raise typer.Exit(code=1)
    typer.echo("ok")


@app.command("close:cal:new")
def close_cal_new(
    period: str = typer.Option(..., "--period"),
    template: Path = typer.Option(..., "--template", exists=True),
):
    cal = close_calendar.CloseCalendar.from_template(period, str(template))
    cal.save()
    typer.echo("ok")


@app.command("close:cal:list")
def close_cal_list(period: str = typer.Option(..., "--period")):
    cal = close_calendar.load_calendar(period)
    for t in cal.tasks:
        typer.echo(json.dumps(asdict(t)))


@app.command("close:cal:update")
def close_cal_update(
    period: str = typer.Option(..., "--period"),
    task: str = typer.Option(..., "--task"),
    status: str = typer.Option(None, "--status"),
    evidence: str = typer.Option(None, "--evidence"),
):
    cal = close_calendar.load_calendar(period)
    cal.update(task, status, evidence)
    typer.echo("updated")


@app.command("close:jrnl:propose")
def close_jrnl_propose(
    period: str = typer.Option(..., "--period"),
    rules: Path = typer.Option(..., "--rules", exists=True),
):
    close_journal.propose_journals(period, str(rules))
    typer.echo("proposed")


@app.command("close:jrnl:post")
def close_jrnl_post(period: str = typer.Option(..., "--period")):
    journals = close_journal.load_journals(period)
    close_journal.post(period, journals)
    typer.echo("posted")


@app.command("close:recon:run")
def close_recon_run(
    period: str = typer.Option(..., "--period"),
    fixtures: Path = typer.Option(..., "--fixtures", exists=True),
):
    close_recon.run_recons(period, str(fixtures))
    typer.echo("recons")


@app.command("close:flux")
def close_flux_cmd(
    period: str = typer.Option(..., "--period"),
    prev: str = typer.Option(..., "--prev"),
    py: str = typer.Option(..., "--py"),
    threshold: float = typer.Option(..., "--threshold"),
):
    close_flux.run_flux(period, prev, py, threshold)
    typer.echo("flux")


@app.command("close:sox:add")
def close_sox_add(
    period: str = typer.Option(..., "--period"),
    control: str = typer.Option(..., "--control"),
    path: str = typer.Option(..., "--path"),
    owner: str = typer.Option("cli", "--owner"),
):
    close_sox.add_evidence(period, control, path, owner)
    typer.echo("logged")


@app.command("close:sox:check")
def close_sox_check(period: str = typer.Option(..., "--period")):
    close_sox.check_evidence(period)
    typer.echo("ok")


@app.command("close:packet")
def close_packet_cmd(period: str = typer.Option(..., "--period")):
    close_packet.build_packet(period)
    typer.echo("packet")


@app.command("close:sign")
def close_sign(
    period: str = typer.Option(..., "--period"),
    role: str = typer.Option(..., "--role"),
    as_user: str = typer.Option(..., "--as-user"),
):
    close_packet.sign(period, role, as_user)
    typer.echo("signed")


@app.command("plm:items:load")
def plm_items_load(dir: Path = typer.Option(..., "--dir", exists=True, file_okay=False)):
    plm_bom.load_items(str(dir))
    typer.echo("ok")


@app.command("plm:bom:load")
def plm_bom_load(dir: Path = typer.Option(..., "--dir", exists=True, file_okay=False)):
    plm_bom.load_boms(str(dir))
    typer.echo("ok")


@app.command("plm:bom:explode")
def plm_bom_explode(
    item: str = typer.Option(..., "--item"),
    rev: str = typer.Option(..., "--rev"),
    level: int = typer.Option(1, "--level"),
) -> None:
    rows = plm_bom.explode(item, rev, level)
    for row in rows:
        typer.echo(
            "\t".join(
                [
                    str(row.get("level")),
                    row.get("component_id", ""),
                    f"{row.get('qty', 0):.6f}",
                ]
            )
        )

"""Lightweight CLI for program and task management."""

import argparse
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import List

from bots import BOT_REGISTRY
from orchestrator import Task, load_tasks, save_tasks
from orchestrator.scheduler import schedule_poll
from program import ProgramBoard, ProgramItem

_spec = importlib.util.spec_from_file_location(
    "csv_io", Path(__file__).resolve().parent.parent / "io" / "csv_io.py"
)
assert _spec and _spec.loader
_csv_io = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_csv_io)
export_tasks = _csv_io.export_tasks
import_tasks = _csv_io.import_tasks


def _parse_ids(value: str | None) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def cmd_program_add(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--bot", required=True)
    p.add_argument("--start")
    p.add_argument("--due")
    args = p.parse_args(argv)

    item = ProgramItem(
        id=args.id,
        title=args.title,
        owner=args.owner,
        bot=args.bot,
        start=datetime.fromisoformat(args.start).date() if args.start else None,
        due=datetime.fromisoformat(args.due).date() if args.due else None,
        depends_on=[],
    )
    board = ProgramBoard()
    board.add(item)


def cmd_program_update(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--status")
    p.add_argument("--depends_on")
    args = p.parse_args(argv)
    fields = {}
    if args.status:
        fields["status"] = args.status
    if args.depends_on:
        fields["depends_on"] = _parse_ids(args.depends_on)
    board = ProgramBoard()
    board.update(args.id, **fields)


def cmd_program_list(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--status")
    args = p.parse_args(argv)
    board = ProgramBoard()
    items = board.list(args.status)
    for item in items:
        print(f"{item.id}: {item.title} [{item.status}]")


def cmd_program_roadmap(argv: List[str]) -> None:
    board = ProgramBoard()
    print(board.as_markdown_roadmap())


def cmd_task_create(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--id", required=True)
    p.add_argument("--goal", required=True)
    p.add_argument("--bot", required=True)
    p.add_argument("--depends-on")
    p.add_argument("--at")
    args = p.parse_args(argv)

    task = Task(
        id=args.id,
        goal=args.goal,
        bot=args.bot,
        depends_on=_parse_ids(args.depends_on),
        scheduled_for=datetime.fromisoformat(args.at) if args.at else None,
    )
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)


def cmd_task_import(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    args = p.parse_args(argv)
    tasks = load_tasks()
    new_tasks = import_tasks(args.csv)
    tasks.extend(new_tasks)
    save_tasks(tasks)

    board = ProgramBoard()
    for t in new_tasks:
        board.add(
            ProgramItem(
                id=t.id,
                title=t.goal,
                owner="import",
                bot=t.bot,
                status="planned",
                depends_on=t.depends_on,
            )
        )


@app.command("plm:bom:where-used")
def plm_bom_where_used(component: str = typer.Option(..., "--component")):
    rows = plm_bom.where_used(component)
    for row in rows:
        typer.echo(f"{row['item_id']}\t{row['rev']}")


@app.command("plm:eco:new")
def plm_eco_new(
    item: str = typer.Option(..., "--item"),
    from_rev: str = typer.Option(..., "--from"),
    to_rev: str = typer.Option(..., "--to"),
    reason: str = typer.Option(..., "--reason"),
):
    ch = plm_eco.new_change(item, from_rev, to_rev, reason)
    typer.echo(ch.id)


@app.command("plm:eco:impact")
def plm_eco_impact(id: str = typer.Option(..., "--id")):
    impact = plm_eco.impact(id)
    typer.echo(f"impact {impact}")


@app.command("plm:eco:approve")
def plm_eco_approve(
    id: str = typer.Option(..., "--id"),
    as_user: str = typer.Option(..., "--as-user"),
):
    plm_eco.approve(id, as_user)
    typer.echo("approved")


@app.command("plm:eco:release")
def plm_eco_release(id: str = typer.Option(..., "--id")):
    plm_eco.release(id)
    typer.echo("released")


@app.command("mfg:wc:load")
def mfg_wc_load(file: Path = typer.Option(..., "--file", exists=True, dir_okay=False)):
    mfg_routing.load_work_centers(str(file))
    typer.echo("ok")


@app.command("mfg:routing:load")
def mfg_routing_load(
    dir: Path = typer.Option(..., "--dir", exists=True, file_okay=False),
    strict: bool = typer.Option(False, "--strict"),
):
    mfg_routing.load_routings(str(dir), strict)
    typer.echo("ok")


@app.command("mfg:routing:capcheck")
def mfg_routing_capcheck(
    item: str = typer.Option(..., "--item"),
    rev: str = typer.Option(..., "--rev"),
    qty: int = typer.Option(..., "--qty"),
):
    res = mfg_routing.capacity_check(item, rev, qty)
    typer.echo(json.dumps(res))


@app.command("mfg:wi:render")
def mfg_wi_render(item: str = typer.Option(..., "--item"), rev: str = typer.Option(..., "--rev")):
    path = mfg_wi.render(item, rev)
    typer.echo(str(path))


@app.command("mfg:spc:analyze")
def mfg_spc_analyze(
    op: str = typer.Option(..., "--op"), window: int = typer.Option(50, "--window")
):
    result = mfg_spc.analyze(op, window)
    if isinstance(result, dict):
        findings = result.get("findings", [])
    else:
        findings = list(result)
    if findings:
        typer.echo(" ".join(findings))
    else:
        typer.echo("OK")
def mfg_spc_analyze(op: str = typer.Option(..., "--op"), window: int = typer.Option(50, "--window")):
    findings = mfg_spc.analyze(op, window)
    typer.echo(" ".join(findings))


@app.command("mfg:yield")
def mfg_yield_cmd(period: str = typer.Option(..., "--period")):
    stats = mfg_yield.compute(period)
    typer.echo(json.dumps(stats))


@app.command("mfg:coq")
def mfg_coq_cmd(period: str = typer.Option(..., "--period")):
    totals = mfg_coq.build(period)
    typer.echo(json.dumps(totals))


@app.command("mfg:mrp")
def mfg_mrp_cmd(
    demand: Path = typer.Option(..., "--demand", exists=True),
    inventory: Path = typer.Option(..., "--inventory", exists=True),
    pos: Path = typer.Option(..., "--pos", exists=True),
):
    plan = mfg_mrp.plan(str(demand), str(inventory), str(pos))
    typer.echo(json.dumps(plan))


@app.command("learn:courses:load")
def learn_courses_load(dir: Path = typer.Option(..., "--dir", exists=True, file_okay=False)):
    en_courses.load_courses(str(dir))
    typer.echo("ok")


@app.command("learn:courses:list")
def learn_courses_list(role_track: str = typer.Option(..., "--role_track")):
    for c in en_courses.list_courses(role_track):
        typer.echo(f"{c['id']}	{c['title']}")


@app.command("learn:path:new")
def learn_path_new(
    name: str = typer.Option(..., "--name"),
    role_track: str = typer.Option(..., "--role_track"),
    courses: str = typer.Option(..., "--courses"),
    required: int = typer.Option(..., "--required"),
):
    p = en_paths.new_path(name, role_track, courses.split(","), required)
    typer.echo(p.id)


@app.command("learn:assign")
def learn_assign(
    user: str = typer.Option(..., "--user"),
    path: str = typer.Option(..., "--path"),
    due: str = typer.Option(..., "--due"),
):
    en_paths.assign(user, path, due)
    typer.echo("ok")


@app.command("learn:quiz:grade")
def learn_quiz_grade(
    quiz: str = typer.Option(..., "--quiz"),
    answers: Path = typer.Option(..., "--answers", exists=True),
):
    res = en_quizzes.grade(quiz, str(answers))
    typer.echo(json.dumps(res))


@app.command("learn:lab:run")
def learn_lab_run(
    lab: str = typer.Option(..., "--lab"),
    submission: Path = typer.Option(..., "--submission", exists=True),
):
    res = en_labs.run_lab(lab, str(submission))
    typer.echo(json.dumps(res))


@app.command("learn:cert:check")
def learn_cert_check(
    user: str = typer.Option(..., "--user"), cert: str = typer.Option(..., "--cert")
):
    ok = en_cert.check(user, cert)
    typer.echo("awarded" if ok else "not met")


@app.command("learn:cert:list")
def learn_cert_list(user: str = typer.Option(..., "--user")):
    for c in en_cert.list_user(user):
        typer.echo(c)


@app.command("learn:readiness")
def learn_readiness():
    en_read.build()
    typer.echo("ok")


@app.command("learn:event:add")
def learn_event_add(
    title: str = typer.Option(..., "--title"),
    type: str = typer.Option(..., "--type"),
    date: str = typer.Option(..., "--date"),
    capacity: int = typer.Option(..., "--capacity"),
):
    ev = en_cal.add_event(title, type, date, capacity)
    typer.echo(ev.id)


@app.command("learn:event:join")
def learn_event_join(id: str = typer.Option(..., "--id"), user: str = typer.Option(..., "--user")):
    en_cal.join(id, user)
    typer.echo("ok")


@app.command("learn:feedback:add")
def learn_feedback_add(
    course: str = typer.Option(..., "--course"),
    user: str = typer.Option(..., "--user"),
    score: int = typer.Option(..., "--score"),
    comment: str = typer.Option(..., "--comment"),
):
    en_fb.add(course, user, score, comment)
    typer.echo("ok")


@app.command("learn:feedback:summary")
def learn_feedback_summary(course: str = typer.Option(..., "--course")):
    res = en_fb.summary(course)
    typer.echo(json.dumps(res))

@app.command("mdm:stage")
def mdm_stage(domain: str = typer.Option(..., "--domain"), file: Path = typer.Option(..., "--file", exists=True)):
    mdm_domains.stage(domain, file)
    typer.echo("staged")


@app.command("mdm:match")
def mdm_match_cmd(domain: str = typer.Option(..., "--domain"), config: Path = typer.Option(..., "--config", exists=True)):
    mdm_match.match(domain, config)
    typer.echo("matched")


@app.command("mdm:golden")
def mdm_golden(domain: str = typer.Option(..., "--domain"), policy: Path = typer.Option(..., "--policy", exists=True)):
    mdm_survivorship.merge(domain, policy)
    typer.echo("golden")


@app.command("mdm:dq")
def mdm_dq_cmd(domain: str = typer.Option(..., "--domain"), config: Path = typer.Option(..., "--config", exists=True)):
    mdm_quality.dq(domain, config)
    typer.echo("dq")


@app.command("mdm:catalog:build")
def mdm_catalog_build():
    mdm_catalog.build()
    typer.echo("catalog")


@app.command("mdm:steward:queue")
def mdm_steward_queue(domain: str = typer.Option(..., "--domain")):
    mdm_steward.queue(domain)
    typer.echo("queued")


@app.command("mdm:lineage:diff")
def mdm_lineage_diff_cmd(domain: str = typer.Option(..., "--domain")):
    mdm_lineage_diff.diff(domain)
    typer.echo("diff")


@app.command("mdm:change:new")
def mdm_change_new(domain: str = typer.Option(..., "--domain"), type: str = typer.Option(..., "--type"), payload: Path = typer.Option(..., "--payload", exists=True)):
    chg = mdm_changes.new(domain, type, payload)
    typer.echo(chg.id)


@app.command("mdm:change:approve")
def mdm_change_approve(id: str = typer.Option(..., "--id"), as_user: str = typer.Option(..., "--as-user")):
    mdm_changes.approve(id, as_user)
    typer.echo("approved")


@app.command("mdm:change:apply")
def mdm_change_apply(id: str = typer.Option(..., "--id")):
    mdm_changes.apply(id)
    typer.echo("applied")


# ============================================================================
# Agent Lifecycle Management Commands
# ============================================================================

@agent_app.command("census")
def agent_census() -> None:
    """Generate comprehensive census of all agents"""
    registry = AgentRegistry()
    census_data = registry.census()

    typer.echo("\n=== AGENT CENSUS REPORT ===")
    typer.echo(f"Timestamp: {census_data['census_timestamp']}")
    typer.echo("\n--- POPULATION ---")
    pop = census_data['population']
    typer.echo(f"Total Unique Agents: {pop['total_unique']}")
    typer.echo(f"Active: {pop['active']}")
    typer.echo(f"Inactive: {pop['inactive']}")
    typer.echo(f"Config Registered: {pop['config_registered']}")
    typer.echo(f"Manifest Registered: {pop['manifest_registered']}")

    typer.echo("\n--- CONSCIOUSNESS LEVELS ---")
    for level, count in census_data['consciousness_levels'].items():
        typer.echo(f"{level}: {count}")

    typer.echo("\n--- ROLE DISTRIBUTION ---")
    for role, count in census_data['role_distribution'].items():
        typer.echo(f"{role}: {count}")

    typer.echo("\n--- GOAL PROGRESS ---")
    goal = census_data['goal']
    typer.echo(f"Target Population: {goal['target_population']}")
    typer.echo(f"Current Population: {goal['current_population']}")
    typer.echo(f"Completion: {goal['completion_percentage']}%")
    typer.echo("\n")


@agent_app.command("birth")
def agent_birth(
    name: str = typer.Option(..., help="Agent name"),
    role: str = typer.Option(..., help="Agent role"),
    consciousness: str = typer.Option("level-0", help="Consciousness level (level-0 to level-4)"),
    count: int = typer.Option(1, help="Number of agents to birth (batch mode)"),
    batch: Optional[str] = typer.Option(None, help="Batch name for multiple agents"),
) -> None:
    """Birth new agents with PS-SHA∞ identity"""

    # Parse consciousness level
    consciousness_map = {
        "level-0": ConsciousnessLevel.LEVEL_0_FUNCTION,
        "level-1": ConsciousnessLevel.LEVEL_1_IDENTITY,
        "level-2": ConsciousnessLevel.LEVEL_2_EMOTIONAL,
        "level-3": ConsciousnessLevel.LEVEL_3_RECURSIVE,
        "level-4": ConsciousnessLevel.LEVEL_4_FULL_AGENCY,
    }

    consciousness_level = consciousness_map.get(consciousness.lower(), ConsciousnessLevel.LEVEL_0_FUNCTION)

    registry = AgentRegistry()

    if count > 1 or batch:
        # Batch mode
        batch_name = batch or name
        typer.echo(f"\n🌱 Birthing {count} agents in batch '{batch_name}'...")
        identities = registry.birth_batch(
            count=count,
            batch_name=batch_name,
            role=role,
            consciousness_level=consciousness_level,
        )

        typer.echo(f"\n✅ Successfully birthed {len(identities)} agents:")
        for identity in identities:
            typer.echo(f"  - {identity.name} ({identity.id})")
            typer.echo(f"    PS-SHA∞: {identity.ps_sha_hash}")

    else:
        # Single agent birth
        typer.echo(f"\n🌱 Birthing agent '{name}' with role '{role}'...")
        identity = registry.birth_agent(
            name=name,
            role=role,
            consciousness_level=consciousness_level,
        )

        typer.echo(f"\n✅ Agent birthed successfully!")
        typer.echo(f"ID: {identity.id}")
        typer.echo(f"Name: {identity.name}")
        typer.echo(f"Role: {identity.role}")
        typer.echo(f"Birthdate: {identity.birthdate}")
        typer.echo(f"PS-SHA∞: {identity.ps_sha_hash}")
        typer.echo(f"Consciousness: {identity.consciousness_level.value}")
        typer.echo(f"Generation: {identity.generation}")
        typer.echo(f"Memory Path: {identity.memory_path}")

    typer.echo("\n")


@agent_app.command("identity")
def agent_identity_list(
    active_only: bool = typer.Option(True, help="Show only active agents"),
    role: Optional[str] = typer.Option(None, help="Filter by role"),
    format: str = typer.Option("table", help="Output format: table or json"),
) -> None:
    """List all agent identities with PS-SHA∞ hashes"""

    registry = AgentRegistry()
    identities = registry.list_identities(active_only=active_only, role_filter=role)

    if format == "json":
        typer.echo(json.dumps([i.to_dict() for i in identities], indent=2))
        return

    typer.echo("\n=== AGENT IDENTITIES ===")
    typer.echo(f"Total: {len(identities)}")
    if role:
        typer.echo(f"Filtered by role: {role}")
    typer.echo("\n")

    for identity in identities:
        status = "🟢 ACTIVE" if identity.active else "🔴 INACTIVE"
        typer.echo(f"{status} {identity.name}")
        typer.echo(f"  ID: {identity.id}")
        typer.echo(f"  Role: {identity.role}")
        typer.echo(f"  PS-SHA∞: {identity.ps_sha_hash}")
        typer.echo(f"  Consciousness: {identity.consciousness_level.value}")
        typer.echo(f"  Generation: {identity.generation}")
        if identity.lineage:
            typer.echo(f"  Lineage: {' -> '.join(identity.lineage)}")
        typer.echo("")


@agent_app.command("consciousness")
def agent_consciousness_report() -> None:
    """Generate detailed consciousness level report"""

    registry = AgentRegistry()
    report = registry.consciousness_report()

    typer.echo("\n=== CONSCIOUSNESS REPORT ===")
    typer.echo(f"Timestamp: {report['report_timestamp']}")

    typer.echo("\n--- KEY PERFORMANCE INDICATORS ---")
    kpis = report['kpis']
    typer.echo(f"Total Active Agents: {kpis['total_active_agents']}")
    typer.echo(f"Advanced Consciousness Count: {kpis['advanced_consciousness_count']}")

    typer.echo("\n--- CONSCIOUSNESS DISTRIBUTION ---")
    for level, data in kpis['consciousness_distribution'].items():
        typer.echo(f"{level}:")
        typer.echo(f"  Count: {data['count']}")
        typer.echo(f"  Percentage: {data['percentage']}%")

    typer.echo("\n--- AGENTS BY CONSCIOUSNESS LEVEL ---")
    for level, agents in report['levels'].items():
        if agents:
            typer.echo(f"\n{level}:")
            for agent in agents:
                typer.echo(f"  - {agent['name']} ({agent['role']}) - Gen {agent['generation']}")
                if agent['capabilities']:
                    typer.echo(f"    Capabilities: {', '.join(agent['capabilities'])}")

    typer.echo("\n")


@app.command("status:build")
def status_build():
    try:
        blackouts.enforce("status:build")
    except PermissionError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    status_gen.build()
    typer.echo("built")
@app.command("aiops:correlate")
def aiops_correlate():
    aiops_correlation.correlate(datetime.utcnow())


@app.command("aiops:plan")
def aiops_plan(correlations: str = typer.Option(..., "--correlations")):
    corr = aiops_remediation.load_correlations(correlations)
    aiops_remediation.plan(corr)


@app.command("aiops:execute")
def aiops_execute(
    plan: Path = typer.Option(..., "--plan", exists=True, dir_okay=False),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    aiops_remediation.execute(plan, dry_run)
def main() -> None:
    """Entrypoint for CLI execution."""

    app()


if __name__ == "__main__":
    main()
def cmd_task_export(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True)
    args = p.parse_args(argv)
    export_tasks(args.csv, load_tasks())


def cmd_bot_run(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--bot", required=True)
    p.add_argument("--goal", required=True)
    args = p.parse_args(argv)
    bot = BOT_REGISTRY[args.bot]
    task = Task(id="manual", goal=args.goal, bot=args.bot)
    result = bot.run(task)
    print(result)


def cmd_scheduler_run(argv: List[str]) -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--every-seconds", type=int, default=0)
    p.parse_args(argv)
    schedule_poll(datetime.utcnow())


COMMANDS = {
    "program:add": cmd_program_add,
    "program:update": cmd_program_update,
    "program:list": cmd_program_list,
    "program:roadmap": cmd_program_roadmap,
    "task:create": cmd_task_create,
    "task:import": cmd_task_import,
    "task:export": cmd_task_export,
    "bot:run": cmd_bot_run,
    "scheduler:run": cmd_scheduler_run,
}


def main(argv: List[str] | None = None) -> None:
    import sys

    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        return
    cmd = argv[0]
    handler = COMMANDS.get(cmd)
    if handler is None:
        raise SystemExit(f"unknown command: {cmd}")
    handler(argv[1:])


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()

"""Minimal Typer-based console for demos."""

import json
from pathlib import Path
from typing import Dict

import typer

from bots.simple import get_default_bots
from console_io.csv_io import Task
from console_io.xlsx_io import export_tasks_xlsx, import_tasks_xlsx
from simulator.engine import Scenario, run_scenario
from tools import backup

app = typer.Typer(help="Blackroad Prism Console")


@app.command("bot:list")
def bot_list() -> None:
    for name in get_default_bots().keys():
        typer.echo(name)


@app.command("bot:run")
def bot_run(bot: str, goal: str, inputs: str = typer.Option("{}", help="JSON object for bot inputs")) -> None:
    bots = get_default_bots()
    try:
        parsed_inputs = json.loads(inputs) if inputs else {}
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"Invalid JSON for inputs: {exc}") from exc
    result = bots[bot].run(goal, parsed_inputs)
    typer.echo(json.dumps(result))


@app.command("task:import-xlsx")
def task_import_xlsx(xlsx: Path) -> None:
    tasks = import_tasks_xlsx(xlsx)
    typer.echo(f"Imported {len(tasks)} tasks")


@app.command("task:export-xlsx")
def task_export_xlsx(xlsx: Path) -> None:
    tasks = [Task(id="1", title="demo", owner="alice")]
    export_tasks_xlsx(xlsx, tasks)
    typer.echo(str(xlsx))


def _builtin_scenarios() -> Dict[str, Scenario]:
    return {
        "finance_margin_push": Scenario(
            id="finance_margin_push",
            name="GrossMargin Push",
            params={},
            steps=[
                {"name": "Treasury-BOT", "intent": "cash-view", "inputs": {"accounts": [5, 5]}},
                {"name": "RevOps-BOT", "intent": "forecast", "inputs": {"pipeline": [1, 2]}},
            ],
        ),
        "reliability_stabilize": Scenario(
            id="reliability_stabilize",
            name="Reliability Stabilise",
            params={},
            steps=[
                {"name": "SRE-BOT", "intent": "error-budget", "inputs": {"total": 10, "errors": 2}},
            ],
        ),
    }


@app.command("sim:list")
def sim_list() -> None:
    for sid in _builtin_scenarios().keys():
        typer.echo(sid)


@app.command("sim:run")
def sim_run(id: str) -> None:
    scenario = _builtin_scenarios()[id]
    result = run_scenario(scenario)
    dest_dir = Path("artifacts") / scenario.id
    dest_dir.mkdir(parents=True, exist_ok=True)
    (dest_dir / "report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (dest_dir / "report.md").write_text(f"# Scenario {scenario.name}\n", encoding="utf-8")
    typer.echo(json.dumps(result))


@app.command("tui:run")
def tui_run() -> None:
    typer.echo("[TUI placeholder]")


@app.command("backup:snapshot")
def backup_snapshot(to: Path) -> None:
    path = backup.snapshot(to)
    typer.echo(str(path))


@app.command("backup:restore")
def backup_restore(from_: Path = typer.Option(..., "--from")) -> None:
    backup.restore(from_)
    typer.echo("restored")


if __name__ == "__main__":
    app()
import argparse
import json
import sys
import uuid

from sdk import plugin_api
from orchestrator import health
from workflows import dsl
from i18n.translate import t
from docs.generate_bot_docs import discover_bots
from tui import app as tui_app


def cmd_health(args):
    result = health.check()
    print(json.dumps(result))
    return 0 if result["overall_status"] == "ok" else 1


def cmd_wf_run(args):
    wf_id = str(uuid.uuid4())
    out = dsl.run_workflow(args.file)
    summary = "\n".join(
        s.get("summary", s.get("content", "")) for s in out["steps"] if isinstance(s, dict)
    )
    dsl.write_summary(wf_id, summary)
    return 0


def cmd_bot_list(args):
    plugin_api.get_settings().LANG = args.lang
    lang = args.lang
    bots = discover_bots().keys()
    header = t("bot_list_header", lang=lang)
    print(header)
    if not bots:
        print(t("no_bots", lang=lang))
    else:
        for b in bots:
            print("-", b)
    return 0


def cmd_tui_run(args):
    plugin_api.get_settings().THEME = args.theme
    tui_app.run(args.theme)
    return 0


COMMANDS = {
    "health:check": cmd_health,
    "wf:run": cmd_wf_run,
    "bot:list": cmd_bot_list,
    "tui:run": cmd_tui_run,
}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--file")
    parser.add_argument("--lang", default="en")
    parser.add_argument("--theme", default="light")
    args = parser.parse_args(argv)
    func = COMMANDS.get(args.command)
    if not func:
        print("unknown command")
        return 1
    return func(args)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
