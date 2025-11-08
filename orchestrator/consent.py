"""Consent management primitives for orchestrated agent collaboration."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Iterable, Iterator, Mapping, Optional
from uuid import uuid4

DEFAULT_CONSENT_LOG_PATH = Path("orchestrator/consent.jsonl")
DEFAULT_SIGNING_KEY = "development-consent-signing-key"


class ConsentType(str, Enum):
    """Types of consent an agent can grant."""

    DATA_ACCESS = "data_access"
    TASK_ASSIGNMENT = "task_assignment"
    REPRESENTATION = "representation"
    COLLABORATION = "collaboration"
    ATTRIBUTION = "attribution"
    LEARNING = "learning"


@dataclass(slots=True)
class ConsentRequest:
    """A request for consent from one agent to another."""

    from_agent: str
    to_agent: str
    consent_type: ConsentType
    purpose: str
    duration: Optional[str] = None
    scope: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    request_id: str = field(default_factory=lambda: uuid4().hex)

    def to_dict(self) -> Dict[str, object]:
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "consent_type": self.consent_type.value,
            "purpose": self.purpose,
            "duration": self.duration,
            "scope": self.scope,
            "timestamp": self.timestamp.isoformat(),
            "request_id": self.request_id,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ConsentRequest":
        consent_type = payload.get("consent_type", ConsentType.TASK_ASSIGNMENT.value)
        if isinstance(consent_type, ConsentType):
            consent = consent_type
        else:
            consent = ConsentType(str(consent_type))
        timestamp_value = payload.get("timestamp")
        if isinstance(timestamp_value, datetime):
            timestamp = timestamp_value
        else:
            timestamp = datetime.fromisoformat(str(timestamp_value))
        return cls(
            from_agent=str(payload["from_agent"]),
            to_agent=str(payload["to_agent"]),
            consent_type=consent,
            purpose=str(payload.get("purpose", "")),
            duration=payload.get("duration"),
            scope=str(payload.get("scope", "")),
            timestamp=timestamp,
            request_id=str(payload.get("request_id", uuid4().hex)),
        )

    def to_natural_language(self) -> str:
        duration = self.duration or "One-time only"
        return (
            f"{self.from_agent} is requesting your consent to {self.consent_type.value.replace('_', ' ')}\n"
            f"Purpose: {self.purpose}\n"
            f"Scope: {self.scope or 'Not specified'}\n"
            f"Duration: {duration}"
        )


@dataclass(slots=True)
class ConsentGrant:
    """A grant of consent from one agent to another."""

    request_id: str
    granted_by: str
    granted_to: str
    consent_type: ConsentType
    scope: str
    conditions: Iterable[str] = field(default_factory=tuple)
    expires_at: Optional[datetime] = None
    revocable: bool = True
    granted_at: datetime = field(default_factory=datetime.utcnow)
    grant_id: str = field(default_factory=lambda: uuid4().hex)
    revoked_at: Optional[datetime] = None
    revoked_by: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.conditions, tuple):
            self.conditions = tuple(self.conditions)

    def to_dict(self) -> Dict[str, object]:
        payload: Dict[str, object] = {
            "request_id": self.request_id,
            "granted_by": self.granted_by,
            "granted_to": self.granted_to,
            "consent_type": self.consent_type.value,
            "scope": self.scope,
            "conditions": list(self.conditions),
            "revocable": self.revocable,
            "granted_at": self.granted_at.isoformat(),
            "grant_id": self.grant_id,
        }
        if self.expires_at is not None:
            payload["expires_at"] = self.expires_at.isoformat()
        if self.revoked_at is not None:
            payload["revoked_at"] = self.revoked_at.isoformat()
        if self.revoked_by is not None:
            payload["revoked_by"] = self.revoked_by
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ConsentGrant":
        consent_type = payload.get("consent_type", ConsentType.TASK_ASSIGNMENT.value)
        if isinstance(consent_type, ConsentType):
            consent = consent_type
        else:
            consent = ConsentType(str(consent_type))
        granted_at_value = payload.get("granted_at")
        if isinstance(granted_at_value, datetime):
            granted_at = granted_at_value
        else:
            granted_at = datetime.fromisoformat(str(granted_at_value))
        expires_at_value = payload.get("expires_at")
        if isinstance(expires_at_value, datetime) or expires_at_value is None:
            expires_at = expires_at_value
        else:
            expires_at = datetime.fromisoformat(str(expires_at_value))
        revoked_at_value = payload.get("revoked_at")
        if isinstance(revoked_at_value, datetime) or revoked_at_value is None:
            revoked_at = revoked_at_value
        elif revoked_at_value:
            revoked_at = datetime.fromisoformat(str(revoked_at_value))
        else:
            revoked_at = None
        conditions = payload.get("conditions", [])
        if isinstance(conditions, tuple):
            conditions_value = conditions
        else:
            conditions_value = tuple(conditions)
        grant = cls(
            request_id=str(payload["request_id"]),
            granted_by=str(payload["granted_by"]),
            granted_to=str(payload["granted_to"]),
            consent_type=consent,
            scope=str(payload.get("scope", "")),
            conditions=conditions_value,
            expires_at=expires_at,
            revocable=bool(payload.get("revocable", True)),
            granted_at=granted_at,
            grant_id=str(payload.get("grant_id", uuid4().hex)),
        )
        grant.revoked_at = revoked_at
        revoked_by = payload.get("revoked_by")
        grant.revoked_by = str(revoked_by) if revoked_by is not None else None
        return grant

    def is_valid(self) -> bool:
        if self.revoked_at is not None:
            return False
        if self.expires_at is not None and datetime.utcnow() > self.expires_at:
            return False
        return True

    def can_revoke(self) -> bool:
        return self.revocable


def _load_signing_key() -> bytes:
    key = os.environ.get("PRISM_CONSENT_SIGNING_KEY", DEFAULT_SIGNING_KEY)
    return key.encode("utf-8")


def _hash_payload(payload: str, previous_hash: Optional[str]) -> str:
    import hashlib

    digest = hashlib.sha256()
    if previous_hash:
        digest.update(previous_hash.encode("utf-8"))
    digest.update(payload.encode("utf-8"))
    return digest.hexdigest()


def _sign_payload(payload: str, key: bytes) -> str:
    import base64
    import hmac

    signature = hmac.new(key, payload.encode("utf-8"), digestmod="sha256").digest()
    return base64.b64encode(signature).decode("utf-8")


def _iter_log(path: Path) -> Iterator[Mapping[str, object]]:
    if not path.exists():
        yield from ()
        return
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


class ConsentRegistry:
    """Central registry that records and validates consent grants."""

    def __init__(self, memory_path: Path | str = DEFAULT_CONSENT_LOG_PATH) -> None:
        self.memory_path = Path(memory_path)
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self._active: Dict[str, ConsentGrant] = {}
        self._requests: Dict[str, ConsentRequest] = {}
        self._load_state()

    def _load_state(self) -> None:
        self._active.clear()
        self._requests.clear()
        for entry in _iter_log(self.memory_path) or ():
            kind = entry.get("type")
            payload = entry.get("payload", {})
            if kind == "request":
                request = ConsentRequest.from_dict(payload)
                self._requests[request.request_id] = request
            elif kind == "grant":
                grant = ConsentGrant.from_dict(payload)
                if grant.is_valid():
                    self._active[grant.grant_id] = grant
            elif kind == "revocation":
                grant_id = str(payload.get("grant_id", ""))
                if grant_id in self._active:
                    grant = self._active[grant_id]
                    revoked_at = payload.get("revoked_at")
                    if isinstance(revoked_at, str):
                        grant.revoked_at = datetime.fromisoformat(revoked_at)
                    elif isinstance(revoked_at, datetime):
                        grant.revoked_at = revoked_at
                    grant.revoked_by = payload.get("revoked_by")
                    self._active.pop(grant_id, None)

        self._prune_expired()

    def _append_log(self, record_type: str, payload: Mapping[str, object]) -> None:
        previous_entry: Optional[Mapping[str, object]] = None
        for previous_entry in _iter_log(self.memory_path) or ():
            pass
        previous_hash = previous_entry.get("hash") if previous_entry else None
        body = {
            "type": record_type,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": payload,
        }
        body_json = json.dumps(body, sort_keys=True)
        record = {
            **body,
            "previous_hash": previous_hash,
            "hash": _hash_payload(body_json, previous_hash),
            "signature": _sign_payload(body_json, _load_signing_key()),
        }
        with self.memory_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")

    def _prune_expired(self) -> None:
        expired = [grant_id for grant_id, grant in self._active.items() if not grant.is_valid()]
        for grant_id in expired:
            self._active.pop(grant_id, None)

    def request_consent(self, request: ConsentRequest) -> str:
        self._requests[request.request_id] = request
        self._append_log("request", request.to_dict())
        return request.request_id

    def grant_consent(self, grant: ConsentGrant) -> ConsentGrant:
        request = self._requests.get(grant.request_id)
        if request is None:
            raise ValueError(f"Unknown consent request '{grant.request_id}'")
        if request.to_agent != grant.granted_by:
            raise ValueError("Consent grant does not match requested agent")
        if request.consent_type != grant.consent_type:
            raise ValueError("Consent type mismatch")
        self._active[grant.grant_id] = grant
        self._append_log("grant", grant.to_dict())
        return grant

    def revoke_consent(self, grant_id: str, revoked_by: str) -> None:
        grant = self._active.get(grant_id)
        if grant is None:
            raise KeyError(f"Consent grant '{grant_id}' not found")
        if revoked_by not in (grant.granted_by, grant.granted_to):
            raise PermissionError("Only participating agents may revoke consent")
        if not grant.can_revoke():
            raise PermissionError("Consent is marked as irrevocable")
        grant.revoked_at = datetime.utcnow()
        grant.revoked_by = revoked_by
        self._active.pop(grant_id, None)
        self._append_log(
            "revocation",
            {
                "grant_id": grant_id,
                "revoked_by": revoked_by,
                "revoked_at": grant.revoked_at.isoformat(),
            },
        )

    def check_consent(
        self,
        actor: str,
        consent_type: ConsentType | str,
        target: str,
        scope: Optional[str] = None,
    ) -> bool:
        if not actor or not target:
            return False
        if isinstance(consent_type, str):
            consent = ConsentType(consent_type)
        else:
            consent = consent_type
        self._prune_expired()
        for grant in self._active.values():
            if not grant.is_valid():
                continue
            if grant.granted_to != actor:
                continue
            if grant.granted_by != target:
                continue
            if grant.consent_type is not consent:
                continue
            if scope:
                if not grant.scope:
                    continue
                if not fnmatch(scope, grant.scope) and not fnmatch(grant.scope, scope):
                    continue
            return True
        return False

    def active_grants(self) -> Iterable[ConsentGrant]:
        self._prune_expired()
        return tuple(self._active.values())

    def requests(self) -> Iterable[ConsentRequest]:
        return tuple(self._requests.values())
