"""HTTP blueprint exposing Amundson–BlackRoad simulations and ledgers."""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from flask import Blueprint, jsonify, request

from amundson_blackroad.autonomy import conserved_mass, step_transport
from amundson_blackroad.spiral import fixed_point_stability, simulate_am2
from amundson_blackroad.thermo import (
    annotate_run_with_thermo,
    energy_increment,
    landauer_min,
    spiral_entropy,
)

bp = Blueprint("ambr", __name__, url_prefix="/api/ambr")


def _serialize_complex(values: np.ndarray) -> List[Dict[str, float]]:
    return [
        {"real": float(val.real), "imag": float(val.imag)}
        for val in np.asarray(values).ravel()
    ]


@bp.get("/sim/am2")
def am2_endpoint():
    q = request.args
    T = float(q.get("T", 10.0))
    dt = float(q.get("dt", 1e-3))
    a0 = float(q.get("a0", 0.1))
    theta0 = float(q.get("theta0", 0.0))
    gamma = float(q.get("gamma", 0.3))
    kappa = float(q.get("kappa", 0.7))
    eta = float(q.get("eta", 0.5))
    omega0 = float(q.get("omega0", 1.0))
    bits = float(q.get("bits", 0.0))
    temperature = float(q.get("temperature", 300.0))
    omega_surface = float(q.get("Omega", q.get("omega", 0.0)))

    t, a, theta, amp = simulate_am2(
        T,
        dt,
        a0,
        theta0,
        gamma,
        kappa,
        eta,
        omega0,
    )
    payload: Dict[str, Any] = {
        "t": t.tolist(),
        "a": a.tolist(),
        "theta": theta.tolist(),
        "amplitude": amp.tolist(),
        "units": {"t": "s", "a": "1", "theta": "rad", "amplitude": "1"},
    }
    if len(a) >= 2:
        da = float(a[-1] - a[-2])
        dtheta = float(theta[-1] - theta[-2])
        entropy = spiral_entropy(float(a[-2]), float(theta[-2]))
        payload["ledger"] = {
            "spiral_entropy_J_per_K": entropy,
            "da": da,
            "dtheta": dtheta,
        }
        payload = annotate_run_with_thermo(
            payload,
            bits=bits,
            n_bits=bits,
            temperature=temperature,
            Omega=omega_surface,
            a=float(a[-2]),
            theta=float(theta[-2]),
            da=da,
            dtheta=dtheta,
        )
    stability = fixed_point_stability(float(a[-1]), float(theta[-1]), gamma, kappa, eta, omega0)
    payload["stability"] = {
        "jacobian": stability.jacobian.tolist(),
        "eigenvalues": _serialize_complex(stability.eigenvalues),
        "is_stable": stability.is_stable,
    }
    return jsonify(payload)


@bp.post("/sim/transport")
def transport_endpoint():
    body = request.get_json(force=True)
    x = np.asarray(body["x"], dtype=float)
    A = np.asarray(body["A"], dtype=float)
    rho = np.asarray(body["rho"], dtype=float)
    dt = float(body.get("dt", 1e-3))
    steps = int(body.get("steps", 100))
    mu = float(body.get("mu", 1.0))
    chi = float(body.get("chi", 0.0))
    Uc = np.asarray(body["Uc"], dtype=float) if "Uc" in body else None
    dx = float(body.get("dx", x[1] - x[0]))

    current = A.copy()
    flux = np.zeros_like(current)
    for _ in range(steps):
        current, flux = step_transport(current, rho, dx, dt, mu_A=mu, chi_A=chi, Uc=Uc)
    mass_initial = conserved_mass(x, A)
    mass_final = conserved_mass(x, current)
    payload = {
        "x": x.tolist(),
        "A": current.tolist(),
        "flux": flux.tolist(),
        "mass": mass_final,
        "mass_initial": mass_initial,
        "mass_error": mass_final - mass_initial,
        "units": {
            "x": "m",
            "A": "A-units",
            "flux": "A-units*m/s",
            "mass": "A-units*m",
        },
    }
    bits = float(body.get("bits", 0.0))
    temperature = float(body.get("temperature", 300.0))
    payload = annotate_run_with_thermo(
        payload,
        bits=bits,
        n_bits=bits,
        temperature=temperature,
    )
    return jsonify(payload)


@bp.post("/energy")
def energy_endpoint():
    body = request.get_json(force=True)
    T = float(body["T"])
    a = float(body["a"])
    theta = float(body["theta"])
    da = float(body["da"])
    dtheta = float(body["dtheta"])
    Omega = float(body.get("Omega", 0.0))
    n_bits = float(body.get("n_bits", body.get("bits", 0.0)))

    delta_e = energy_increment(T, da, dtheta, a, theta, Omega=Omega)
    response: Dict[str, Any] = {
        "dE_J": delta_e,
        "units": {"dE_J": "J"},
    }
    if "n_bits" in body or "bits" in body:
        Emin = landauer_min(T, n_bits)
        response["E_min_J"] = Emin
        response["passes_landauer"] = bool(delta_e + 1e-30 >= Emin)
    return jsonify(response)
