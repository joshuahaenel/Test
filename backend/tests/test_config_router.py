import pytest
from fastapi.testclient import TestClient

from backend import runtime_config
from backend.app import app


@pytest.fixture(autouse=True)
def _reset_runtime_config():
    runtime_config.clear()
    yield
    runtime_config.clear()


@pytest.fixture
def client():
    return TestClient(app)


def test_read_config_defaults(client):
    response = client.get("/api/config")
    assert response.status_code == 200
    body = response.json()
    assert body["default_location"] == "Berlin"
    assert body["auto_speak"] is True


def test_update_config_persists_in_memory(client):
    response = client.post("/api/config", json={"default_location": "Hamburg", "auto_speak": False})
    assert response.status_code == 200
    assert response.json()["default_location"] == "Hamburg"
    assert response.json()["auto_speak"] is False

    response = client.get("/api/config")
    assert response.json()["default_location"] == "Hamburg"
    assert response.json()["auto_speak"] is False
