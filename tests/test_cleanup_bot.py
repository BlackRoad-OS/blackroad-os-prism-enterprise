"""Tests for :mod:`agents.cleanup_bot`."""

from subprocess import CalledProcessError

import pytest

from agents.cleanup_bot import CleanupBot


def test_cleanup_bot_executes_git_commands(monkeypatch: pytest.MonkeyPatch) -> None:
    """The bot should execute git commands for each branch."""

    bot = CleanupBot(["feature/new"], dry_run=False)
    calls: list[tuple[str, ...]] = []

    def fake_run(*cmd: str):
        calls.append(cmd)
        return None

    monkeypatch.setattr(bot, "_run", fake_run)

    results = bot.cleanup()

    assert results == {"feature/new": True}
    assert calls == [
        ("git", "branch", "-D", "feature/new"),
        ("git", "push", "origin", "--delete", "feature/new"),
    ]


def test_cleanup_bot_dry_run_prints_commands(capsys: pytest.CaptureFixture[str]) -> None:
    """Dry-run mode should log delete commands without executing them."""

    bot = CleanupBot(branches=["feature/awesome"], dry_run=True)

    results = bot.cleanup()

    captured = capsys.readouterr().out.strip().splitlines()
    assert captured == [
        "DRY-RUN: git branch -D feature/awesome",
        "DRY-RUN: git push origin --delete feature/awesome",
    ]
    assert results == {"feature/awesome": True}


def test_cleanup_bot_cleanup_handles_failures(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """``CleanupBot`` should mark branches as failed when git commands error."""

    bot = CleanupBot(branches=["bugfix/failure"], dry_run=False)
    calls: list[tuple[str, ...]] = []

    def failing_git(*args: str):
        calls.append(args)
        raise CalledProcessError(returncode=1, cmd=("git", *args))

    monkeypatch.setattr(bot, "_git", failing_git)

    results = bot.cleanup()

    assert results == {"bugfix/failure": False}
    captured = capsys.readouterr().out.strip().splitlines()
    assert captured == [
        "Failed to delete local branch 'bugfix/failure'",
        "Failed to delete branch 'bugfix/failure' locally or remotely",
    ]
    assert calls == [("branch", "-D", "bugfix/failure")]
