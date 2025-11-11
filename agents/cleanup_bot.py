"""Bot for cleaning up merged Git branches.

Provides :class:`CleanupBot` to delete local and remote branches after they
have been merged. Supports a dry-run mode to preview actions without
executing them.
"""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
from subprocess import CalledProcessError, CompletedProcess
from typing import Dict, List


@dataclass
class CleanupBot:
    """Delete local and remote branches after merges.

    Parameters
    ----------
    branches:
        Branch names to remove.
    dry_run:
        If ``True`` commands are printed instead of executed.
    """

    branches: List[str]
    dry_run: bool = False

    def _run(self, *cmd: str) -> CompletedProcess:
        """Run ``cmd`` unless in dry-run mode."""
        if self.dry_run:
            print("DRY-RUN:", " ".join(cmd))
            return CompletedProcess(cmd, 0)
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
        return result

    def _run_optional(self, *cmd: str) -> bool:
        """Run ``cmd`` and return success instead of raising."""
        try:
            self._run(*cmd)
        except CalledProcessError as error:
            message = (error.stderr or error.stdout or "").strip()
            if message:
                print(message)
            return False
        return True

    def _local_branch_exists(self, branch: str) -> bool:
        """Return ``True`` when ``branch`` exists locally."""
        if self.dry_run:
            return True
        result = subprocess.run(
            ("git", "rev-parse", "--verify", branch),
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def _remote_branch_exists(self, branch: str) -> bool:
        """Return ``True`` when ``branch`` exists on ``origin``."""
        if self.dry_run:
            return True
        result = subprocess.run(
            ("git", "ls-remote", "--heads", "origin", branch),
            capture_output=True,
            text=True,
        )
        return bool(result.stdout.strip())

    def delete_branch(self, branch: str) -> bool:
        """Delete a branch locally and remotely.

        Returns
        -------
        bool
            ``True`` if the branch was removed everywhere it existed,
            ``False`` otherwise.
        """
        local_deleted = True
        if self._local_branch_exists(branch):
            local_deleted = self._run_optional("git", "branch", "-D", branch)
            if not local_deleted:
                print(f"Failed to delete local branch '{branch}'.")
        else:
            print(f"Local branch '{branch}' already removed.")

        remote_deleted = True
        if self._remote_branch_exists(branch):
            remote_deleted = self._run_optional(
                "git", "push", "origin", "--delete", branch
            )
            if not remote_deleted:
                print(f"Failed to delete remote branch '{branch}'.")
        else:
            print(f"Remote branch '{branch}' already removed.")

        return local_deleted and remote_deleted

    def cleanup(self) -> Dict[str, bool]:
        """Remove configured branches locally and remotely."""
        results: Dict[str, bool] = {}
        for branch in self.branches:
            results[branch] = self.delete_branch(branch)
        return results


if __name__ == "__main__":
    print("CleanupBot ready to delete branches.")
