from fastapi.testclient import TestClient

from backend.app import app
from backend.config import get_settings
from backend.routers import health as health_router


def test_webhook_rejects_missing_token(monkeypatch):
    monkeypatch.setenv("HEALTH_WEBHOOK_SECRET", "testsecret")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post("/api/health/webhook", json={"data": {"metrics": []}})

    assert response.status_code == 401
    get_settings.cache_clear()


def test_webhook_rejects_wrong_token(monkeypatch):
    monkeypatch.setenv("HEALTH_WEBHOOK_SECRET", "testsecret")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/api/health/webhook",
        json={"data": {"metrics": []}},
        headers={"X-Webhook-Token": "wrong"},
    )

    assert response.status_code == 401
    get_settings.cache_clear()


def test_webhook_accepts_correct_token(monkeypatch):
    monkeypatch.setenv("HEALTH_WEBHOOK_SECRET", "testsecret")
    get_settings.cache_clear()
    calls = []
    monkeypatch.setattr(
        health_router.health_store,
        "store_payload",
        lambda payload, **kw: calls.append(payload) or 0,
    )
    client = TestClient(app)

    response = client.post(
        "/api/health/webhook",
        json={"data": {"metrics": []}},
        headers={"X-Webhook-Token": "testsecret"},
    )

    assert response.status_code == 204
    assert calls == [{"data": {"metrics": []}}]
    get_settings.cache_clear()
