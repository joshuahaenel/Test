"""In-memory store for user-adjustable, non-secret settings that can change
without restarting the backend (unlike the .env-based Settings)."""

from __future__ import annotations

_state: dict = {}


def get(key: str, default=None):
    return _state.get(key, default)


def set(key: str, value) -> None:
    _state[key] = value


def clear() -> None:
    _state.clear()
