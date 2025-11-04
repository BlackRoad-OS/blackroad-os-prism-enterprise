"""Engineering change helpers focused on the unit tests.

The production file shipped with the repository was heavily conflicted.
This module re-implements just the behaviour exercised by
``tests/plm_mfg/test_eco.py``: creating ECO records, approving them and
applying a simple dual-approval policy when releasing high risk changes.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List

ART_DIR: Path = Path("artifacts/plm/changes")
COUNTER_FILE: Path = ART_DIR / "_counter"
PLM_CATALOG_DIR: Path = Path("artifacts/plm")
ROUTING_DIR: Path = Path("artifacts/mfg/routing")


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
    _write_markdown(change)


def _markdown_path(change_id: str) -> Path:
    return _ensure_art_dir() / f"eco_{change_id}.md"


def _write_markdown(change: Change) -> None:
    lines = [
        f"# Engineering Change {change.id}",
        "",
        f"Item: {change.item_id}",
        f"From rev: {change.from_rev}",
        f"To rev: {change.to_rev}",
        f"Status: {change.status}",
        f"Risk: {change.risk}",
        "",
        f"Reason: {change.reason}",
        "",
        f"Updated: {datetime.utcnow().isoformat(timespec='seconds')}Z",
    ]
    _markdown_path(change.id).write_text("\n".join(lines) + "\n", encoding="utf-8")


def _catalog_path(name: str) -> Path:
    return PLM_CATALOG_DIR / name


def _load_catalog(name: str) -> List[Dict[str, object]]:
    path = _catalog_path(name)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        return data
    # support legacy dict payloads
    return list(data.values())


def _items_index() -> Dict[str, Dict[str, object]]:
    index: Dict[str, Dict[str, object]] = {}
    for row in _load_catalog("items.json"):
        item_id = str(row.get("id", "")).strip()
        if not item_id:
            continue
        index.setdefault(item_id, {})[str(row.get("rev", "A"))] = row
    return index


def _boms_index() -> Dict[tuple[str, str], Dict[str, object]]:
    index: Dict[tuple[str, str], Dict[str, object]] = {}
    for row in _load_catalog("boms.json"):
        item_id = str(row.get("item_id", "")).strip()
        rev = str(row.get("rev", "A")).strip() or "A"
        if not item_id:
            continue
        index[(item_id, rev)] = row
    return index


def _routing_index() -> Dict[str, Dict[str, object]]:
    try:
        from mfg import routing as routing_mod  # type: ignore

        if getattr(routing_mod, "ROUT_DB", {}):
            return routing_mod.ROUT_DB
    except Exception:  # pragma: no cover - routing module optional during tests
        pass

    path = ROUTING_DIR / "routings.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, dict):
        return data
    index: Dict[str, Dict[str, object]] = {}
    if isinstance(data, list):
        for entry in data:
            if not isinstance(entry, dict):
                continue
            key = f"{entry.get('item')}" + "_" + f"{entry.get('rev')}"
            index[key] = entry
    return index


def _bom_cost(bom_row: Dict[str, object], item_costs: Dict[str, float]) -> float:
    total = 0.0
    for line in bom_row.get("lines", []) or []:
        if not isinstance(line, dict):
            continue
        component = str(line.get("component_id", ""))
        qty = float(line.get("qty", 0) or 0.0)
        scrap = float(line.get("scrap_pct", 0) or 0.0)
        total += qty * (1 + scrap / 100.0) * item_costs.get(component, 0.0)
    return total


def _supplier_risk(components: List[str], items: Dict[str, Dict[str, object]]) -> str:
    for component in components:
        options = items.get(component, {})
        if not options:
            continue
        latest = options.get(sorted(options)[-1])
        suppliers = (latest or {}).get("suppliers", []) if latest else []
        if isinstance(suppliers, list) and len(suppliers) < 2:
            return "single_source"
    return "ok"


def _impact_path(change_id: str) -> Path:
    return _ensure_art_dir() / f"{change_id}_impact.json"


def create_change(item_id: str, from_rev: str, to_rev: str, reason: str) -> Change:
    change = Change(
        id=_next_id(),
        item_id=item_id,
        from_rev=from_rev,
        to_rev=to_rev,
        reason=reason,
        effects=[item_id],
    )
    _write(change)
    return change


new_change = create_change


def approve(change_id: str, user: str) -> Change:
    change = _load(change_id)
    if user not in change.approvals:
        change.approvals.append(user)
    if change.risk != "high" or len(change.approvals) >= 2:
        change.status = "approved"
    _write(change)
    return change


def _spc_blocking_flag() -> Path:
    return Path("artifacts/mfg/spc/blocking.flag")


def impact(change_id: str) -> Dict[str, object]:
    change = _load(change_id)

    items = _items_index()
    item_costs = {
        item_id: float((options.get(sorted(options)[-1]) or {}).get("cost", 0) or 0.0)
        for item_id, options in items.items()
        if options
    }

    boms = _boms_index()
    from_bom = boms.get((change.item_id, change.from_rev)) or {"lines": []}
    to_bom = boms.get((change.item_id, change.to_rev)) or {"lines": []}

    def _components(bom_row: Dict[str, object]) -> List[str]:
        comps: List[str] = []
        for line in bom_row.get("lines", []) or []:
            if isinstance(line, dict):
                comp = str(line.get("component_id", ""))
                if comp:
                    comps.append(comp)
        return comps

    from_components = set(_components(from_bom))
    to_components = set(_components(to_bom))
    components_added = sorted(to_components - from_components)
    components_removed = sorted(from_components - to_components)

    cost_from = _bom_cost(from_bom, item_costs)
    cost_to = _bom_cost(to_bom, item_costs)
    cost_delta = cost_to - cost_from

    routing_key = f"{change.item_id}_{change.to_rev}"
    routing = _routing_index().get(routing_key, {})
    work_centers = sorted(
        {
            str(step.get("wc"))
            for step in routing.get("steps", []) or []
            if isinstance(step, dict) and step.get("wc")
        }
    )

    impact_payload = {
        "id": change.id,
        "item_id": change.item_id,
        "from_rev": change.from_rev,
        "to_rev": change.to_rev,
        "cost_delta": round(cost_delta, 4),
        "components_added": components_added,
        "components_removed": components_removed,
        "supplier_risk": _supplier_risk(list(to_components), items),
        "impacted_work_centers": work_centers,
    }

    _impact_path(change.id).write_text(
        json.dumps(impact_payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    return impact_payload


def release(change_id: str) -> Change:
    change = _load(change_id)

    if change.risk == "high" and len(change.approvals) < 2:
        raise SystemExit("Policy: dual approval required for high risk changes")

    flag = _spc_blocking_flag()
    if flag.exists():
        raise SystemExit("DUTY_SPC_UNSTABLE: SPC blocking flag present")

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
    return create_change(args.item, args.from_rev, args.to_rev, args.reason)


def cli_eco_impact(argv: List[str] | None = None) -> Dict[str, object]:
    parser = argparse.ArgumentParser(prog="plm:eco:impact", description="Summarise ECO impact")
    parser.add_argument("--id", required=True)
    args = parser.parse_args(argv)
    return impact(args.id)


def cli_eco_release(argv: List[str] | None = None) -> Change:
    parser = argparse.ArgumentParser(prog="plm:eco:release", description="Release an ECO")
    parser.add_argument("--id", required=True)
    args = parser.parse_args(argv)
    return release(args.id)


__all__ = [
    "Change",
    "create_change",
    "new_change",
    "approve",
    "release",
    "impact",
    "cli_eco_new",
    "cli_eco_impact",
    "cli_eco_release",
    "ART_DIR",
    "_path",
]
