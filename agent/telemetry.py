"""Utilities for collecting local and remote telemetry for the dashboard."""
from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Telemetry:
    """Structured representation of host telemetry for easier rendering."""

    hostname: str
    platform: str
    uptime_seconds: Optional[float]
    load_average: Optional[Dict[str, float]]
    disk: Optional[Dict[str, int]]
    raw: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        """Return a representation that can be fed to templates directly."""
        return {
            "hostname": self.hostname,
            "platform": self.platform,
            "uptime_seconds": self.uptime_seconds,
            "load_average": self.load_average,
            "disk": self.disk,
            "raw": self.raw,
        }


def _read_uptime() -> Optional[float]:
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as fh:
            first, *_ = fh.readline().split()
            return float(first)
    except (FileNotFoundError, OSError, ValueError):
        return None


def _collect_base_stats() -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "uptime_seconds": _read_uptime(),
    }

    if hasattr(os, "getloadavg"):
        try:
            load1, load5, load15 = os.getloadavg()
            data["load_average"] = {
                "1m": float(load1),
                "5m": float(load5),
                "15m": float(load15),
            }
        except OSError:
            data["load_average"] = None
    else:
        data["load_average"] = None

    try:
        usage = shutil.disk_usage("/")
        data["disk"] = {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
        }
    except OSError:
        data["disk"] = None

    return data


def collect_local() -> Telemetry:
    """Gather telemetry information for the host running the dashboard."""
    stats = _collect_base_stats()
    return Telemetry(
        hostname=stats.get("hostname", "unknown"),
        platform=stats.get("platform", "unknown"),
        uptime_seconds=stats.get("uptime_seconds"),
        load_average=stats.get("load_average"),
        disk=stats.get("disk"),
        raw=stats,
    )


_REMOTE_SCRIPT = """
import json
import os
import platform
import shutil
import socket


def read_uptime():
    try:
        with open('/proc/uptime', 'r', encoding='utf-8') as fh:
            first, *_ = fh.readline().split()
            return float(first)
    except Exception:  # pragma: no cover - defensive
        return None


def collect():
    data = {
        'hostname': socket.gethostname(),
        'platform': platform.platform(),
        'uptime_seconds': read_uptime(),
        'load_average': None,
        'disk': None,
    }

    if hasattr(os, 'getloadavg'):
        try:
            load1, load5, load15 = os.getloadavg()
            data['load_average'] = {
                '1m': float(load1),
                '5m': float(load5),
                '15m': float(load15),
            }
        except OSError:
            data['load_average'] = None

    try:
        usage = shutil.disk_usage('/')
        data['disk'] = {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
        }
    except OSError:
        data['disk'] = None

    return data

print(json.dumps(collect()))
""".strip()


def _run_ssh_command(
    host: str,
    user: Optional[str],
    args: list[str],
    *,
    timeout: int,
    input_data: Optional[str] = None,
) -> subprocess.CompletedProcess:
    target = f"{user}@{host}" if user else host
    base_cmd = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={timeout}",
        target,
    ]
    return subprocess.run(
        base_cmd + args,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        input=input_data,
    )


def collect_remote(host: str, *, user: Optional[str] = None, timeout: int = 10) -> Telemetry:
    """Collect telemetry from a remote host over SSH.

    Errors are captured and surfaced via the ``raw`` payload to keep the
    dashboard functional even when the remote host is unreachable.
    """

    result = _run_ssh_command(
        host,
        user,
        ["python3", "-"],
        timeout=timeout,
        input_data=_REMOTE_SCRIPT,
    )

    if result.returncode != 0:
        raw: Dict[str, Any] = {
            "error": "ssh_failed",
            "returncode": result.returncode,
            "stderr": result.stderr.strip(),
        }
        return Telemetry(
            hostname=host,
            platform="unknown",
            uptime_seconds=None,
            load_average=None,
            disk=None,
            raw=raw,
        )

    try:
        stats = json.loads(result.stdout)
    except json.JSONDecodeError:
        stats = {"error": "invalid_json", "stdout": result.stdout.strip()}

    if not isinstance(stats, dict):
        stats = {"error": "invalid_payload", "payload": stats}

    return Telemetry(
        hostname=stats.get("hostname", host),
        platform=stats.get("platform", "unknown"),
        uptime_seconds=stats.get("uptime_seconds"),
        load_average=stats.get("load_average"),
        disk=stats.get("disk"),
        raw=stats,
    )


__all__ = ["Telemetry", "collect_local", "collect_remote"]
