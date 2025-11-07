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
