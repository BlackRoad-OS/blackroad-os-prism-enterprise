"""Time Machine indexer for repository operational artifacts.

This module aggregates data from a variety of operational sources into a
single JSON index that can be consumed by downstream automation.

The script is intentionally defensive: all inputs are optional and missing or
malformed files are tolerated. Each section in the resulting JSON object will
be present even if the corresponding source is unavailable so that consumers do
not have to handle missing keys.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MAX_EMBEDDED_BYTES = 16_384


def _read_text(path: Path, limit: int = MAX_EMBEDDED_BYTES) -> str:
    data = path.read_bytes()[:limit]
    return data.decode("utf-8", errors="replace")


def _load_json(path: Optional[Path], default: Any) -> Any:
    if not path:
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to decode JSON from {path}") from exc


def _load_jsonl(path: Optional[Path]) -> List[Any]:
    if not path:
        return []
    try:
        lines: List[Any] = []
        with path.open("r", encoding="utf-8") as handle:
            for raw in handle:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    lines.append(json.loads(raw))
                except json.JSONDecodeError:
                    lines.append({"raw": raw})
        return lines
    except FileNotFoundError:
        return []


def _collect_directory_metadata(base: Optional[Path]) -> List[Dict[str, Any]]:
    if not base or not base.exists():
        return []

    results: List[Dict[str, Any]] = []
    for file_path in sorted(p for p in base.rglob("*") if p.is_file()):
        rel_path = file_path.relative_to(base).as_posix()
        stat = file_path.stat()
        entry: Dict[str, Any] = {
            "path": rel_path,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime(ISO_FORMAT),
        }

        if file_path.suffix.lower() in {".json", ".jsonl"} and stat.st_size <= MAX_EMBEDDED_BYTES:
            try:
                entry["data"] = json.loads(_read_text(file_path))
            except json.JSONDecodeError:
                entry["preview"] = _read_text(file_path)
        elif file_path.suffix.lower() in {".md", ".txt", ".log"}:
            entry["preview"] = _read_text(file_path)
        else:
            entry["preview"] = _read_text(file_path, limit=2048)

        results.append(entry)
    return results


def _resolve_path(path_str: Optional[str]) -> Optional[Path]:
    if not path_str:
        return None
    resolved = Path(path_str).expanduser().resolve()
    return resolved if resolved.exists() else resolved


def build_index(
    lh_path: Optional[Path] = None,
    ci_path: Optional[Path] = None,
    k6_path: Optional[Path] = None,
    run_meta_path: Optional[Path] = None,
    alerts_path: Optional[Path] = None,
    runtime_path: Optional[Path] = None,
    agents_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Build the consolidated time machine index."""

    index: Dict[str, Any] = {
        "generated_at": datetime.now(tz=timezone.utc).strftime(ISO_FORMAT),
        "lh": _load_json(lh_path, default={}),
        "ci": _load_json(ci_path, default={}),
        "k6": _load_json(k6_path, default={}),
        "sim": _load_json(run_meta_path, default={}),
        "alerts": _load_jsonl(alerts_path),
        "runtime": _collect_directory_metadata(runtime_path),
        "agents": _collect_directory_metadata(agents_path),
    }
    return index


def _parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Time Machine index")
    parser.add_argument("--lh", dest="lh", help="Path to Lighthouse history JSON")
    parser.add_argument("--ci", dest="ci", help="Path to CI runs JSON")
    parser.add_argument("--k6", dest="k6", help="Path to k6 summary JSON")
    parser.add_argument("--runmeta", dest="runmeta", help="Path to run_meta.json")
    parser.add_argument("--alerts", dest="alerts", help="Path to alerts JSONL stream")
    parser.add_argument("--runtime", dest="runtime", help="Directory of runtime logs")
    parser.add_argument("--agents", dest="agents", help="Directory for agent lineage data")
    parser.add_argument("--out", dest="out", required=True, help="Destination JSON file")
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = _parse_args(argv)
    index = build_index(
        lh_path=_resolve_path(args.lh),
        ci_path=_resolve_path(args.ci),
        k6_path=_resolve_path(args.k6),
        run_meta_path=_resolve_path(args.runmeta),
        alerts_path=_resolve_path(args.alerts),
        runtime_path=_resolve_path(args.runtime),
        agents_path=_resolve_path(args.agents),
    )

    out_path = Path(args.out).expanduser().resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
# tools/timemachine/index.py
# Usage:
#   python tools/timemachine/index.py \
#     --lh sites/blackroad/public/metrics/lh.json \
#     --ci sites/blackroad/public/metrics/ci.json \
#     --k6 logs/perf/k6_summary.json \
#     --runmeta run_meta.json \
#     --alerts data/aiops/alerts.jsonl \
#     --runtime logs/runtime \
#     --agents agents/lineage \
#     --out data/timemachine/index.json
from __future__ import annotations
import argparse, json, os, re, sys
from pathlib import Path
from datetime import datetime, timezone


def _read_text(p: Path) -> str | None:
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return None


def _read_json(p: Path):
    try:
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _ensure_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def parse_lighthouse(p: Path):
    j = _read_json(p)
    if not j:
        return {"history": []}
    # Accept either {"updatedAt":..., "history":[...]} or raw list
    hist = j.get("history", j if isinstance(j, list) else [])
    out = []
    for row in hist:
        try:
            out.append(
                {
                    "ts": row.get("ts"),
                    "perf": row.get("perf"),
                    "a11y": row.get("a11y"),
                    "bp": row.get("bp"),
                    "seo": row.get("seo"),
                    "LCP": row.get("LCP"),
                    "FCP": row.get("FCP"),
                    "CLS": row.get("CLS"),
                    "TBT": row.get("TBT"),
                    "notes": row.get("notes"),
                }
            )
        except Exception:
            continue
    return {"history": out}


def parse_ci(p: Path):
    j = _read_json(p)
    if not j:
        return {"runs": []}
    runs = j.get("runs", j.get("history", j))
    out = []
    for r in runs or []:
        out.append(
            {
                "ts": r.get("ts") or r.get("updatedAt"),
                "name": r.get("name") or r.get("workflow"),
                "conclusion": r.get("conclusion") or r.get("status"),
                "duration_ms": r.get("duration_ms") or r.get("durationMs"),
                "sha": r.get("sha"),
                "url": r.get("url") or r.get("html_url"),
            }
        )
    return {"runs": out}


def parse_k6(p: Path):
    j = _read_json(p)
    if not j:
        return {"components": [], "raw": None}
    metrics = j.get("metrics", j)
    comps = []
    re_comp = re.compile(r"http_req_duration\{component:([a-zA-Z0-9_\-]+)\}")
    for key, val in metrics.items():
        m = re_comp.match(key)
        if m and isinstance(val, dict):
            comp = m.group(1)
            p50 = val.get("med") or val.get("p(50)")
            p90 = val.get("p(90)")
            p95 = val.get("p(95)")
            comps.append({"component": comp, "p50": p50, "p90": p90, "p95": p95})
    # overall rates and checks if present
    http_reqs = metrics.get("http_reqs", {})
    checks = metrics.get("checks", {})
    summary = {
        "http_reqs_count": http_reqs.get("count"),
        "http_reqs_rate": http_reqs.get("rate"),
        "checks_passes": checks.get("passes"),
        "checks_fails": checks.get("fails"),
        "duration_avg": (metrics.get("http_req_duration") or {}).get("avg"),
        "duration_p95": (metrics.get("http_req_duration") or {}).get("p(95)"),
    }
    return {"components": comps, "summary": summary}


def parse_runmeta(p: Path):
    j = _read_json(p)
    if not j:
        return {"runs": []}
    # Single run_meta.json
    metrics = j.get("metrics", {})
    return {
        "runs": [
            {
                "run_id": j.get("run_id"),
                "generated_at": j.get("generated_at"),
                "solid": metrics.get("solid"),
                "fluid": metrics.get("fluid"),
                "artifacts": j.get("artifacts"),
            }
        ]
    }


def parse_alerts(p: Path):
    if not p.exists():
        return {"alerts": []}
    out = []
    for line in (_read_text(p) or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            j = json.loads(line)
            out.append(j)
        except Exception:
            continue
    return {"alerts": out}


def parse_runtime(dirp: Path):
    if not dirp.exists():
        return {"files": []}
    files = []
    for root, _, names in os.walk(dirp):
        for n in names:
            fp = Path(root) / n
            try:
                stat = fp.stat()
                files.append(
                    {
                        "path": str(fp),
                        "bytes": stat.st_size,
                        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    }
                )
            except Exception:
                continue
    return {"files": files}


def parse_agents(dirp: Path):
    if not dirp.exists():
        return {"items": []}
    items = []
    for root, _, names in os.walk(dirp):
        for n in names:
            fp = Path(root) / n
            if not fp.suffix.lower() in {".json", ".jsonl", ".md"}:
                continue
            size = fp.stat().st_size if fp.exists() else None
            items.append({"path": str(fp), "bytes": size})
    return {"items": items}


def main():
    ap = argparse.ArgumentParser(description="Build unified Time Machine index")
    ap.add_argument("--lh", type=Path, default=Path("sites/blackroad/public/metrics/lh.json"))
    ap.add_argument("--ci", type=Path, default=Path("sites/blackroad/public/metrics/ci.json"))
    ap.add_argument("--k6", type=Path, default=Path("logs/perf/k6_summary.json"))
    ap.add_argument("--runmeta", type=Path, default=Path("run_meta.json"))
    ap.add_argument("--alerts", type=Path, default=Path("data/aiops/alerts.jsonl"))
    ap.add_argument("--runtime", type=Path, default=Path("logs/runtime"))
    ap.add_argument("--agents", type=Path, default=Path("agents/lineage"))
    ap.add_argument("--out", type=Path, default=Path("data/timemachine/index.json"))
    args = ap.parse_args()

    out = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "lh": parse_lighthouse(args.lh),
        "ci": parse_ci(args.ci),
        "k6": parse_k6(args.k6),
        "sim": parse_runmeta(args.runmeta),
        "alerts": parse_alerts(args.alerts),
        "runtime": parse_runtime(args.runtime),
        "agents": parse_agents(args.agents),
    }
    _ensure_dir(args.out)
    args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    sys.exit(main())
