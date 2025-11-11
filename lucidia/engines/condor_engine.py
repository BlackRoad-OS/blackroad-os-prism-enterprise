"""Wrappers for running NASA Condor models locally.

The helpers here expose a minimal, import-safe subset of Condor's
functionality so tests can exercise code paths without requiring the full
dependency. The real Condor package is optional at import time; calling
these helpers will raise ``RuntimeError`` if Condor is not installed.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
import tempfile
from dataclasses import asdict, is_dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Type

try:  # pragma: no cover - optional dependency
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - numpy may be absent
    np = None  # type: ignore

try:  # pragma: no cover - optional dependency
    import condor  # type: ignore
except Exception:  # pragma: no cover - condor may be absent in CI
    condor = None  # type: ignore

ALLOWED_IMPORTS = {"condor", "math", "numpy", "dataclasses"}
FORBIDDEN_NAMES = {
    "open",
    "os",
    "sys",
    "subprocess",
    "socket",
    "sockets",
    "eval",
    "exec",
    "__import__",
}


def _dataclass_to_dict(obj: Any) -> Any:
    """
    Recursively convert dataclasses and ``numpy`` arrays into primitives suitable for JSON serialization.

    This helper ensures that results are JSON serialisable. ``numpy`` arrays are transformed into Python lists.
    """
    if is_dataclass(obj):
        return {k: _dataclass_to_dict(v) for k, v in asdict(obj).items()}
    if np is not None and isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (list, tuple, set)):
        return [_dataclass_to_dict(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _dataclass_to_dict(v) for k, v in obj.items()}
    return obj


def validate_model_source(py_text: str) -> None:
    """
    Validate user-supplied model source code using conservative static analysis.

    The validator walks the ``ast`` for the provided source, restricts imports to a
    small allow-list, and rejects several dangerous names and dunder attribute
    access. Any disallowed construct raises ``ValueError`` to prevent unsafe
    execution when loading user models.
    """
    tree = ast.parse(py_text)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_IMPORTS:
                    raise ValueError(f"import of '{alias.name}' is not allowed")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_IMPORTS:
                raise ValueError(f"from '{node.module}' import is not allowed")
        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN_NAMES:
                raise ValueError(f"usage of '{node.id}' is forbidden")
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                raise ValueError("dunder attribute access is forbidden")


def _load_module_from_source(source: str, module_name: str) -> ModuleType:
    """Load a module from source text in an isolated temporary directory."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / f"{module_name}.py"
        path.write_text(source, encoding="utf-8")
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:  # pragma: no cover - defensive
            raise ImportError("Could not create import spec for model")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module


def load_model_from_source(py_text: str, class_name: str) -> Type[Any]:
    """
    Validate and load a model class from source code.

    Parameters
    ----------
    py_text : str
        The Python source code as a string, expected to define a model class.
    class_name : str
        The name of the class to load from the provided source code.

    Returns
    -------
    Type[Any]
        The loaded model class object.

    Raises
    ------
    ValueError
        If the source code contains forbidden imports or names.
    ImportError
        If the module cannot be loaded from the source code.
    AttributeError
        If the specified class is not found in the loaded module.

    This function first validates the provided source code for safety,
    then loads it as a module in an isolated temporary directory,
    and finally returns the specified class object from the module.
    """
    validate_model_source(py_text)
    module = _load_module_from_source(py_text, "user_model")
    return getattr(module, class_name)


def solve_algebraic(model_cls: Type[Any], **params: Any) -> Dict[str, Any]:
    """
    Instantiates the given Condor ``AlgebraicSystem`` model class with the provided parameters,
    calls its ``solve`` method, and returns the results as a JSON-friendly dictionary.

    Parameters
    ----------
    model_cls : Type[Any]
        The Condor model class to instantiate (should be a subclass of ``AlgebraicSystem``).
    **params : Any
        Keyword arguments to pass to the model class constructor.

    Returns
    -------
    Dict[str, Any]
        The solution returned by ``model.solve()``, converted to a JSON-serializable dictionary.
    """
    if condor is None:  # pragma: no cover - runtime guard
        raise RuntimeError("Condor is not installed")
    model = model_cls(**params)
    solution = model.solve()
    return _dataclass_to_dict(solution)


def simulate_ode(
    model_cls: Type[Any],
    t_final: float,
    initial: Dict[str, Any],
    params: Dict[str, Any],
    events: Any | None = None,
    modes: Any | None = None,
) -> Dict[str, Any]:
    """
    Simulate an ``ODESystem`` until ``t_final``.

    Forwards to the model's ``simulate`` method and returns results
    serialised via :func:`_dataclass_to_dict`.
    The output is a serialisable dictionary.
    """
    if condor is None:  # pragma: no cover - runtime guard
        raise RuntimeError("Condor is not installed")
    model = model_cls(**params)
    result = model.simulate(t_final, initial, events=events, modes=modes)
    return _dataclass_to_dict(result)


def optimize(
    problem_cls: Type[Any],
    initial_guess: Dict[str, Any],
    bounds: Dict[str, Any],
    options: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Solve an ``OptimizationProblem`` and return a serialisable dictionary."""
    if condor is None:  # pragma: no cover - runtime guard
        raise RuntimeError("Condor is not installed")
    problem = problem_cls()
    result = problem.solve(initial_guess=initial_guess, bounds=bounds, options=options)
    return _dataclass_to_dict(result)

