"""Runtime for executing <tool .../> tags generated offline."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Tuple
import json
import os
import re

from ..policies import Policy

TagRegistry = Dict[str, Callable[..., Any]]

_TAG_RE = re.compile(r"<tool\s+([^>/]+?)/>")
_ATTR_RE = re.compile(r"(\w+)\s*=\s*\"((?:\\.|[^\"])*)\"")


def _coerce(value: str) -> Any:
    """Best-effort conversion from attribute strings to Python objects."""

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        try:
            cleaned = bytes(value, "utf-8").decode("unicode_escape")
            return json.loads(cleaned)
        except Exception:
            pass
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            lowered = value.lower()
            if lowered in {"true", "false"}:
                return lowered == "true"
            return value


@dataclass
class ToolContext:
    """Execution context tracking variables and artifacts."""

    variables: Dict[str, Any] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)

    def remember(self, name: str, value: Any) -> None:
        self.variables[name] = value
        if isinstance(value, str) and os.path.exists(value):
            if value not in self.artifacts:
                self.artifacts.append(value)


@dataclass
class ToolTrace:
    name: str
    alias: str | None
    result_preview: str
    artifacts: Tuple[str, ...] = tuple()

    def as_dict(self) -> Dict[str, Any]:
        payload = {"name": self.name, "result": self.result_preview}
        if self.alias:
            payload["as"] = self.alias
        if self.artifacts:
            payload["artifacts"] = list(self.artifacts)
        return payload


def _parse_tag(raw: str) -> Dict[str, str]:
    attrs = dict(_ATTR_RE.findall(raw))
    if "name" not in attrs:
        raise ValueError(f"tool tag missing name attribute: {raw}")
    return attrs


def execute_tagged_text(
    text: str,
    registry: TagRegistry,
    policy: Policy | None = None,
    ctx: ToolContext | None = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Execute <tool .../> tags embedded in ``text``."""

    policy = policy or Policy()
    ctx = ctx or ToolContext()
    cursor = 0
    rendered: List[str] = []
    trace: List[Dict[str, Any]] = []
    for match in _TAG_RE.finditer(text):
        rendered.append(text[cursor : match.start()])
        attrs = _parse_tag(match.group(1))
        name = attrs.pop("name")
        alias = attrs.pop("as", None)
        source_name = attrs.pop("from", None)
        args_payload = attrs.pop("args", None)
        if not policy.allows(name):
            raise PermissionError(f"Tool {name} blocked by policy")
        func = registry.get(name)
        if func is None:
            raise KeyError(f"Unknown tool: {name}")
        positional: List[Any] = []
        if source_name:
            if source_name not in ctx.variables:
                raise KeyError(f"Unknown variable '{source_name}' for tool {name}")
            positional.append(ctx.variables[source_name])
        if args_payload is not None:
            positional.append(_coerce(args_payload))
        kwargs = {key: _coerce(value) for key, value in attrs.items()}
        result = func(*positional, **kwargs)
        if alias:
            ctx.remember(alias, result)
        artifacts: List[str] = []
        if isinstance(result, str) and os.path.exists(result):
            ctx.remember(alias or name, result)
            artifacts.append(result)
        preview = repr(result)
        trace.append(ToolTrace(name, alias, preview, tuple(artifacts)).as_dict())
        rendered.append(f'<result name="{name}" as="{alias or ""}"/>')
        cursor = match.end()
    rendered.append(text[cursor:])
    return ("".join(rendered), trace)
