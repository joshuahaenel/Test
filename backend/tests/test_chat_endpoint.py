import pytest
from fastapi.testclient import TestClient

from backend import conversation
from backend.app import app
from backend.routers import chat as chat_router


class FakeBlock:
    def __init__(self, type_, **kwargs):
        self.type = type_
        for key, value in kwargs.items():
            setattr(self, key, value)


class FakeResponse:
    def __init__(self, content, stop_reason):
        self.content = content
        self.stop_reason = stop_reason


def _fake_create_message(responses):
    responses = iter(responses)

    async def fake(client, messages, tools):
        return next(responses)

    return fake


@pytest.fixture(autouse=True)
def _reset_conversations():
    conversation.clear_all()
    yield
    conversation.clear_all()


@pytest.fixture
def client():
    return TestClient(app)


def test_plain_conversational_reply(monkeypatch, client):
    responses = [FakeResponse([FakeBlock("text", text="Hallo, wie kann ich helfen?")], "end_turn")]
    monkeypatch.setattr(chat_router, "create_message", _fake_create_message(responses))
    monkeypatch.setattr(chat_router, "build_client", lambda: object())

    response = client.post("/api/chat", json={"session_id": "s1", "message": "hallo"})

    assert response.status_code == 200
    body = response.json()
    assert body["reply"] == "Hallo, wie kann ich helfen?"
    assert body["actions"] == []
    assert body["session_id"] == "s1"


def test_single_tool_call(monkeypatch, client):
    responses = [
        FakeResponse([FakeBlock("tool_use", id="t1", name="get_time", input={})], "tool_use"),
        FakeResponse([FakeBlock("text", text="Es ist gerade spaet.")], "end_turn"),
    ]
    monkeypatch.setattr(chat_router, "create_message", _fake_create_message(responses))
    monkeypatch.setattr(chat_router, "build_client", lambda: object())

    response = client.post("/api/chat", json={"session_id": "s2", "message": "wie spaet ist es"})

    assert response.status_code == 200
    assert response.json()["reply"] == "Es ist gerade spaet."


def test_multiple_tool_calls_in_one_turn(monkeypatch, client):
    responses = [
        FakeResponse(
            [
                FakeBlock("tool_use", id="t1", name="get_time", input={}),
                FakeBlock("tool_use", id="t2", name="tell_joke", input={}),
            ],
            "tool_use",
        ),
        FakeResponse([FakeBlock("text", text="Hier beides.")], "end_turn"),
    ]
    monkeypatch.setattr(chat_router, "create_message", _fake_create_message(responses))
    monkeypatch.setattr(chat_router, "build_client", lambda: object())

    response = client.post("/api/chat", json={"session_id": "s3", "message": "witz und uhrzeit"})

    assert response.json()["reply"] == "Hier beides."


def test_tool_error_is_handled_gracefully(monkeypatch, client):
    responses = [
        FakeResponse(
            [FakeBlock("tool_use", id="t1", name="does_not_exist", input={})], "tool_use"
        ),
        FakeResponse([FakeBlock("text", text="Das ging leider nicht.")], "end_turn"),
    ]
    monkeypatch.setattr(chat_router, "create_message", _fake_create_message(responses))
    monkeypatch.setattr(chat_router, "build_client", lambda: object())

    response = client.post("/api/chat", json={"session_id": "s4", "message": "tu etwas unbekanntes"})

    assert response.status_code == 200
    assert response.json()["reply"] == "Das ging leider nicht."


def test_youtube_tool_action_is_surfaced(monkeypatch, client):
    responses = [
        FakeResponse(
            [
                FakeBlock(
                    "tool_use",
                    id="t1",
                    name="open_youtube_video",
                    input={"query": "https://youtu.be/dQw4w9WgXcQ"},
                )
            ],
            "tool_use",
        ),
        FakeResponse([FakeBlock("text", text="Video wird abgespielt.")], "end_turn"),
    ]
    monkeypatch.setattr(chat_router, "create_message", _fake_create_message(responses))
    monkeypatch.setattr(chat_router, "build_client", lambda: object())

    response = client.post("/api/chat", json={"session_id": "s5", "message": "spiel das video"})

    body = response.json()
    assert body["actions"][0]["video_id"] == "dQw4w9WgXcQ"


def test_history_accumulates_across_requests(monkeypatch, client):
    call_log = []

    async def fake_create_message(client_arg, messages, tools):
        call_log.append([dict(m) for m in messages])
        return FakeResponse([FakeBlock("text", text=f"Antwort {len(call_log)}")], "end_turn")

    monkeypatch.setattr(chat_router, "create_message", fake_create_message)
    monkeypatch.setattr(chat_router, "build_client", lambda: object())

    client.post("/api/chat", json={"session_id": "s6", "message": "erste nachricht"})
    client.post("/api/chat", json={"session_id": "s6", "message": "zweite nachricht"})

    assert len(call_log[1]) == 3  # user, assistant, user
    assert call_log[1][0]["content"] == "erste nachricht"
    assert call_log[1][2]["content"] == "zweite nachricht"
