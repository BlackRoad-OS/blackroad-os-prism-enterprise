"""Utility bot for cleaning up merged Git branches."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from subprocess import CalledProcessError, CompletedProcess, run
from typing import Dict, Iterable, List, Sequence


@dataclass
class CleanupBot:
    """Delete local and remote Git branches once work is merged."""

    branches: Iterable[str]
    dry_run: bool = False
    _normalized_branches: List[str] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Normalise the provided branch names."""

        seen: set[str] = set()
        normalized: List[str] = []
        for raw_name in self.branches:
            name = raw_name.strip()
            if not name or name in seen:
                continue
            seen.add(name)
            normalized.append(name)
        self._normalized_branches = normalized
        self.branches = list(normalized)

    @staticmethod
    def merged_branches(base: str = "main") -> List[str]:
        """Return the names of branches merged into ``base``."""

        try:
            result = run(
                ["git", "branch", "--merged", base],
                capture_output=True,
                text=True,
                check=True,
            )
        except CalledProcessError as exc:  # pragma: no cover - defensive guard
            raise RuntimeError("Could not list merged branches") from exc

        branches: List[str] = []
        for line in result.stdout.splitlines():
            name = line.strip().lstrip("*").strip()
            if not name or name in {base, "HEAD"}:
                continue
            branches.append(name)
        return branches

    @classmethod
    def from_merged(cls, base: str = "main", dry_run: bool = False) -> "CleanupBot":
        """Construct a bot for branches merged into ``base``."""

        return cls(branches=cls.merged_branches(base), dry_run=dry_run)

    def _run(self, *cmd: str) -> CompletedProcess | None:
        """Execute ``cmd`` unless running in dry-run mode."""

        if self.dry_run:
            print(f"DRY-RUN: {' '.join(cmd)}")
            return None
        return run(cmd, check=True)

    def _git(self, *args: str) -> CompletedProcess | None:
        """Run a ``git`` command, respecting the dry-run flag."""

        return self._run("git", *args)

    def delete_branch(self, branch: str) -> bool:
        """Delete ``branch`` locally and on ``origin``."""

        if self.dry_run:
            self._git("branch", "-D", branch)
            self._git("push", "origin", "--delete", branch)
            return True

        try:
            self._git("branch", "-D", branch)
        except CalledProcessError:
            print(f"Failed to delete local branch '{branch}'")
            return False

        try:
            self._git("push", "origin", "--delete", branch)
        except CalledProcessError:
            print(f"Failed to delete remote branch '{branch}'")
            return False

        return True

    def cleanup(self) -> Dict[str, bool]:
        """Delete all configured branches."""

        results: Dict[str, bool] = {}
        for branch in self._normalized_branches:
            success = self.delete_branch(branch)
            results[branch] = success
        return results


def cleanup(branches: Iterable[str], dry_run: bool = False) -> Dict[str, bool]:
    """Convenience wrapper around :class:`CleanupBot`."""

    return CleanupBot(branches=branches, dry_run=dry_run).cleanup()


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "branches",
        nargs="*",
        help="Branch names to delete. If omitted, branches merged into --base are used.",
    )
    parser.add_argument(
        "--base",
        default="main",
        help="Base branch used to detect merged branches when none are provided.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show commands without executing them.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the CleanupBot CLI."""

    args = _parse_args(argv)
    branches = args.branches if args.branches is not None else CleanupBot.merged_branches(args.base)
    bot = CleanupBot(branches=branches, dry_run=args.dry_run)
    results = bot.cleanup()
    failures = [name for name, success in results.items() if not success]
    return 0 if not failures else 1


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
