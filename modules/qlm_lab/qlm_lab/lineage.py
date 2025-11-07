"""Artifact lineage logging utilities for QLM Lab."""
from __future__ import annotations

from json import dumps
from pathlib import Path
from typing import Any, Dict, List

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
LINEAGE_PATH = ARTIFACTS_DIR / "lineage.jsonl"


def _coerce(value: Any) -> Any:
    """Convert values into JSON-serialisable primitives."""

    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _coerce(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_coerce(item) for item in value]
    return value


def append(event: Dict[str, Any]) -> Path:
    """Append ``event`` to the lineage JSONL log."""

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = _coerce(event)
    with LINEAGE_PATH.open("a", encoding="utf-8") as handle:
        handle.write(dumps(payload, sort_keys=True) + "\n")
    return LINEAGE_PATH


def artifact_index() -> Dict[str, Any]:
    """Return a summary of known artifacts within the lab."""

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    files: List[str] = sorted(
        entry.name for entry in ARTIFACTS_DIR.iterdir() if entry.is_file()
    )
    return {"count": len(files), "files": files}


__all__ = ["append", "artifact_index", "ARTIFACTS_DIR", "LINEAGE_PATH"]
