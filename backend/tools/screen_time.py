from __future__ import annotations

from backend import screen_time_store


async def get_screen_time_summary(days: int = 7, **kwargs) -> list[dict]:
    return screen_time_store.get_history(days=days)


async def log_screen_time(minutes: int, date: str | None = None, **kwargs) -> dict:
    return screen_time_store.log_entry(minutes, entry_date=date)
