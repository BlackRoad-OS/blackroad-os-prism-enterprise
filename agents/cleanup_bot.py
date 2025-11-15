"""Utility for removing merged Git branches."""
"""Utilities for deleting merged Git branches."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from subprocess import CalledProcessError, CompletedProcess
from typing import Iterable, List

LOGGER = logging.getLogger(__name__)
from subprocess import CalledProcessError
from typing import List
import subprocess
from dataclasses import dataclass
from subprocess import CalledProcessError
from typing import Dict, List


@dataclass(frozen=True)
class BranchCleanupResult:
    """Outcome of deleting a branch locally and remotely."""

    branch: str
    local_deleted: bool
    remote_deleted: bool

    @property
    def success(self) -> bool:
        """Return ``True`` when the branch was removed locally and remotely."""
        return self.local_deleted and self.remote_deleted


@dataclass(frozen=True, slots=True)
class CleanupResult:
    """Result of attempting to delete a branch."""

    local_deleted: bool
    remote_deleted: bool
    skipped: bool = False


@dataclass
class CleanupBot:
    """Delete local and remote Git branches once work is merged."""

    branches: Iterable[str]
    """Delete local and remote branches after merges.

    Args:
        branches: Branch names to delete.
        dry_run: If True, print commands instead of executing them.
    """
    """Delete local and remote branches after merges."""

    branches: List[str]
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
    def _run(self, *cmd: str) -> subprocess.CompletedProcess:
        """Run a command unless in dry-run mode."""
        if self.dry_run:
            print("DRY-RUN:", " ".join(cmd))
            return subprocess.CompletedProcess(cmd, 0)
        return subprocess.run(cmd, check=True)

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
    def _run_git(self, *args: str) -> subprocess.CompletedProcess:
        """Execute a git command and return its result.

        Parameters
        ----------
        *args:
            Additional arguments passed directly to ``git``.

        Returns
        -------
        subprocess.CompletedProcess
            The completed process instance with captured output.
        """
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True)

    def delete_branch(self, branch: str) -> bool:
        """Attempt to delete a branch locally and remotely.

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
        Args:
            branch: The branch name to remove.

        Returns:
            True if the branch was deleted both locally and remotely, False otherwise.
        """
        success = True
    def _execute(self, *cmd: str) -> bool:
        """Execute a command and return ``True`` when it succeeds."""
        try:
            self._run(*cmd)
        except CalledProcessError:
            return False
        return True

    def delete_branch(self, branch: str) -> CleanupResult:
        """Delete a branch locally and remotely."""
        if self.dry_run:
            print(f"Would delete branch '{branch}' locally and remotely")
            return CleanupResult(local_deleted=False, remote_deleted=False, skipped=True)
        local_deleted = self._execute("git", "branch", "-D", branch)
        remote_deleted = False
        if local_deleted:
            remote_deleted = self._execute("git", "push", "origin", "--delete", branch)
        return CleanupResult(local_deleted=local_deleted, remote_deleted=remote_deleted)

    def cleanup(self) -> None:
    def cleanup(self) -> dict[str, CleanupResult]:
        """Remove the configured branches locally and remotely.
            self._run_git("branch", "-D", branch)
        except CalledProcessError:
            print(f"Failed to delete local branch '{branch}'")
            success = False
        try:
            self._run_git("push", "origin", "--delete", branch)
        except CalledProcessError:
            print(f"Failed to delete remote branch '{branch}'")
            success = False
        return success

    def cleanup(self) -> Dict[str, bool]:
        """Attempt to remove the configured branches locally and remotely.
    def _run_git(self, *args: str) -> tuple[bool, str | None]:
        """Execute a git command while respecting dry-run mode."""

        command = ["git", *args]
        if self.dry_run:
            print("DRY-RUN:", " ".join(command))
            return True, None
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else None
            return False, stderr
        return True, None

    def _delete_local_branch(self, branch: str) -> tuple[bool, str | None]:
        """Delete a local branch."""

        return self._run_git("branch", "-D", branch)

    def _delete_remote_branch(self, branch: str) -> tuple[bool, str | None]:
        """Delete a remote branch from ``origin``."""

        return self._run_git("push", "origin", "--delete", branch)

    def cleanup(self) -> List[BranchCleanupResult]:
        """Remove the configured branches locally and remotely."""

        results: List[BranchCleanupResult] = []
        for branch in self.branches:
            try:
                self._run("git", "branch", "-D", branch)
            except CalledProcessError:
                print(f"Local branch '{branch}' does not exist.")
            try:
                self._run("git", "push", "origin", "--delete", branch)
            except CalledProcessError:
                print(f"Remote branch '{branch}' does not exist.")
            if self.dry_run:
                print(f"Would delete branch '{branch}' locally and remotely")
                results[branch] = True
                continue
        Returns:
            Mapping of branch names to deletion results.
        """
        results: dict[str, CleanupResult] = {}
        for branch in self.branches:
            results[branch] = self.delete_branch(branch)
            local_deleted, local_error = self._delete_local_branch(branch)
            if not local_deleted and local_error:
                print(f"Failed to delete local branch '{branch}': {local_error}")

            remote_deleted, remote_error = self._delete_remote_branch(branch)
            if not remote_deleted and remote_error:
                print(f"Failed to delete remote branch '{branch}': {remote_error}")

            results.append(
                BranchCleanupResult(
                    branch=branch,
                    local_deleted=local_deleted,
                    remote_deleted=remote_deleted,
                )
            )
        return results


__all__ = ["CleanupBot"]
