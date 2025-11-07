"""Policy helpers for QLM Lab demos and agents."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Mapping


@dataclass
class PolicyConfig:
    """Configuration for runtime policy enforcement."""

    allow_network: bool = False
    max_artifacts_mb: float = 20.0
    required_artifacts: List[str] = field(default_factory=list)


def artifact_paths(root: Path, patterns: Iterable[str]) -> List[Path]:
    """Resolve artifact paths relative to ``root``.

    Missing paths are returned as-is so callers can report the failure.
    """

    resolved: List[Path] = []
    for pattern in patterns:
        path = root / pattern
        resolved.append(path)
    return resolved


def check_artifact_quota(paths: Iterable[Path], max_megabytes: float) -> bool:
    """Return ``True`` if the combined size of ``paths`` is within quota."""

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
    "PolicyConfig",
    "artifact_paths",
    "check_artifact_quota",
    "ensure_required_artifacts",
    "chsh_within_bounds",
    "coverage_thresholds_met",
    "network_allowed",
]
