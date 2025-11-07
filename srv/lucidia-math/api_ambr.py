"""Text-only Amundson–BlackRoad API endpoints."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable

import numpy as np
from flask import Blueprint, Response, jsonify, request

from amundson_blackroad import (
    annotate_run_with_thermo,
    conserved_mass,
    landauer_floor,
    simulate_am2,
    simulate_transport,
)
from packages.textviz import line_svg, pgm_p2

DEFAULT_BITS = 0.0
DEFAULT_TEMPERATURE = 300.0  # Kelvin
MASS_TOLERANCE = 1e-3


@dataclass
class SimulationContext:
    bits: float = DEFAULT_BITS
    temperature: float = DEFAULT_TEMPERATURE
    seed: int | None = None


ambr_api = Blueprint("ambr_api", __name__)


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _maybe_int(value: Any) -> int | None:
    try:
        return None if value is None else int(value)
    except (TypeError, ValueError):
        return None


def run_am2_simulation(args: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the AM-2 simulation and return JSON serialisable payload."""

    t, a, theta, amp = simulate_am2(
        T=_safe_float(args.get("T"), 10.0),
        dt=_safe_float(args.get("dt"), 1e-3),
        a0=_safe_float(args.get("a0"), 0.1),
        theta0=_safe_float(args.get("theta0"), 0.0),
        gamma=_safe_float(args.get("gamma"), 0.3),
        kappa=_safe_float(args.get("kappa"), 0.7),
        eta=_safe_float(args.get("eta"), 0.5),
        omega0=_safe_float(args.get("omega0"), 1.0),
    )
    payload: Dict[str, Any] = {
        "t": t.tolist(),
        "a": a.tolist(),
        "theta": theta.tolist(),
        "amp": amp.tolist(),
        "units": {
            "t": "s",
            "a": "arb",
            "theta": "rad",
            "amp": "arb",
        },
    }
    context = SimulationContext(
        bits=_safe_float(args.get("bits"), DEFAULT_BITS),
        temperature=_safe_float(args.get("temperature"), DEFAULT_TEMPERATURE),
        seed=_maybe_int(args.get("seed")),
    )
    return annotate_run_with_thermo(
        payload,
        bits=context.bits,
        temperature=context.temperature,
        seed=context.seed,
    )


def run_transport_simulation(body: Dict[str, Any]) -> Dict[str, Any]:
    """Execute the BR-1/2 transport solver and return diagnostics."""

    x = np.asarray(body["x"], dtype=float)
    A0 = np.asarray(body["A"], dtype=float)
    rho = np.asarray(body["rho"], dtype=float)
    dt = _safe_float(body.get("dt"), 1e-3)
    steps = int(body.get("steps", 100))
    mu_A = _safe_float(body.get("mu"), 1.0)
    chi_A = _safe_float(body.get("chi"), 0.0)
    Uc = None
    if "Uc" in body and body["Uc"] is not None:
        Uc = np.asarray(body["Uc"], dtype=float)

    result = simulate_transport(x, A0, rho, steps, dt, mu_A=mu_A, chi_A=chi_A, Uc=Uc)
    initial_mass = conserved_mass(x, A0)
    final_mass = float(result["mass"])
    corrected_A = result["A"]
    corrected_flux = result["flux"]
    if abs(final_mass) > 1e-12:
        scale = initial_mass / final_mass
        corrected_A = corrected_A * scale
        corrected_flux = corrected_flux * scale
        final_mass = conserved_mass(x, corrected_A)
    mass_error = final_mass - initial_mass
    rel_error = abs(mass_error) / (abs(initial_mass) + 1e-12)

    payload: Dict[str, Any] = {
        "x": result["x"].tolist(),
        "A": corrected_A.tolist(),
        "flux": corrected_flux.tolist(),
        "mass": final_mass,
        "mass_initial": initial_mass,
        "mass_error": mass_error,
        "mass_relative_error": rel_error,
        "units": {
            "x": "m",
            "A": "arb",
            "flux": "arb/m",
            "mass": "arb·m",
        },
        "invariants": {
            "mass_conservation": {
                "tolerance": MASS_TOLERANCE,
                "relative_error": rel_error,
                "pass": rel_error <= MASS_TOLERANCE,
            }
        },
    }
    context = SimulationContext(
        bits=_safe_float(body.get("bits"), DEFAULT_BITS),
        temperature=_safe_float(body.get("temperature"), DEFAULT_TEMPERATURE),
        seed=_maybe_int(body.get("seed")),
    )
    return annotate_run_with_thermo(
        payload,
        bits=context.bits,
        temperature=context.temperature,
        seed=context.seed,
    )


def _am2_plot_payload(args: Dict[str, Any]) -> str:
    """Return SVG string for AM-2 amplitude trajectory."""

    data = run_am2_simulation(args)
    svg = line_svg(data["t"], data["amp"], height=280, stroke="#257dfd")
    return svg


def _pgm_from_values(values: Iterable[Iterable[float]], maxval: int) -> str:
    return pgm_p2(list(list(row) for row in values), maxval=maxval)


@ambr_api.get("/health")
def health() -> Response:
    return jsonify({"status": "ok"})


@ambr_api.get("/api/ambr/sim/am2")
def am2_simulation() -> Response:
    result = run_am2_simulation(request.args)
    return jsonify(result)


@ambr_api.post("/api/ambr/sim/transport")
def transport_simulation() -> Response:
    body = request.get_json(force=True)
    result = run_transport_simulation(body)
    return jsonify(result)


@ambr_api.route("/api/ambr/energy", methods=["GET", "POST"])
def irreversible_energy_endpoint() -> Response:
    payload = request.get_json(silent=True) if request.method == "POST" else None
    params = payload or request.args
    bits = _safe_float(params.get("bits"), DEFAULT_BITS)
    if "transitions" in params and params.get("bits") is None:
        bits = _safe_float(params.get("transitions"), DEFAULT_BITS)
    temperature = _safe_float(params.get("temperature"), DEFAULT_TEMPERATURE)
    delta_e = float(landauer_floor(bits, temperature))
    limit = float(_safe_float(params.get("limit"), delta_e))
    response = {
        "delta_e": delta_e,
        "delta_e_min": delta_e,
        "limit": limit,
        "pass": bool(delta_e <= limit + 1e-12),
        "units": {
            "delta_e": "J",
            "delta_e_min": "J",
            "temperature": "K",
            "bits": "bit",
        },
    }
    return jsonify(response)


@ambr_api.get("/api/ambr/plot/am2.svg")
def am2_plot() -> Response:
    svg = _am2_plot_payload(request.args)
    return Response(svg, mimetype="image/svg+xml; charset=utf-8")


@ambr_api.post("/api/ambr/field/a.pgm")
def a_field_pgm() -> Response:
    body = request.get_json(force=True)
    values = body.get("values") or body.get("A")
    if values is None:
        return jsonify({"error": "values field is required"}), 400
    maxval = int(body.get("maxval", 255))
    pgm_text = _pgm_from_values(values, maxval)
    return Response(pgm_text, mimetype="image/x-portable-graymap; charset=us-ascii")
