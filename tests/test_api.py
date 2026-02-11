from fastapi.testclient import TestClient

from agent.main import app
from agent.store import init_db


client = TestClient(app)


def setup_module() -> None:
    init_db()


def test_root_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "BuckGrid Agent" in response.text


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_task_lifecycle() -> None:
    payload = {"task_type": "code", "objective": "Fix failing lint in repo", "risk_tags": []}
    create_resp = client.post("/tasks", json=payload)
    assert create_resp.status_code == 200
    task_id = create_resp.json()["task"]["id"]

    run_resp = client.post("/manager/run-once")
    assert run_resp.status_code == 200

    get_resp = client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["task"]["status"] in {"done", "queued", "running"}


def test_high_risk_requires_approval() -> None:
    payload = {"task_type": "email", "objective": "Send vendor payment", "risk_tags": ["money"]}
    create_resp = client.post("/tasks", json=payload)
    assert create_resp.status_code == 200
    assert create_resp.json()["task"]["requires_approval"] is True
