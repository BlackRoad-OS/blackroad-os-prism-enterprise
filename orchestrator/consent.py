"""Consent management primitives for orchestrated agent collaboration."""

from __future__ import annotations

import base64
import json
import os
import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Iterable, Iterator, Mapping, Optional, Sequence
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
from typing import Iterable, Mapping, Sequence

from orchestrator.exceptions import ConsentError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_utc(moment: datetime | None) -> datetime | None:
    if moment is None:
        return None
    if moment.tzinfo is None:
        return moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)


def _normalise_scope(scope: str | Sequence[str] | None) -> tuple[str, ...]:
    if scope is None:
        return tuple()
    if isinstance(scope, str):
        if not scope:
            return tuple()
        return (scope,)
    return tuple(str(item) for item in scope if str(item))


_DURATION_PATTERN = re.compile(r"(?P<value>\d+)(?P<unit>[smhdw])", re.IGNORECASE)
_DURATION_FACTORS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}


def _parse_duration(value: str | timedelta | None) -> timedelta | None:
    if value is None:
        return None
    if isinstance(value, timedelta):
        return value
    if not isinstance(value, str):  # pragma: no cover - defensive
        raise TypeError("duration must be str or timedelta")
    seconds = 0
    for match in _DURATION_PATTERN.finditer(value.strip().lower()):
        factor = _DURATION_FACTORS[match.group("unit")]
        seconds += int(match.group("value")) * factor
    if seconds == 0:
        raise ValueError(f"invalid duration: {value!r}")
    return timedelta(seconds=seconds)


def _format_duration(duration: timedelta | None) -> str | None:
    if duration is None:
        return None
    remaining = int(duration.total_seconds())
    components: list[str] = []
    for unit, factor in ("w", 604800), ("d", 86400), ("h", 3600), ("m", 60), ("s", 1):
        if remaining >= factor:
            value, remaining = divmod(remaining, factor)
            if value:
                components.append(f"{value}{unit}")
    if not components:
        components.append("0s")
    return "".join(components)


def _ps_shainfty(data: str) -> str:
    """Return a deterministic PS-SHA∞ signature for *data*."""

    payload = data.encode("utf-8")
    sha3 = __import__("hashlib").sha3_512(payload).digest()
    sha2 = __import__("hashlib").sha512(sha3 + payload).digest()
    blake = __import__("hashlib").blake2b(sha2 + sha3, digest_size=32).digest()
    combined = sha3 + sha2 + blake
    return base64.urlsafe_b64encode(combined).decode("ascii").rstrip("=")


def _serialise_payload(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


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


@dataclass
class ConsentRequest:
    """Structured payload describing a consent negotiation."""

    request_id: str
    from_agent: str
    to_agent: str
    consent_type: str
    purpose: str
    duration: timedelta | None
    scope: tuple[str, ...]
    created_at: datetime = field(default_factory=_utcnow)
    signature: str = field(init=False)

    def __post_init__(self) -> None:
        self.from_agent = self.from_agent.strip()
        self.to_agent = self.to_agent.strip()
        self.consent_type = self.consent_type.strip()
        self.purpose = self.purpose.strip()
        self.duration = _parse_duration(self.duration)
        self.scope = _normalise_scope(self.scope)
        self.created_at = _ensure_utc(self.created_at) or _utcnow()
        self.signature = self._compute_signature()

    def _compute_signature(self) -> str:
        payload = self._signature_payload()
        return _ps_shainfty(_serialise_payload(payload))

    def _signature_payload(self) -> Mapping[str, object]:
        return {
            "created_at": self.created_at.isoformat(),
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.consent_type,
            "purpose": self.purpose,
            "duration": _format_duration(self.duration),
            "scope": list(self.scope),
        }

    def to_natural_language(self) -> str:
        scope_text = ", ".join(self.scope) if self.scope else "defined scope"
        duration_text = (
            f"for {_format_duration(self.duration)}"
            if self.duration is not None
            else "until revoked"
        )
        return (
            f"{self.from_agent} requests {self.consent_type} consent from {self.to_agent} "
            f"to {self.purpose} within {scope_text} {duration_text}."
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "consent_type": self.consent_type,
            "purpose": self.purpose,
            "duration": _format_duration(self.duration),
            "scope": list(self.scope),
            "created_at": self.created_at.isoformat(),
            "signature": self.signature,
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
        duration_raw = payload.get("duration")
        created_raw = payload.get("created_at")
        created_at = (
            datetime.fromisoformat(str(created_raw)) if created_raw is not None else _utcnow()
        )
        request = cls(
            request_id=str(payload["request_id"]),
            from_agent=str(payload["from_agent"]),
            to_agent=str(payload["to_agent"]),
            consent_type=str(payload["consent_type"]),
            purpose=str(payload["purpose"]),
            duration=_parse_duration(duration_raw) if duration_raw else None,
            scope=tuple(payload.get("scope", ())),
            created_at=_ensure_utc(created_at) or _utcnow(),
        )
        if request.signature != payload.get("signature"):
            raise ConsentError("consent request signature verification failed")
        return request


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
    """Represents an approved consent request."""

    grant_id: str
    request_id: str
    from_agent: str
    to_agent: str
    consent_type: str
    scope: tuple[str, ...]
    conditions: tuple[str, ...]
    expires_at: datetime | None
    revocable: bool
    issued_at: datetime = field(default_factory=_utcnow)
    revoked_at: datetime | None = None
    revocation_reason: str | None = None
    signature: str = field(init=False)

    def __post_init__(self) -> None:
        self.scope = _normalise_scope(self.scope)
        self.conditions = tuple(self.conditions)
        self.expires_at = _ensure_utc(self.expires_at)
        self.issued_at = _ensure_utc(self.issued_at) or _utcnow()
        self.revoked_at = _ensure_utc(self.revoked_at)
        self.signature = self._compute_signature()

    def _compute_signature(self) -> str:
        payload = self._signature_payload()
        return _ps_shainfty(_serialise_payload(payload))

    def _signature_payload(self) -> Mapping[str, object]:
        return {
            "grant_id": self.grant_id,
            "request_id": self.request_id,
            "from": self.from_agent,
            "to": self.to_agent,
            "type": self.consent_type,
            "scope": list(self.scope),
            "conditions": list(self.conditions),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revocable": self.revocable,
            "issued_at": self.issued_at.isoformat(),
        }

    def is_valid(self, moment: datetime | None = None) -> bool:
        if self.revoked_at is not None:
            return False
        moment = _ensure_utc(moment) or _utcnow()
        if self.expires_at is None:
            return True
        return moment <= self.expires_at

    def can_revoke(self) -> bool:
        return self.revocable and self.revoked_at is None

    def matches(self, from_agent: str, to_agent: str, consent_type: str) -> bool:
        from_matches = self.from_agent in {from_agent, "*"} or from_agent == "*"
        to_matches = self.to_agent in {to_agent, "*"} or to_agent == "*"
        type_matches = self.consent_type == consent_type
        return from_matches and to_matches and type_matches

    def scope_includes(self, required: Sequence[str]) -> bool:
        if not required:
            return True
        if "*" in self.scope:
            return True
        return all(item in self.scope for item in required)

    def to_dict(self) -> dict[str, object]:
        return {
            "grant_id": self.grant_id,
            "request_id": self.request_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "consent_type": self.consent_type,
            "scope": list(self.scope),
            "conditions": list(self.conditions),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "revocable": self.revocable,
            "issued_at": self.issued_at.isoformat(),
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "revocation_reason": self.revocation_reason,
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "ConsentGrant":
        grant = cls(
            grant_id=str(payload["grant_id"]),
            request_id=str(payload["request_id"]),
            from_agent=str(payload["from_agent"]),
            to_agent=str(payload["to_agent"]),
            consent_type=str(payload["consent_type"]),
            scope=tuple(payload.get("scope", [])),
            conditions=tuple(payload.get("conditions", [])),
            expires_at=(
                datetime.fromisoformat(str(payload["expires_at"]))
                if payload.get("expires_at")
                else None
            ),
            revocable=bool(payload.get("revocable", True)),
            issued_at=(
                datetime.fromisoformat(str(payload["issued_at"]))
                if payload.get("issued_at")
                else _utcnow()
            ),
            revoked_at=(
                datetime.fromisoformat(str(payload["revoked_at"]))
                if payload.get("revoked_at")
                else None
            ),
            revocation_reason=payload.get("revocation_reason"),
        )
        if grant.signature != payload.get("signature"):
            raise ConsentError("consent grant signature verification failed")
        return grant


class ConsentRegistry:
    """Manage consent lifecycle and audit logging."""

    _default_lock = threading.Lock()
    _default_registry: "ConsentRegistry" | None = None

    def __init__(self, log_path: Path | None = None) -> None:
        env_path = os.environ.get("PRISM_CONSENT_LOG")
        base_path = (
            Path(log_path)
            if log_path is not None
            else Path(env_path)
            if env_path
            else Path(__file__).resolve().parent / "consent.jsonl"
        )
        self.log_path = base_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._requests: dict[str, ConsentRequest] = {}
        self._grants: dict[str, ConsentGrant] = {}
        self._lock = threading.RLock()
        self._load()

    @classmethod
    def get_default(cls) -> "ConsentRegistry":
        with cls._default_lock:
            if cls._default_registry is None:
                cls._default_registry = cls()
            return cls._default_registry

    @classmethod
    def reset_default(cls) -> None:
        with cls._default_lock:
            cls._default_registry = None

    def request_consent(
        self,
        *,
        from_agent: str,
        to_agent: str,
        consent_type: str,
        purpose: str,
        duration: str | timedelta | None = None,
        scope: str | Sequence[str] | None = None,
    ) -> str:
        with self._lock:
            request_id = f"req_{uuid.uuid4().hex}"[:16]
            request = ConsentRequest(
                request_id=request_id,
                from_agent=from_agent,
                to_agent=to_agent,
                consent_type=consent_type,
                purpose=purpose,
                duration=_parse_duration(duration) if duration else None,
                scope=_normalise_scope(scope),
            )
            self._requests[request.request_id] = request
            self._append_log({"type": "request", "request": request.to_dict()})
            return request.request_id

    def get_request(self, request_id: str) -> ConsentRequest:
        with self._lock:
            try:
                return self._requests[request_id]
            except KeyError as exc:  # pragma: no cover - defensive guard
                raise ConsentError(f"unknown consent request '{request_id}'") from exc

    def grant_consent(
        self,
        request_id: str,
        *,
        conditions: Iterable[str] | None = None,
        expires_in: str | timedelta | None = None,
        expires_at: datetime | None = None,
        revocable: bool = True,
    ) -> str:
        with self._lock:
            try:
                request = self._requests[request_id]
            except KeyError as exc:
                raise ConsentError(f"unknown consent request '{request_id}'") from exc

            grant_id = f"grant_{uuid.uuid4().hex}"[:18]
            expiry_candidate = expires_at or (
                request.created_at + request.duration if request.duration else None
            )
            if expires_in is not None:
                expiry_candidate = _utcnow() + _parse_duration(expires_in)
            grant = ConsentGrant(
                grant_id=grant_id,
                request_id=request.request_id,
                from_agent=request.from_agent,
                to_agent=request.to_agent,
                consent_type=request.consent_type,
                scope=request.scope,
                conditions=tuple(conditions or ()),
                expires_at=expiry_candidate,
                revocable=revocable,
            )
            self._grants[grant.grant_id] = grant
            self._append_log({"type": "grant", "grant": grant.to_dict()})
            return grant.grant_id

    def get_grant(self, grant_id: str) -> ConsentGrant:
        with self._lock:
            try:
                return self._grants[grant_id]
            except KeyError as exc:  # pragma: no cover - defensive guard
                raise ConsentError(f"unknown consent grant '{grant_id}'") from exc

    def revoke_consent(
        self, grant_id: str, *, reason: str | None = None, revoked_at: datetime | None = None
    ) -> None:
        with self._lock:
            try:
                grant = self._grants[grant_id]
            except KeyError as exc:
                raise ConsentError(f"unknown consent grant '{grant_id}'") from exc
            if not grant.can_revoke():
                raise ConsentError(f"grant '{grant_id}' cannot be revoked")
            grant.revoked_at = _ensure_utc(revoked_at) or _utcnow()
            grant.revocation_reason = reason
            self._append_log(
                {
                    "type": "revoke",
                    "grant_id": grant_id,
                    "revoked_at": grant.revoked_at.isoformat(),
                    "reason": reason,
                    "signature": _ps_shainfty(
                        _serialise_payload(
                            {
                                "grant_id": grant_id,
                                "revoked_at": grant.revoked_at.isoformat(),
                                "reason": reason,
                            }
                        )
                    ),
                }
            )

    def check_consent(
        self,
        *,
        from_agent: str,
        to_agent: str,
        consent_type: str,
        scope: str | Sequence[str] | None = None,
    ) -> ConsentGrant:
        required_scope = _normalise_scope(scope)
        with self._lock:
            for grant in self._grants.values():
                if not grant.matches(from_agent, to_agent, consent_type):
                    continue
                if not grant.scope_includes(required_scope):
                    continue
                if grant.is_valid():
                    return grant
            raise ConsentError(
                "missing valid consent: "
                f"from={from_agent} to={to_agent} type={consent_type} scope={required_scope}"
            )

    def audit(self, agent: str | None = None) -> list[dict[str, object]]:
        entries: list[dict[str, object]] = []
        for entry in self._iter_log():
            if agent is None:
                entries.append(entry)
                continue
            if entry["type"] == "request":
                payload = entry["request"]
                if agent in {payload["from_agent"], payload["to_agent"]}:
                    entries.append(entry)
            elif entry["type"] == "grant":
                payload = entry["grant"]
                if agent in {payload["from_agent"], payload["to_agent"]}:
                    entries.append(entry)
            elif entry["type"] == "revoke":
                grant_payload = self._grants.get(entry.get("grant_id", ""))
                if grant_payload and agent in {grant_payload.from_agent, grant_payload.to_agent}:
                    entries.append(entry)
        return entries

    def _load(self) -> None:
        if not self.log_path.exists():
            return
        for entry in self._iter_log():
            entry_type = entry["type"]
            if entry_type == "request":
                request = ConsentRequest.from_dict(entry["request"])
                self._requests[request.request_id] = request
            elif entry_type == "grant":
                grant = ConsentGrant.from_dict(entry["grant"])
                self._grants[grant.grant_id] = grant
            elif entry_type == "revoke":
                grant = self._grants.get(entry.get("grant_id", ""))
                if grant:
                    grant.revoked_at = _ensure_utc(
                        datetime.fromisoformat(str(entry["revoked_at"]))
                    )
                    grant.revocation_reason = entry.get("reason")

    def _iter_log(self) -> Iterable[dict[str, object]]:
        if not self.log_path.exists():
            return []
        with self.log_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                entry = json.loads(line)
                payload = {k: v for k, v in entry.items() if k != "entry_signature"}
                signature = entry.get("entry_signature")
                expected = _ps_shainfty(_serialise_payload(payload))
                if signature != expected:
                    raise ConsentError("consent log entry signature verification failed")
                yield payload

    def _append_log(self, payload: Mapping[str, object]) -> None:
        entry = dict(payload)
        entry["entry_signature"] = _ps_shainfty(_serialise_payload(payload))
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")


__all__ = [
    "ConsentRegistry",
    "ConsentRequest",
    "ConsentGrant",
]

