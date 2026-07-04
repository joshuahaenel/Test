from __future__ import annotations

from backend import calendar_client
from backend.config import get_settings


async def get_calendar_events(days: int = 7, **kwargs) -> list[dict]:
    settings = get_settings()
    return await calendar_client.get_upcoming_events(settings.timetree_ics_url, days=days)
