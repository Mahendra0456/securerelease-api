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


def test_create_task_without_database():
    response = client.post("/tasks", json={"name": "test task"})
    assert response.status_code in (200, 500)


def test_invalid_task():
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_root_not_found():
    response = client.get("/")
    assert response.status_code == 404
