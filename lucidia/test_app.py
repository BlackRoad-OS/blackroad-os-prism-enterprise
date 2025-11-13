import pytest

from lucidia.app import app, reset_all_session_state


@pytest.fixture(autouse=True)
def clear_state():
    """Ensure each test has an isolated execution environment."""
    reset_all_session_state()


def test_index():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Lucidia Co Coding Portal" in resp.data


def test_run_code():
    client = app.test_client()
    resp = client.post("/run", json={"code": "print('hi')"})
    assert resp.status_code == 200
    assert "hi" in resp.get_json()["output"]


def test_state_and_builtins():
    client = app.test_client()
    client.post("/run", json={"code": "nums = list(range(3))"})
    resp = client.post("/run", json={"code": "print(len(nums))"})
    assert resp.status_code == 200
    assert resp.get_json()["output"].strip() == "3"


def test_safe_builtins_are_isolated_per_request():
    client = app.test_client()
    tamper_resp = client.post(
        "/run",
        json={"code": "__builtins__['len'] = lambda items: 999"},
    )
    assert tamper_resp.status_code == 200

    resp = client.post("/run", json={"code": "print(len([1, 2, 3]))"})
    assert resp.status_code == 200
    assert resp.get_json()["output"].strip() == "3"


def test_state_is_not_shared_across_sessions():
    client_a = app.test_client()
    client_b = app.test_client()

    resp_a = client_a.post("/run", json={"code": "secret = 123"})
    assert resp_a.status_code == 200

    resp_b = client_b.post("/run", json={"code": "print('secret' in globals())"})
    assert resp_b.status_code == 200
    assert resp_b.get_json()["output"].strip() == "False"


def test_state_mutations_do_not_persist_between_sessions():
    client_a = app.test_client()
    client_b = app.test_client()

    client_a.post("/run", json={"code": "__builtins__ = {}; value = 42"})

    resp_a = client_a.post("/run", json={"code": "print(value)"})
    assert resp_a.status_code == 200
    assert resp_a.get_json()["output"].strip() == "42"

    resp_b = client_b.post("/run", json={"code": "print('value' in globals())"})
    assert resp_b.status_code == 200
    assert resp_b.get_json()["output"].strip() == "False"
