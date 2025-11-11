#!/usr/bin/env python3
"""Utilities for running the lightweight Codex deployment pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Tuple
from urllib import request

import requests
from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger("codex.pipeline")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

ERROR_LOG = Path("pipeline_errors.log")
LOG_FILE = Path("pipeline_validation.log")
LATEST_BACKUP = Path("/var/backups/blackroad/latest")
DROPLET_BACKUP = Path("/var/backups/blackroad/droplet")
CONNECTOR_ACTIONS = ("paste", "append", "replace", "restart", "build")


def run(cmd: str, *, dry_run: bool = False) -> None:
    """Execute ``cmd`` unless ``dry_run`` is enabled."""

    LOGGER.info("[cmd] %s", cmd)
    if dry_run:
        return
    subprocess.run(cmd, shell=True, check=True)


def log_error(stage: str, exc: Exception, rollback: bool, webhook: str | None) -> None:
    """Persist a pipeline failure and optionally notify a webhook."""

    timestamp = datetime.utcnow().isoformat()
    ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ERROR_LOG.open("a", encoding="utf-8") as handle:
        handle.write(f"{timestamp} [{stage}] {exc}\n")
        handle.write("ROLLBACK" if rollback else "NO-ROLLBACK")
        handle.write("\n")
    if webhook:
        payload = {"stage": stage, "error": str(exc), "rollback": rollback}
        try:
            requests.post(webhook, json=payload, timeout=5)
        except requests.RequestException:
            LOGGER.warning("Failed to post webhook notification", exc_info=True)


def rollback_from_backup() -> None:
    run(f"rsync -a {LATEST_BACKUP}/ ./")


def push_to_github() -> None:
    run("git push origin HEAD")


def deploy_to_droplet() -> None:
    run("deploy-to-droplet")


def _pipeline_call_connectors() -> None:
    run("connector-sync")


def _pipeline_validate_services() -> None:
    validate_services(run_probe=True)


def run_pipeline(*, force: bool = False, webhook: str | None = None) -> None:
    """Execute the default pipeline stages with rollback handling."""

    stages: Iterable[Tuple[str, Callable[[], None]]] = (
        ("push_to_github", push_to_github),
        ("deploy_to_droplet", deploy_to_droplet),
        ("call_connectors", _pipeline_call_connectors),
        ("validate_services", _pipeline_validate_services),
    )

    for stage_name, stage_func in stages:
        try:
            stage_func()
        except subprocess.CalledProcessError as exc:
            rollback = False
            if stage_name == "push_to_github":
                run("git reset --hard")
            elif stage_name == "deploy_to_droplet":
                rollback = True
                run(f"rsync -a {DROPLET_BACKUP}/ /srv/blackroad/")
            elif stage_name == "validate_services":
                rollback = True
                rollback_from_backup()
            log_error(stage_name, exc, rollback, webhook)
            if not force:
                raise


def push_latest(*, dry_run: bool = False) -> None:
    run("git push origin HEAD", dry_run=dry_run)


def refresh_working_copy(*, dry_run: bool = False) -> None:
    run("git fetch --all", dry_run=dry_run)
    run("git reset --hard origin/HEAD", dry_run=dry_run)


def redeploy_droplet(*, dry_run: bool = False) -> None:
    run("deploy-to-droplet", dry_run=dry_run)


def call_connectors(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke the hosted connector action with retry logic."""

    token = os.getenv("CONNECTOR_KEY")
    if not token:
        raise RuntimeError("CONNECTOR_KEY environment variable is required")

    url = f"https://blackroad.io/connectors/{action}"
    headers = {"Authorization": f"Bearer {token}"}

    for attempt in range(3):
        try:
            LOGGER.info("POST %s payload=%s", url, payload)
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            if data.get("ok") is True:
                return data
            LOGGER.error("Connector returned non-ok response: %s", data)
        except requests.RequestException as exc:
            LOGGER.error("Connector request failed: %s", exc)
        time.sleep(2**attempt)

    raise RuntimeError("Connector call failed after retries")


def sync_connectors(action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Public wrapper used by CLI invocations."""

    return call_connectors(action, payload)


def validate_services(*, run_probe: bool = False) -> Dict[str, str]:
    """Validate the public services and return a status summary."""

    if run_probe:
        run("validate-services")

    services = {
        "frontend": "https://blackroad.io/health/frontend",
        "api": "https://blackroad.io/health/api",
        "llm": "https://blackroad.io/health/llm",
        "math": "https://blackroad.io/health/math",
    }

    summary: Dict[str, str] = {}
    for name, url in services.items():
        try:
            with request.urlopen(url, timeout=5) as response:
                ok = response.getcode() == 200
                if ok:
                    body = response.read().decode("utf-8")
                    payload = json.loads(body or "{}")
                    ok = payload.get("status") == "ok"
        except Exception as exc:  # pragma: no cover - network failures
            LOGGER.warning("Health check failed for %s: %s", name, exc)
            ok = False
        summary[name] = "OK" if ok else "FAIL"

    summary["timestamp"] = datetime.utcnow().isoformat()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(summary) + "\n")
    return summary


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Codex pipeline utilities")
    parser.add_argument("--dry-run", action="store_true", help="print commands without executing")
    parser.add_argument("--skip-validate", action="store_true", help="skip health checks after commands")
    parser.add_argument("--force", action="store_true", help="continue pipeline after failures")
    parser.add_argument("--webhook", help="Webhook URL for error notifications")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("push", help="push commits and redeploy droplet")
    sub.add_parser("refresh", help="refresh working copy then redeploy")
    sub.add_parser("rebase", help="rebase from origin before redeploy")
    sync = sub.add_parser("sync", help="call a connector action")
    sync.add_argument("action", choices=CONNECTOR_ACTIONS)
    sync.add_argument("payload", help="JSON payload for the connector")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    if args.command is None:
        try:
            run_pipeline(force=args.force, webhook=args.webhook)
        except subprocess.CalledProcessError:
            return 1
        return 0

    if args.command == "push":
        push_latest(dry_run=args.dry_run)
        redeploy_droplet(dry_run=args.dry_run)
        if not args.skip_validate:
            validate_services()
        return 0

    if args.command == "refresh":
        push_latest(dry_run=args.dry_run)
        refresh_working_copy(dry_run=args.dry_run)
        redeploy_droplet(dry_run=args.dry_run)
        if not args.skip_validate:
            validate_services()
        return 0

    if args.command == "rebase":
        run("git pull --rebase", dry_run=args.dry_run)
        push_latest(dry_run=args.dry_run)
        redeploy_droplet(dry_run=args.dry_run)
        if not args.skip_validate:
            validate_services()
        return 0

    if args.command == "sync":
        payload = json.loads(args.payload)
        if args.dry_run:
            LOGGER.info("DRY RUN: would call %s with %s", args.action, payload)
        else:
            sync_connectors(args.action, payload)
        return 0

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
