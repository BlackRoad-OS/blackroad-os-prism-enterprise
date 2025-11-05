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
):
def plm_bom_explode(item: str = typer.Option(..., "--item"), rev: str = typer.Option(..., "--rev"), level: int = typer.Option(1, "--level")):
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
@app.command("plm:eco:new")
def plm_eco_new(item: str = typer.Option(..., "--item"), from_rev: str = typer.Option(..., "--from"), to_rev: str = typer.Option(..., "--to"), reason: str = typer.Option(..., "--reason")):
    ch = plm_eco.new_change(item, from_rev, to_rev, reason)
    typer.echo(ch.id)


@app.command("plm:eco:impact")
def plm_eco_impact(id: str = typer.Option(..., "--id")):
    impact = plm_eco.impact(id)
    typer.echo(f"impact {impact}")


@app.command("plm:eco:approve")
def plm_eco_approve(
    id: str = typer.Option(..., "--id"), as_user: str = typer.Option(..., "--as-user")
):
def plm_eco_approve(id: str = typer.Option(..., "--id"), as_user: str = typer.Option(..., "--as-user")):
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
def mfg_routing_load(dir: Path = typer.Option(..., "--dir", exists=True, file_okay=False)):
    mfg_routing.load_routings(str(dir))
    typer.echo("ok")


@app.command("mfg:routing:capcheck")
def mfg_routing_capcheck(
    item: str = typer.Option(..., "--item"),
    rev: str = typer.Option(..., "--rev"),
    qty: int = typer.Option(..., "--qty"),
):
def mfg_routing_capcheck(item: str = typer.Option(..., "--item"), rev: str = typer.Option(..., "--rev"), qty: int = typer.Option(..., "--qty")):
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
