"""Lineage logging utilities."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List

from .proto import Msg


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

    message: Msg
    note: str | None = None

    def to_json(self) -> str:
        payload = asdict(self)
        payload["message"]["ts"] = float(self.message.ts)
        return json.dumps(payload, default=str)


class LineageLogger:
    """Persist lineage events to a JSONL file."""

    def __init__(self, path: str | Path | None = None):
        default_path = Path(__file__).resolve().parents[1] / "artifacts" / "lineage.jsonl"
        self.path = Path(path) if path is not None else default_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._records: List[LineageRecord] = []

    def log(self, message: Msg, note: str | None = None) -> None:
        record = LineageRecord(message=message, note=note)
        self._records.append(record)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(record.to_json() + "\n")

    def load(self) -> List[LineageRecord]:
        """Load records from disk, replacing in-memory cache."""

        records: List[LineageRecord] = []
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        raw = json.loads(line)
                        msg = Msg(**raw["message"])
                        records.append(LineageRecord(message=msg, note=raw.get("note")))
        self._records = records
        return list(self._records)

    @property
    def records(self) -> List[LineageRecord]:
        return list(self._records)


__all__ = ["LineageLogger", "LineageRecord", "append"]
