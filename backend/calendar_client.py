"""Read-only TimeTree calendar integration.

TimeTree has had no official public API since 2020. The only stable,
ToS-compliant way to read events from a TimeTree calendar is its "Calendar
sharing" feature, which produces a read-only ICS/webcal feed URL (the same
mechanism you'd use to subscribe a TimeTree calendar in Google Calendar).
This client fetches and parses that feed — there is no write access.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

import httpx
from icalendar import Calendar

CACHE_TTL = timedelta(minutes=15)

_cache: dict[str, tuple[datetime, list[dict]]] = {}


class CalendarNotConfiguredError(Exception):
    pass


def clear_cache() -> None:
    _cache.clear()


def _to_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    raise TypeError(f"Unsupported date/time value: {value!r}")


def parse_ics(raw_ics: str) -> list[dict]:
    calendar = Calendar.from_ical(raw_ics)
    events = []
    for component in calendar.walk("VEVENT"):
        start = component.get("dtstart")
        if start is None:
            continue
        end = component.get("dtend")
        events.append(
            {
                "summary": str(component.get("summary", "")),
                "start": _to_datetime(start.dt).isoformat(),
                "end": _to_datetime(end.dt).isoformat() if end else None,
                "location": str(component.get("location", "")) or None,
            }
        )
    events.sort(key=lambda e: e["start"])
    return events


async def fetch_events(ics_url: str, client: httpx.AsyncClient | None = None) -> list[dict]:
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=10.0)
    try:
        response = await client.get(ics_url)
        response.raise_for_status()
        return parse_ics(response.text)
    finally:
        if owns_client:
            await client.aclose()


async def get_upcoming_events(
    ics_url: str | None,
    days: int = 7,
    client: httpx.AsyncClient | None = None,
    now: datetime | None = None,
) -> list[dict]:
    if not ics_url:
        raise CalendarNotConfiguredError(
            "Kein TimeTree-Kalender konfiguriert (TIMETREE_ICS_URL fehlt)."
        )
    now = now or datetime.now(timezone.utc)

    cached = _cache.get(ics_url)
    if cached and now - cached[0] < CACHE_TTL:
        events = cached[1]
    else:
        events = await fetch_events(ics_url, client=client)
        _cache[ics_url] = (now, events)

    horizon = now + timedelta(days=days)
    return [e for e in events if now <= datetime.fromisoformat(e["start"]) <= horizon]
