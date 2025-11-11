"""Lightweight helpers for Condor model execution used in tests."""

from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
from dataclasses import asdict, is_dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Type

try:  # pragma: no cover - optional dependency in CI
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover
    np = None  # type: ignore

condor = None  # placeholder for the real library at runtime

ALLOWED_IMPORTS = {"condor", "math", "numpy", "dataclasses"}
FORBIDDEN_NAMES = {"open", "os", "sys", "subprocess", "socket", "eval", "exec"}


def _normalise(value: Any) -> Any:
    if is_dataclass(value):
        return {k: _normalise(v) for k, v in asdict(value).items()}
    if np is not None and isinstance(value, np.ndarray):  # pragma: no cover - optional
        return value.tolist()
    if isinstance(value, dict):
        return {k: _normalise(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_normalise(v) for v in value]
    return value


def validate_model_source(py_text: str) -> None:
    """Perform a tiny security audit over ``py_text``."""

    tree = ast.parse(py_text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    raise ValueError(f"Disallowed import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            if root not in ALLOWED_IMPORTS:
                raise ValueError(f"Disallowed import: {node.module}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            raise ValueError(f"Forbidden name: {node.id}")

    for forbidden in FORBIDDEN_NAMES:
        if forbidden in py_text:
            raise ValueError(f"Forbidden token found: {forbidden}")


def _load_module(py_text: str, module_name: str) -> ModuleType:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{module_name}.py"
        path.write_text(py_text, encoding="utf-8")
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:  # pragma: no cover - defensive
            raise ImportError("Unable to create import spec")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


def load_model_from_source(py_text: str, class_name: str) -> Type[Any]:
    """Validate ``py_text`` and return ``class_name`` from it."""

    validate_model_source(py_text)
    module = _load_module(py_text, "condor_user_model")
    return getattr(module, class_name)


def solve_algebraic(model_cls: Type[Any], **params: Any) -> Dict[str, Any]:
    model = model_cls(**params)
    result = model.solve() if hasattr(model, "solve") else model
    return _normalise(result)


def simulate_ode(
    model_cls: Type[Any],
    t_final: float,
    initial: Dict[str, Any],
    params: Dict[str, Any],
    *,
    events: Any | None = None,
    modes: Any | None = None,
) -> Dict[str, Any]:
    model = model_cls(**params)
    if not hasattr(model, "simulate"):
        raise RuntimeError("Model does not implement simulate()")
    result = model.simulate(t_final, initial, events=events, modes=modes)
    return _normalise(result)


def optimize(
    problem_cls: Type[Any],
    initial_guess: Dict[str, Any],
    bounds: Dict[str, Any] | None = None,
    options: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    problem = problem_cls()
    if not hasattr(problem, "solve"):
        raise RuntimeError("Problem does not implement solve()")
    result = problem.solve(initial_guess, bounds=bounds, options=options)
    return _normalise(result)


__all__ = [
    "condor",
    "validate_model_source",
    "load_model_from_source",
    "solve_algebraic",
    "simulate_ode",
    "optimize",
]
