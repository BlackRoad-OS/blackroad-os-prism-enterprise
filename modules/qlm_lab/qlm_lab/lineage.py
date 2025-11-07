"""Artifact lineage logging utilities for QLM Lab."""
from __future__ import annotations

from json import dumps
from pathlib import Path
from typing import Any, Dict, List

ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / "artifacts"
LINEAGE_PATH = ARTIFACTS_DIR / "lineage.jsonl"


DEFAULT_LINEAGE_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "lineage.jsonl"


def append(event: dict[str, object], path: Path | None = None) -> None:
    """Append a lightweight lineage ``event`` to the JSONL log."""

    target = Path(path) if path is not None else DEFAULT_LINEAGE_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(event, default=str)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")



@dataclass
class LineageRecord:
    """Serializable lineage record for agent activity."""
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


    @property
    def records(self) -> List[LineageRecord]:
        return list(self._records)


__all__ = ["LineageLogger", "LineageRecord", "append"]
__all__ = ["append", "artifact_index", "ARTIFACTS_DIR", "LINEAGE_PATH"]
