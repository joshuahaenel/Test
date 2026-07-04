from datetime import datetime, timezone

import httpx
import pytest
import respx

from backend import calendar_client

SAMPLE_ICS = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test//EN
BEGIN:VEVENT
UID:1
SUMMARY:Zahnarzt
DTSTART:20260705T090000Z
DTEND:20260705T100000Z
LOCATION:Praxis Mueller
END:VEVENT
BEGIN:VEVENT
UID:2
SUMMARY:Vergangener Termin
DTSTART:20260601T090000Z
DTEND:20260601T100000Z
END:VEVENT
BEGIN:VEVENT
UID:3
SUMMARY:Weit in der Zukunft
DTSTART:20261001T090000Z
DTEND:20261001T100000Z
END:VEVENT
END:VCALENDAR
"""


def test_parse_ics_extracts_events():
    events = calendar_client.parse_ics(SAMPLE_ICS)

    assert len(events) == 3
    zahnarzt = next(e for e in events if e["summary"] == "Zahnarzt")
    assert zahnarzt["location"] == "Praxis Mueller"


@respx.mock
async def test_get_upcoming_events_filters_by_window():
    calendar_client.clear_cache()
    ics_url = "https://example.com/calendar.ics"
    respx.get(ics_url).mock(return_value=httpx.Response(200, text=SAMPLE_ICS))
    now = datetime(2026, 7, 4, tzinfo=timezone.utc)

    events = await calendar_client.get_upcoming_events(ics_url, days=7, now=now)

    assert len(events) == 1
    assert events[0]["summary"] == "Zahnarzt"


async def test_get_upcoming_events_requires_configured_url():
    with pytest.raises(calendar_client.CalendarNotConfiguredError):
        await calendar_client.get_upcoming_events(None)


@respx.mock
async def test_get_upcoming_events_uses_cache():
    calendar_client.clear_cache()
    ics_url = "https://example.com/cached-calendar.ics"
    route = respx.get(ics_url).mock(return_value=httpx.Response(200, text=SAMPLE_ICS))
    now = datetime(2026, 7, 4, tzinfo=timezone.utc)

    await calendar_client.get_upcoming_events(ics_url, days=7, now=now)
    await calendar_client.get_upcoming_events(ics_url, days=7, now=now)

    assert route.call_count == 1
