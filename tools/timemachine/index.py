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
