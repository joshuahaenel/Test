"""In-memory per-session conversation history.

Session state is lost on backend restart — fine for a single-user local app.
If long-lived sessions become a problem (context growth), truncation/
summarization would need to be added; out of scope for the MVP.
"""

from __future__ import annotations

from typing import Any

_sessions: dict[str, list[dict[str, Any]]] = {}


def get_history(session_id: str) -> list[dict[str, Any]]:
    return _sessions.setdefault(session_id, [])


def clear_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def clear_all() -> None:
    _sessions.clear()
