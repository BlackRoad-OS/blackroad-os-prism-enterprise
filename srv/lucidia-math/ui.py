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

import numpy as np
from flask import Flask, jsonify, request, send_from_directory

from amundson_blackroad.autonomy import conserved_mass, simulate_transport
from amundson_blackroad.spiral import simulate_am2
from amundson_blackroad.thermo import annotate_run_with_thermo

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

api_app = Flask(__name__)
app = api_app


@api_app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok"})


@api_app.get("/api/math/<path:subpath>")
def get_output(subpath: str):
    """Serve generated artifacts from the output tree."""
    return send_from_directory(OUTPUT_DIR, subpath)


@api_app.get("/api/ambr/sim/am2")
def simulate_am2_endpoint():
    """Run the AM-2 spiral simulation."""

    args = request.args
    t, a, theta, amp = simulate_am2(
        float(args.get("T", 10.0)),
        float(args.get("dt", 1e-3)),
        float(args.get("a0", 0.1)),
        float(args.get("theta0", 0.0)),
        float(args.get("gamma", 0.3)),
        float(args.get("kappa", 0.7)),
        float(args.get("eta", 0.5)),
        float(args.get("omega0", 1.0)),
    )
    payload = {
        "t": t.tolist(),
        "a": a.tolist(),
        "theta": theta.tolist(),
        "amp": amp.tolist(),
    }
    annotated = annotate_run_with_thermo(payload, bits=float(args.get("bits", 0.0)), temperature=float(args.get("temperature", 300.0)))
    return jsonify(annotated)


@api_app.post("/api/ambr/sim/transport")
def simulate_transport_endpoint():
    """Run BR-1/2 transport and report conservation metrics."""

    body = request.get_json(force=True)
    x = np.asarray(body["x"], dtype=float)
    A0 = np.asarray(body["A"], dtype=float)
    rho = np.asarray(body["rho"], dtype=float)
    dt = float(body.get("dt", 1e-3))
    steps = int(body.get("steps", 100))
    mu_A = float(body.get("mu", 1.0))
    chi_A = float(body.get("chi", 0.0))
    Uc = np.asarray(body["Uc"], dtype=float) if "Uc" in body else None
    result = simulate_transport(x, A0, rho, steps, dt, mu_A=mu_A, chi_A=chi_A, Uc=Uc)
    initial_mass = conserved_mass(x, A0)
    payload = {
        "x": result["x"].tolist(),
        "A": result["A"].tolist(),
        "flux": result["flux"].tolist(),
        "mass": float(result["mass"]),
        "mass_initial": initial_mass,
        "mass_error": float(result["mass"] - initial_mass),
    }
    annotated = annotate_run_with_thermo(payload, bits=float(body.get("bits", 0.0)), temperature=float(body.get("temperature", 300.0)), seed=body.get("seed"))
    return jsonify(annotated)


if __name__ == "__main__":
    api_app.run(host="127.0.0.1", port=8500)
