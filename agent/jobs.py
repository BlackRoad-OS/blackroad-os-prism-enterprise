"""Remote job execution helpers for the dashboard."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Optional


class RemoteJobError(RuntimeError):
    """Raised when a remote job fails to execute successfully."""

    def __init__(self, message: str, *, stderr: str = "", returncode: Optional[int] = None):
        super().__init__(message)
        self.stderr = stderr
        self.returncode = returncode


@dataclass
class RemoteJobResult:
    """Encapsulate stdout/stderr from a remote job."""

    command: str
    returncode: int
    stdout: str
    stderr: str


def _ssh_target(host: str, user: Optional[str]) -> str:
    return f"{user}@{host}" if user else host


def run_remote(host: str, command: str, *, user: Optional[str] = None, timeout: int = 60) -> RemoteJobResult:
    """Execute ``command`` on a remote host via SSH.

    The command is executed without invoking a shell on the local machine to avoid
    injection vulnerabilities. The remote host will still interpret the command
    string using its default shell, so callers should only pass vetted commands.
    """

    if not command.strip():
        raise ValueError("command must be a non-empty string")

    target = _ssh_target(host, user)
    ssh_command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={timeout}",
        target,
        command,
    ]

    result = subprocess.run(
        ssh_command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode != 0:
        raise RemoteJobError(
            f"remote command failed with exit code {result.returncode}",
            stderr=result.stderr,
            returncode=result.returncode,
        )

    return RemoteJobResult(
        command=command,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


__all__ = ["RemoteJobError", "RemoteJobResult", "run_remote"]
