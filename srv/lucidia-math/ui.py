"""User interfaces for the Lucidia Infinity Math System."""

from __future__ import annotations

import json
from typing import Callable, Dict

from flask import Flask, jsonify
from flask_socketio import SocketIO

from . import finance, fractals, logic, numbers, primes, proofs, waves

MENU: Dict[str, Callable[[], object]] = {
    "Logic": logic.demo,
    "Primes": primes.demo,
    "Proofs": proofs.demo,
    "Waves": waves.demo,
    "Finance": finance.demo,
    "Numbers": numbers.demo,
    "Fractals": fractals.demo,
}


def repl() -> None:
    """Simple command line REPL exposing demo functions."""

    options = list(MENU.keys())
    while True:
        for i, name in enumerate(options, start=1):
            print(f"{i}. {name}")
        print("0. Exit")
        try:
            choice = int(input("Select module: "))
        except ValueError:
            print("Invalid input\n")
            continue
        if choice == 0:
            break
        if 1 <= choice <= len(options):
            name = options[choice - 1]
            result = MENU[name]()
            print(json.dumps({"result": result}, indent=2))
        else:
            print("Invalid selection\n")


def create_app() -> Flask:
    """Create a minimal Flask + Socket.IO application."""

    app = Flask(__name__)
    socketio = SocketIO(app, async_mode="threading")

    @app.get("/api/demo/<module>")
    def api_demo(module: str):  # pragma: no cover - thin wrapper
        func = MENU.get(module.capitalize())
        if not func:
            return jsonify({"error": "unknown module"}), 404
        return jsonify(func())

    # expose socket for completeness
    @socketio.on("demo")  # pragma: no cover - requires running server
    def handle_demo(message):
        module = message.get("module", "").capitalize()
        func = MENU.get(module)
        if func:
            socketio.emit("result", func())
        else:
            socketio.emit("result", {"error": "unknown module"})

    return app


def demo() -> None:
    """Launch the REPL for interactive exploration."""

    repl()

interactive_app = create_app()

# Flask API for the Infinity Math system.
from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from .api_ambr import bp as ambr_bp

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

api_app = Flask(__name__)
api_app.register_blueprint(ambr_bp)
app = api_app


@api_app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok"})


@api_app.get("/api/math/<path:subpath>")
def get_output(subpath: str):
    """Serve generated artifacts from the output tree."""
    return send_from_directory(OUTPUT_DIR, subpath)


if __name__ == "__main__":
    api_app.run(host="127.0.0.1", port=8500)
