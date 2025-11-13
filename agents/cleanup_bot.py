"""Bot for cleaning up merged Git branches."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from subprocess import CalledProcessError
from typing import Dict, List


@dataclass
class CleanupBot:
    """Delete local and remote branches after merges.

    Parameters
    ----------
    branches:
        A list of branch names to remove.
    dry_run:
        When ``True`` the bot only prints the operations it would perform
        without issuing git commands.
    """

    branches: List[str]
    dry_run: bool = False

    def _run_git(self, *args: str) -> subprocess.CompletedProcess:
        """Run ``git`` with the provided arguments.

        Returns the :class:`subprocess.CompletedProcess` for callers that need
        access to ``stdout`` or ``stderr``. The underlying ``CalledProcessError``
        is allowed to propagate so the caller can decide how to handle failures.
        """
        return subprocess.run(["git", *args], check=True, capture_output=True, text=True)

    def delete_branch(self, branch: str) -> bool:
        """Delete ``branch`` locally and remotely when possible.

        The method keeps attempting both deletions even if the first fails and
        prints a short message for each unsuccessful step. A ``True`` return
        value means both attempts succeeded, while ``False`` indicates at least
        one failure.
        """
        success = True
        try:
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
        """Attempt to remove each configured branch and report the outcome.

        The returned mapping stores ``True`` when both local and remote
        deletions succeed. When ``dry_run`` is enabled every branch is mapped to
        ``True`` to reflect that the deletions would be attempted without
        modifying the repository.
        """
        results: Dict[str, bool] = {}
        for branch in self.branches:
            if self.dry_run:
                print(f"Would delete branch '{branch}' locally and remotely")
                results[branch] = True
                continue
            results[branch] = self.delete_branch(branch)
        return results


if __name__ == "__main__":
    print("CleanupBot ready to delete branches.")
