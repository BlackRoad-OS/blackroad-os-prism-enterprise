"""Policy primitives for QLM Lab."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Policy:
    """Runtime policy describing network and artifact constraints."""

    allow_network: bool = False
    max_artifacts_mb: int = 20


def _iter_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def enforce_file_caps(artifacts_dir: str | Path, policy: Policy | None = None) -> None:
    """Raise ``RuntimeError`` if the total artifact size exceeds the policy cap."""

    policy = policy or Policy()
    root = Path(artifacts_dir)
    if not root.exists():
        return
    total_bytes = sum(path.stat().st_size for path in _iter_files(root))
    limit_bytes = policy.max_artifacts_mb * 1_048_576
    if total_bytes > limit_bytes:
        raise RuntimeError(
            f"artifact quota exceeded: {total_bytes} bytes > {limit_bytes} bytes"
        )


__all__ = ["Policy", "enforce_file_caps"]
