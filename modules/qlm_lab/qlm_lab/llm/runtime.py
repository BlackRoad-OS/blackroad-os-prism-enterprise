from __future__ import annotations

"""Runtime utilities for executing <tool .../> tags produced by an LLM."""

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any, Dict, List, Match, Tuple

from ..lineage import append as log_event
from ..policies import Policy
from ..tools.registry import ToolRegistry

_TAG = re.compile(r"<tool\s+[^>]*?/>")
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
    """Variable scope shared across tool invocations."""

    vars: Dict[str, Any] = field(default_factory=dict)


def _coerce(val: str) -> Any:
    v = val.strip()
    if v.lower() in {"true", "false"}:
        return v.lower() == "true"
    try:
        if "." in v:
            return float(v)
        return int(v)
    except ValueError:
        return v


def _parse_attrs(elem: ET.Element) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in elem.attrib.items():
        if key == "args":
            try:
                out.update(json.loads(value))
            except Exception:
                out["args_raw"] = value
        else:
            out[key] = _coerce(value)
    return out


def _resolve_args(attrs: Dict[str, Any], ctx: ToolContext) -> Tuple[str, Dict[str, Any], str | None, str]:
    name = attrs.pop("name")
    as_var = attrs.pop("as", None)
    from_var = attrs.pop("from", None)
    fname = attrs.pop("fname", None)
    if from_var:
        obj = ctx.vars.get(from_var)
        if obj is None:
            raise ValueError(f"Unknown var '{from_var}'")
        attrs["from_obj"] = obj
    if fname is not None:
        attrs["fname"] = fname
    return name, attrs, as_var, from_var or ""


def execute_tagged_text(
    text: str, registry: ToolRegistry, policy: Policy, ctx: ToolContext | None = None
) -> Tuple[str, List[Dict[str, Any]]]:
    """Execute tool tags in ``text`` and return the stitched output and trace."""

    ctx = ctx or ToolContext()
    trace: List[Dict[str, Any]] = []

    def _repl(match: Match[str]) -> str:
        tag = match.group(0)
        try:
            elem = ET.fromstring(tag)
            attrs = _parse_attrs(elem)
            name, args, as_var, from_var = _resolve_args(attrs, ctx)
            if name.startswith("llm.") and not policy.allow_network:
                raise PermissionError("Network/remote LLM disabled by policy")
            fn = registry.get(name)
            call_args = dict(args)
            if "from_obj" in call_args:
                from_obj = call_args.pop("from_obj")
                result = fn(from_obj, **call_args)
            else:
                result = fn(**call_args)
            if as_var:
                ctx.vars[as_var] = result
            log_event(
                {
                    "kind": "tool",
                    "name": name,
                    "args": {k: str(v)[:200] for k, v in call_args.items()},
                    "as": as_var,
                    "from": from_var,
                }
            )
            rtype = type(result).__name__
            trace.append({"name": name, "type": rtype, "as": as_var, "from": from_var})
            return f'<result name="{as_var or name}" type="{rtype}"/>'
        except Exception as exc:  # pragma: no cover - exercised indirectly
            log_event({"kind": "tool_error", "tag": tag, "error": str(exc)})
            return f'<error tool="{tag}" reason="{str(exc)}"/>'

    new_text = _TAG.sub(_repl, text)
    return new_text, trace


__all__ = ["ToolContext", "execute_tagged_text"]
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
