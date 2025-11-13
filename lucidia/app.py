"""Simple coding portal for executing Python snippets."""

from __future__ import annotations

import io
import os
import secrets
import threading
from contextlib import redirect_stdout

import werkzeug
from flask import Flask, jsonify, render_template, request, session

# Expose a restricted set of safe built-in functions to executed code.
SAFE_BUILTINS: dict[str, object] = {
    "abs": abs,
    "enumerate": enumerate,
    "globals": globals,
    "len": len,
    "list": list,
    "max": max,
    "min": min,
    "print": print,
    "range": range,
    "sum": sum,
}

# Preserve variables and functions defined per user session.
SESSION_STATES: dict[str, dict[str, object]] = {}
STATE_LOCK = threading.RLock()


if not hasattr(werkzeug, "__version__"):
    try:  # pragma: no cover - compatibility shim
        from werkzeug import __about__ as _werkzeug_about
    except ImportError:  # pragma: no cover - fallback when metadata missing
        werkzeug.__version__ = "0"
    else:  # pragma: no cover - executed when metadata available
        werkzeug.__version__ = getattr(_werkzeug_about, "__version__", "0")
        del _werkzeug_about

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "lucidia-dev-secret")


def _get_session_id() -> str:
    """Return a stable session identifier for the current client."""

    session_id = session.get("lucidia_session_id")
    if session_id is None:
        session_id = secrets.token_hex(16)
        session["lucidia_session_id"] = session_id
    return session_id


def _load_session_state(session_id: str) -> dict[str, object]:
    """Return a shallow copy of the stored session state."""

    with STATE_LOCK:
        state = SESSION_STATES.setdefault(session_id, {})
        return dict(state)


def _persist_session_state(session_id: str, new_state: dict[str, object]) -> None:
    """Persist sanitized execution locals for the session."""

    sanitized = {k: v for k, v in new_state.items() if k != "__builtins__"}
    with STATE_LOCK:
        SESSION_STATES[session_id] = sanitized


def reset_all_session_state() -> None:
    """Helper for tests to reset every stored session."""

    with STATE_LOCK:
        SESSION_STATES.clear()


@app.route("/")
def index():
    """Serve the main page."""
    return render_template("index.html")


@app.post("/run")
def run_code():
    """Execute user-supplied Python code and return the output."""
    data = request.get_json(silent=True) or {}
    code = data.get("code", "")
    session_id = _get_session_id()
    session_state = _load_session_state(session_id)
    exec_locals = {k: v for k, v in session_state.items() if k != "__builtins__"}
    stdout = io.StringIO()
    try:
        with redirect_stdout(stdout):
            exec(code, {"__builtins__": SAFE_BUILTINS.copy()}, exec_locals)
        output = stdout.getvalue()
    except Exception as exc:  # noqa: BLE001 - broad for user feedback
        output = f"Error: {exc}"
    finally:
        _persist_session_state(session_id, exec_locals)
    return jsonify({"output": output})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
