"""Utility for removing merged Git branches."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from subprocess import CalledProcessError, CompletedProcess
from typing import Iterable, List

LOGGER = logging.getLogger(__name__)


@dataclass
class CleanupBot:
    """Delete local and remote Git branches once work is merged."""

    branches: Iterable[str]
    dry_run: bool = False
    remote: str = "origin"
    _normalized_branches: List[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Normalise the provided branch names."""

        seen: set[str] = set()
        normalized: List[str] = []
        for raw_name in self.branches:
            name = raw_name.strip()
            if not name or name in seen:
                continue
            if name == "HEAD":  # pragma: no cover - defensive guard
                continue
            seen.add(name)
            normalized.append(name)
        self._normalized_branches = normalized
        self.branches = list(normalized)

    @staticmethod
    def merged_branches(base: str = "main") -> List[str]:
        """Return the names of branches merged into ``base``."""

        try:
            result = subprocess.run(
                ["git", "branch", "--merged", base],
                capture_output=True,
                text=True,
                check=True,
            )
        except CalledProcessError as exc:  # pragma: no cover - command failure
            LOGGER.error("Failed to list merged branches", exc_info=exc)
            raise RuntimeError("Could not list merged branches") from exc

        branches: List[str] = []
        for line in result.stdout.splitlines():
            name = line.strip().lstrip("*").strip()
            if not name or name == base:
                continue
            branches.append(name)
        return branches

    @classmethod
    def from_merged(cls, base: str = "main", *, dry_run: bool = False) -> "CleanupBot":
        """Construct a bot configured with branches merged into ``base``."""

        return cls(branches=cls.merged_branches(base), dry_run=dry_run)

    def _run(self, *cmd: str) -> CompletedProcess[str] | None:
        """Execute ``cmd`` unless running in dry-run mode."""

        if self.dry_run:
            LOGGER.info("DRY-RUN %s", " ".join(cmd))
            return None
        LOGGER.debug("Executing: %s", " ".join(cmd))
        return subprocess.run(cmd, check=True, text=True, capture_output=True)

    def delete_local(self, branch: str) -> None:
        """Delete the local branch if it exists."""

        self._run("git", "branch", "-d", branch)

    def delete_remote(self, branch: str) -> None:
        """Delete the remote branch if it exists."""

        self._run("git", "push", self.remote, "--delete", branch)

    def execute(self) -> None:
        """Remove all configured branches locally and remotely."""

        for branch in self._normalized_branches:
            try:
                self.delete_local(branch)
            except CalledProcessError as exc:  # pragma: no cover - logging only
                LOGGER.warning("Unable to delete local branch %s", branch, exc_info=exc)
            try:
                self.delete_remote(branch)
            except CalledProcessError as exc:  # pragma: no cover - logging only
                LOGGER.warning("Unable to delete remote branch %s", branch, exc_info=exc)


__all__ = ["CleanupBot"]
