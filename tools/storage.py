"""Storage helpers for Prism console utilities."""
"""File-system backed storage helpers used by the console."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, Union

import yaml

BASE_DIR = Path.cwd()
CONFIG_ROOT = BASE_DIR / "config"
DATA_ROOT = BASE_DIR / "data"
READ_ONLY = os.environ.get("PRISM_READ_ONLY", "0") == "1"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write(path: Union[str, Path], content: Union[dict[str, Any], str]) -> None:
    target = Path(path)
    _ensure_parent(target)
    mode = "a" if target.suffix == ".jsonl" else "w"
    text = json.dumps(content) if isinstance(content, dict) else str(content)
    with target.open(mode, encoding="utf-8") as handle:
        if mode == "a":
            handle.write(text + "\n")
        else:
            handle.write(text)


def read(path: str) -> str:
def read(path: Union[str, Path]) -> str:
    target = Path(path)
    if not target.exists():
        return ""
    return target.read_text(encoding="utf-8")


def _resolve(path: str, root: Path) -> Path:
    return root / path


def read_json(path: str, *, from_data: bool = False) -> Any:
    root = DATA_ROOT if from_data else CONFIG_ROOT
    target = _resolve(path, root)
    if not from_data and not target.exists():
        target = BASE_DIR / path
    with target.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: str, data: Any, *, from_data: bool = True) -> None:
    if READ_ONLY:
        raise RuntimeError("read-only mode")
    root = DATA_ROOT if from_data else CONFIG_ROOT
    target = _resolve(path, root)
    _ensure_parent(target)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def append_jsonl(path: str, record: Any, *, from_data: bool = True) -> None:
    if READ_ONLY:
        raise RuntimeError("read-only mode")
    root = DATA_ROOT if from_data else CONFIG_ROOT
    target = _resolve(path, root)
    _ensure_parent(target)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def read_jsonl(path: str, *, from_data: bool = True) -> Iterable[Any]:
    root = DATA_ROOT if from_data else CONFIG_ROOT
    target = _resolve(path, root)
    if not target.exists():
        return []
    with target.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def read_yaml(path: str, *, from_data: bool = False) -> Any:
    root = DATA_ROOT if from_data else CONFIG_ROOT
    target = _resolve(path, root)
    if not from_data and not target.exists():
        target = BASE_DIR / path
    with target.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def read_text(path: str, *, from_data: bool = False) -> str:
    root = DATA_ROOT if from_data else CONFIG_ROOT
    target = _resolve(path, root)
    if not from_data and not target.exists():
        target = BASE_DIR / path
    return target.read_text(encoding="utf-8")
    with target.open("r", encoding="utf-8") as handle:
        return handle.read()


def write_text(path: str, text: str, *, from_data: bool = False) -> None:
    if READ_ONLY:
        raise RuntimeError("read-only mode")
    root = DATA_ROOT if from_data else CONFIG_ROOT
    target = _resolve(path, root)
    _ensure_parent(target)
    target.write_text(text, encoding="utf-8")


def save(path: str, content: bytes) -> None:
    raise NotImplementedError("Storage adapter not implemented. TODO: connect to object store")


def load_json(path: Path, default: Any) -> Any:
    with target.open("w", encoding="utf-8") as handle:
        handle.write(text)


def save(path: str, content: bytes) -> None:
    """Stubbed storage write used by legacy callers."""

    raise NotImplementedError(
        "Storage adapter not implemented. TODO: connect to object store"
    )


def load_json(path: Path, default: Any) -> Any:
    """Load JSON data from *path* if it exists, otherwise return *default*."""

    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    return default


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    """Persist *data* as JSON to *path*."""

    _ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, default=str)


__all__ = [
    "write",
    "read",
    "read_json",
    "write_json",
    "append_jsonl",
    "read_jsonl",
    "read_yaml",
    "read_text",
    "write_text",
    "save",
    "load_json",
    "save_json",
]

