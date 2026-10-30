from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_has_version():
    response = client.get("/health")
    assert "version" in response.json()


def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text


def test_create_task_database_unavailable(monkeypatch):
    def fail_connection():
        raise RuntimeError("simulated database outage")

    monkeypatch.setattr("app.main.conn", fail_connection)

    response = client.post("/tasks", json={"name": "test task"})

    assert response.status_code == 500
    assert response.json()["detail"] == "task creation failed"


def test_invalid_task():
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_root_not_found():
    response = client.get("/")
    assert response.status_code == 404
