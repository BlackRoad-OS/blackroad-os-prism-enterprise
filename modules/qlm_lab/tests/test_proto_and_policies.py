from __future__ import annotations

import os
from pathlib import Path

import pytest

from qlm_lab import policies
from qlm_lab.policies import PolicyConfig
from qlm_lab.proto import Msg, new
from qlm_lab.tools import files


def test_message_factory_creates_unique_ids():
    m1 = new("a", "b", "task", "op1", foo=1)
    m2 = new("a", "b", "task", "op1", foo=1)
    assert m1.id != m2.id
    assert isinstance(m1, Msg)


def test_policy_helpers(tmp_path: Path):
    path = tmp_path / "artifact.txt"
    files.safe_write(path, "data")
    config = PolicyConfig(required_artifacts=["artifact.txt"], max_artifacts_mb=1.0)
    paths = policies.artifact_paths(tmp_path, config.required_artifacts)
    assert policies.ensure_required_artifacts(paths) == []
    assert policies.check_artifact_quota(paths, config.max_artifacts_mb)
    coverage = {"file": 0.95}
    assert policies.coverage_thresholds_met(coverage, 0.9)
    assert policies.chsh_within_bounds(2.3)


def test_network_allowed_env_override(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("QLAB_ALLOW_NETWORK", "true")
    assert policies.network_allowed(PolicyConfig(allow_network=False))


def test_file_helpers_enforce_quota(tmp_path: Path):
    path = tmp_path / "data.txt"
    files.safe_write(path, "hello", limit_bytes=10)
    assert files.safe_read(path, limit_bytes=10) == "hello"
    with pytest.raises(ValueError):
        files.safe_write(path, "x" * 20, limit_bytes=5)
    with pytest.raises(ValueError):
        files.safe_read(path, limit_bytes=2)
