"""CLI helpers and Flask application for Lucidia Infinity Math."""
from __future__ import annotations

import json
from typing import Callable, Dict

from flask import Flask, jsonify

from packages.textviz import pgm_p2

from .api_ambr import ambr_api, run_am2_simulation, run_transport_simulation
from .api_math import (
    mandelbrot_counts,
    math_api,
    primes_payload,
    sine_wave_samples,
    truth_table_payload,
)


def _demo_am2() -> Dict[str, object]:
    return run_am2_simulation({})


def _demo_transport() -> Dict[str, object]:
    import numpy as np

    x = np.linspace(-1.0, 1.0, 64)
    A0 = np.exp(-x**2)
    rho = 1.0 - 0.2 * x**2
    body = {
        "x": x.tolist(),
        "A": A0.tolist(),
        "rho": rho.tolist(),
        "dt": 1e-3,
        "steps": 50,
        "bits": 8,
        "temperature": 300.0,
    }
    return run_transport_simulation(body)


def _demo_mandelbrot() -> Dict[str, object]:
    counts = mandelbrot_counts(40, 40, 40, -2.0, 1.0, -1.5, 1.5)
    return {
        "format": "PGM",
        "sample": pgm_p2(counts).splitlines()[:10],
        "units": {"format": "portable-graymap"},
    }


def _demo_primes() -> Dict[str, object]:
    return primes_payload(100)


def _demo_logic() -> Dict[str, object]:
    return truth_table_payload("a and not b", ["a", "b"])


def _demo_wave() -> Dict[str, object]:
    xs, ys = sine_wave_samples(1.0, 0.0, 16, 1.0)
    return {
        "x": xs,
        "y": ys,
        "units": {"x": "s", "y": "arb"},
    }


MENU: Dict[str, Callable[[], Dict[str, object]]] = {
    "AM-2": _demo_am2,
    "Transport": _demo_transport,
    "Mandelbrot": _demo_mandelbrot,
    "Primes": _demo_primes,
    "Logic": _demo_logic,
    "Wave": _demo_wave,
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
            print(json.dumps({"module": name, "result": result}, indent=2))
        else:
            print("Invalid selection\n")


def create_app() -> Flask:
    """Create a minimal Flask application exposing the text-only API."""

    app = Flask(__name__)
    app.register_blueprint(ambr_api)
    app.register_blueprint(math_api)

    @app.get("/api/demo/<module>")
    def api_demo(module: str):  # pragma: no cover - thin wrapper
        func = MENU.get(module.replace("-", " ").title())
        if not func:
            return jsonify({"error": "unknown module"}), 404
        return jsonify(func())

    return app


def demo() -> None:
    """Launch the REPL for interactive exploration."""

    repl()


app = create_app()
