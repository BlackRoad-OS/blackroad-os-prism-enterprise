"""Minimal engineering change helpers used by the test-suite.

The historical version of :mod:`plm.eco` in this repository contained
conflicted merges which removed the helper functions relied upon by the
``tests/test_eco.py`` regression tests.  The goal of this file is not to
reinstate the entire production surface but to supply a deterministic,
file-backed workflow that mirrors the behaviour exercised in the tests:

* create a new change record on disk with :func:`new_change`
* compute a simple cost impact between revisions with :func:`impact`
* collect approvals while enforcing dual-approval for high-risk changes
* block releases whenever Statistical Process Control (SPC) findings are
  present on disk.

Only the pieces that the tests interact with are implemented which keeps
the module compact and removes a class of brittle merge conflicts.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, List

ART_DIR: Path = Path("artifacts/plm/changes")
COUNTER_FILE: Path = ART_DIR / "_counter"


@dataclass
class Change:
    id: str
    item_id: str
    from_rev: str
    to_rev: str
    reason: str
    risk: str = "medium"
    status: str = "draft"
    type: str = "ECO"
    effects: List[str] = field(default_factory=list)
    approvals: List[str] = field(default_factory=list)


def _ensure_art_dir() -> Path:
    path = Path(ART_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _path(change_id: str) -> Path:
    return _ensure_art_dir() / f"{change_id}.json"


def _next_id() -> str:
    art_dir = _ensure_art_dir()
    counter_path = art_dir / COUNTER_FILE.name
    current = 0
    if counter_path.exists():
        try:
            current = int(counter_path.read_text(encoding="utf-8").strip() or "0")
        except ValueError:
            current = 0
    current += 1
    counter_path.write_text(str(current), encoding="utf-8")
    return f"ECO-{current:05d}"


def _load(change_id: str) -> Change:
    data = json.loads(_path(change_id).read_text(encoding="utf-8"))
    return Change(**data)


def _write(change: Change) -> None:
    payload = json.dumps(asdict(change), indent=2, sort_keys=True)
    _path(change.id).write_text(payload, encoding="utf-8")


def _unique(seq: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    ordered: List[str] = []
    for value in seq:
        if value not in seen:
            seen.add(value)
            ordered.append(value)
    return ordered


def _get_item_cost(item_id: str, rev: str) -> float:
    """Return the unit cost for ``item_id`` at revision ``rev``.

    Item data is loaded through :mod:`plm.bom` fixtures during the tests,
    therefore we reuse the cached ``_ITEMS`` collection instead of hitting
    disk again.  A ``ValueError`` is raised when the revision is unknown so
    callers can surface a helpful failure mode.
    """

    from plm import bom  # Imported lazily to avoid circular imports.

    for item in reversed(list(getattr(bom, "_ITEMS", []))):
        # ``_ITEMS`` contains ``Item`` dataclasses.  Accessing via ``getattr``
        # keeps the helper resilient in the unlikely event of dict rows.
        if getattr(item, "id", None) == item_id and getattr(item, "rev", None) == rev:
            try:
                return float(getattr(item, "cost"))
            except (TypeError, ValueError):
                break
    raise ValueError(f"Unknown item/revision combination: {item_id} rev {rev}")


def new_change(
    item_id: str,
    from_rev: str,
    to_rev: str,
    reason: str,
    *,
    risk: str = "medium",
    change_type: str = "ECO",
) -> Change:
    """Create and persist a new engineering change order.

    The fixture-driven tests only require a subset of metadata so we
    initialise the JSON payload with that core information and return the
    dataclass for convenience.
    """

    change = Change(
        id=_next_id(),
        item_id=item_id,
        from_rev=from_rev,
        to_rev=to_rev,
        reason=reason,
        risk=risk,
        type=change_type,
        effects=[item_id],
        approvals=[],
    )
    _write(change)
    return change


def impact(change_id: str) -> float:
    """Return the cost delta between the change's revisions."""

    change = _load(change_id)
    to_cost = _get_item_cost(change.item_id, change.to_rev)
    from_cost = _get_item_cost(change.item_id, change.from_rev)
    delta = round(to_cost - from_cost, 4)
    return delta


def approve(change_id: str, user: str) -> Change:
    change = _load(change_id)
    change.approvals = _unique([*change.approvals, user])
    if change.risk != "high" or len(change.approvals) >= 2:
        change.status = "approved"
    _write(change)
    return change


def _spc_findings_path() -> Path:
    return Path("artifacts/mfg/spc/findings.json")


def release(change_id: str) -> Change:
    change = _load(change_id)

    if change.risk == "high" and len(change.approvals) < 2:
        raise RuntimeError("Policy: dual approval required for high risk changes")

    findings_path = _spc_findings_path()
    if findings_path.exists():
        try:
            findings = json.loads(findings_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            findings = ["unparseable"]
        if findings:
            raise RuntimeError("DUTY_SPC_UNSTABLE: SPC findings detected")

    change.status = "released"
    _write(change)
    return change


def cli_eco_new(argv: List[str] | None = None) -> Change:
    parser = argparse.ArgumentParser(prog="plm:eco:new", description="Create a new ECO")
    parser.add_argument("--item", required=True)
    parser.add_argument("--from", dest="from_rev", required=True)
    parser.add_argument("--to", dest="to_rev", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args(argv)
    return new_change(args.item, args.from_rev, args.to_rev, args.reason)


def cli_eco_release(argv: List[str] | None = None) -> Change:
    parser = argparse.ArgumentParser(prog="plm:eco:release", description="Release an ECO")
    parser.add_argument("--id", required=True)
    args = parser.parse_args(argv)
    return release(args.id)


__all__ = [
    "Change",
    "new_change",
    "impact",
    "approve",
    "release",
    "cli_eco_new",
    "cli_eco_release",
    "ART_DIR",
    "_path",
]

# Backwards compatibility: some callers still import ``create_change``.
create_change = new_change
