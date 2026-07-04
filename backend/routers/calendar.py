from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend import calendar_client
from backend.config import get_settings

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("/events")
async def read_events(days: int = 7) -> list[dict]:
    settings = get_settings()
    try:
        return await calendar_client.get_upcoming_events(settings.timetree_ics_url, days=days)
    except calendar_client.CalendarNotConfiguredError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
