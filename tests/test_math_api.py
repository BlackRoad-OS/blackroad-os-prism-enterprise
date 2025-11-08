from __future__ import annotations

import json
import math
from pathlib import Path
import importlib.util
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import pytest
from fastapi.testclient import TestClient

from lucidia_math_lab.amundson_equations import phase_derivative

MODULE_PATH = Path(__file__).resolve().parents[1] / "srv" / "lucidia-math" / "api_ambr.py"
spec = importlib.util.spec_from_file_location(
    "lucidia_math",
    MODULE_PATH,
    submodule_search_locations=[str(MODULE_PATH.parent)],
)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
assert spec.loader
spec.loader.exec_module(module)  # type: ignore[arg-type]
app = module.app
SERVER_CONTEXT = module.SERVER_CONTEXT


@pytest.fixture
def client(tmp_path, monkeypatch) -> TestClient:
    monkeypatch.setenv("MATH_OUTPUT_DIR", str(tmp_path))
    return TestClient(app)


def _artifact_exists(output_dir: Path, record: dict) -> bool:
    path = output_dir / Path(record["relative_path"])
    return path.exists() and path.stat().st_size > 0


def test_fractal_endpoint_generates_artifact(client: TestClient, tmp_path: Path) -> None:
    response = client.get(
        "/api/math/fractals/mandelbrot",
        params={"width": 64, "height": 64, "iter": 32, "xmin": -2, "xmax": 1, "ymin": -1, "ymax": 1},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "artifact" in payload
    assert _artifact_exists(tmp_path, payload["artifact"])
    assert payload["units"]["width"] == "px"


def test_prime_endpoint_returns_sequence(client: TestClient) -> None:
    response = client.get("/api/math/primes", params={"limit": 50, "plot": False})
    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == len(payload["primes"])
    assert payload["count"] > 0


def test_truth_table_persists_json(client: TestClient, tmp_path: Path) -> None:
    response = client.post(
        "/api/math/logic/truth-table",
        json={"vars": ["A", "B"], "expression": "A and B"},
    )
    assert response.status_code == 200
    payload = response.json()
    artifact = payload["artifact"]
    assert _artifact_exists(tmp_path, artifact)
    table = payload["table"]
    assert table["rows"][0]["result"] is False
    assert table["rows"][-1]["result"] is True


def test_waves_endpoint_returns_samples(client: TestClient, tmp_path: Path) -> None:
    response = client.get(
        "/api/math/waves/sine",
        params={"freq": 2.0, "phase": 0.0, "samples": 32, "sample_rate": 128.0},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "samples" in payload
    sample_record = payload["samples"]
    path = tmp_path / Path(sample_record["relative_path"])
    assert path.exists()
    data = json.loads(path.read_text())
    assert len(data["values"]) == 32


def test_am2_endpoint_units(client: TestClient) -> None:
    response = client.get(
        "/api/ambr/sim/am2",
        params={"T": 0.1, "dt": 0.01, "a0": 0.2, "theta0": 0.1, "gamma": 0.5, "kappa": 0.3, "eta": 0.2},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["units"]["t"] == "s"
    assert len(payload["t"]) == len(payload["a"])


def test_transport_endpoint_conserves_mass(client: TestClient) -> None:
    x = np.linspace(-1.0, 1.0, 32)
    A = np.exp(-x ** 2)
    rho = np.tanh(x)
    response = client.post(
        "/api/ambr/sim/transport",
        json={
            "x": x.tolist(),
            "A": A.tolist(),
            "rho": rho.tolist(),
            "steps": 20,
            "dt": 1e-3,
            "mu": 0.5,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert abs(payload["mass_error"]) < 1e-3


def test_energy_endpoint_reports_landauer(client: TestClient) -> None:
    response = client.post(
        "/api/ambr/energy",
        json={
            "T": 300.0,
            "a": 0.2,
            "theta": 0.3,
            "da": 0.01,
            "dtheta": 0.02,
            "Omega": 1e-21,
            "n_bits": 8,
            "temperature": 300.0,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["E_min"] > 0
    assert isinstance(payload["pass"], bool)


def test_phase_derivative_endpoint_auto_resolves(client: TestClient) -> None:
    SERVER_CONTEXT.last_phi_x = 0.0
    SERVER_CONTEXT.last_phi_y = 1.2
    response = client.post("/api/ambr/coherence/dphi", json={"phi_x": 0.4})
    assert response.status_code == 200
    payload = response.json()
    resolved = payload["resolved"]
    assert payload["mode"] == "auto"
    assert math.isclose(payload["dphi_dt"], phase_derivative(**resolved))
    assert math.isclose(resolved["phi_x"], 0.4)
    assert math.isclose(resolved["phi_y"], 1.2)
    assert "phi_y" in payload["why"]


def test_phase_derivative_endpoint_strict_requires_fields(client: TestClient) -> None:
    response = client.post(
        "/api/ambr/coherence/dphi",
        json={"auto_resolve": False, "omega_0": 1.0},
    )
    assert response.status_code == 422
    payload = response.json()
    assert payload["error_code"] == "missing_parameters"


def test_phase_derivative_endpoint_strict_success(client: TestClient) -> None:
    body = {
        "auto_resolve": False,
        "omega_0": 1.0,
        "lambda_": 0.5,
        "eta": 0.2,
        "phi_x": 0.3,
        "phi_y": -0.2,
        "r_x": 1.1,
        "r_y": 0.9,
        "k_b_t": 1e-21,
    }
    response = client.post("/api/ambr/coherence/dphi", json=body)
    assert response.status_code == 200
    payload = response.json()
    resolved = payload["resolved"]
    assert payload["mode"] == "strict"
    assert payload["why"] == {}
    assert math.isclose(payload["dphi_dt"], phase_derivative(**resolved))
