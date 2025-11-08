from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from orchestrator.consent import ConsentGrant, ConsentRegistry, ConsentRequest, ConsentType


def test_consent_lifecycle(tmp_path: Path) -> None:
    registry = ConsentRegistry(tmp_path / "consent.jsonl")
    request = ConsentRequest(
        from_agent="finance",
        to_agent="Treasury-BOT",
        consent_type=ConsentType.TASK_ASSIGNMENT,
        purpose="route treasury tasks",
        scope="TSK-*",
    )
    request_id = registry.request_consent(request)
    grant = ConsentGrant(
        request_id=request_id,
        granted_by="Treasury-BOT",
        granted_to="finance",
        consent_type=ConsentType.TASK_ASSIGNMENT,
        scope="TSK-*",
        conditions=("respond within 4 hours",),
        expires_at=datetime.utcnow() + timedelta(hours=1),
    )
    registry.grant_consent(grant)
    assert registry.check_consent("finance", ConsentType.TASK_ASSIGNMENT, "Treasury-BOT", "TSK-123")
    registry.revoke_consent(grant.grant_id, "finance")
    assert not registry.check_consent(
        "finance", ConsentType.TASK_ASSIGNMENT, "Treasury-BOT", "TSK-123"
    )


def test_consent_persistence(tmp_path: Path) -> None:
    path = tmp_path / "consent.jsonl"
    registry = ConsentRegistry(path)
    request = ConsentRequest(
        from_agent="finance",
        to_agent="Treasury-BOT",
        consent_type=ConsentType.DATA_ACCESS,
        purpose="audit", 
        scope="artifacts/treasury/*",
    )
    registry.request_consent(request)
    grant = ConsentGrant(
        request_id=request.request_id,
        granted_by="Treasury-BOT",
        granted_to="finance",
        consent_type=ConsentType.DATA_ACCESS,
        scope="artifacts/treasury/*",
    )
    registry.grant_consent(grant)

    reloaded = ConsentRegistry(path)
    assert reloaded.check_consent(
        "finance", ConsentType.DATA_ACCESS, "Treasury-BOT", "artifacts/treasury/forecast.json"
    )


def test_revoke_requires_participant(tmp_path: Path) -> None:
    registry = ConsentRegistry(tmp_path / "consent.jsonl")
    request = ConsentRequest(
        from_agent="finance",
        to_agent="Treasury-BOT",
        consent_type=ConsentType.TASK_ASSIGNMENT,
        purpose="run treasury bot",
    )
    registry.request_consent(request)
    grant = ConsentGrant(
        request_id=request.request_id,
        granted_by="Treasury-BOT",
        granted_to="finance",
        consent_type=ConsentType.TASK_ASSIGNMENT,
        scope="TSK-001",
    )
    registry.grant_consent(grant)
    with pytest.raises(PermissionError):
        registry.revoke_consent(grant.grant_id, "random-agent")
