from __future__ import annotations

"""Policy helpers for QLM Lab demos and agents."""

import os
from dataclasses import dataclass, field
"""Policy primitives for QLM Lab."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


def _default_artifact_dir() -> Path:
    """Return the default artifact directory for the lab."""

    return Path(__file__).resolve().parents[1] / "artifacts"


@dataclass
class Policy:
    """Runtime policy applied to tool-calling flows."""

    allow_network: bool = False
    artifact_dir: Path = field(default_factory=_default_artifact_dir)
    lineage_path: Path = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.artifact_dir, Path):
            self.artifact_dir = Path(self.artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        self.lineage_path = self.artifact_dir / "lineage.jsonl"
        self.lineage_path.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class Policy:
    """Runtime policy describing network and artifact constraints."""

    allow_network: bool = False
    max_artifacts_mb: int = 20


def artifact_paths(root: Path, patterns: Iterable[str]) -> List[Path]:
    """Resolve artifact paths relative to ``root``."""
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


    total_bytes = 0
    for path in paths:
        if path.exists():
            total_bytes += path.stat().st_size
    return total_bytes <= max_megabytes * 1_048_576


def ensure_required_artifacts(paths: Iterable[Path]) -> List[Path]:
    """Return the subset of ``paths`` that are missing on disk."""

    return [path for path in paths if not path.exists()]


def chsh_within_bounds(value: float, lower: float = 2.2, upper: float = 2.9) -> bool:
    """Validate that a CHSH score lies within the Bell violation band."""

    return lower < value <= upper


def coverage_thresholds_met(coverage: Mapping[str, float], minimum: float) -> bool:
    """Ensure all provided coverage values exceed the ``minimum`` threshold."""

    return all(value >= minimum for value in coverage.values())


def network_allowed(config: PolicyConfig | None = None) -> bool:
    """Determine whether network access is permitted by policy."""

    config = config or PolicyConfig()
    env_override = os.environ.get("QLAB_ALLOW_NETWORK")
    if env_override is not None:
        return env_override.lower() in {"1", "true", "yes"}
    return config.allow_network


__all__ = [
    "Policy",
    "PolicyConfig",
    "artifact_paths",
    "check_artifact_quota",
    "ensure_required_artifacts",
    "chsh_within_bounds",
    "coverage_thresholds_met",
    "network_allowed",
]
__all__ = ["Policy", "enforce_file_caps"]
