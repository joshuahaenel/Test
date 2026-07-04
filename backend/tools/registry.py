"""Claude tool-use schemas and dispatch.

`TOOL_SCHEMAS` is passed as `tools=` to the Anthropic API. `call_tool` maps a
`tool_use` block's name/input to the matching async function and normalizes
its return value into (result_text, actions) for the chat loop.
"""

from __future__ import annotations

import json
from typing import Any, Awaitable, Callable

from backend.tools import basics, browser, calendar, health, screen_time, training
from backend.tools import weather as weather_tool

ToolFunc = Callable[..., Awaitable[Any]]

TOOL_SCHEMAS: list[dict] = [
    {
        "name": "get_weather",
        "description": "Aktuelles Wetter und Kurzprognose für einen Ort abrufen.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Stadt- oder Ortsname"},
                "units": {"type": "string", "enum": ["metric", "imperial"]},
            },
        },
    },
    {
        "name": "open_url",
        "description": "Öffnet eine bestimmte URL im Standardbrowser des Nutzers.",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    },
    {
        "name": "open_youtube_video",
        "description": (
            "Spielt ein YouTube-Video ab. Bei einer URL oder Video-ID wird das Video "
            "direkt im Dashboard eingebettet und abgespielt. Bei einem Themen-/Freitext-"
            "Suchbegriff wird stattdessen die YouTube-Suche im Browser geöffnet."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "search_web",
        "description": "Öffnet eine Google-Suche für den angegebenen Begriff im Standardbrowser.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "get_health_summary",
        "description": "Liest die zuletzt über Health Auto Export synchronisierten Apple-Health-Daten.",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric": {"type": "string", "description": "z.B. step_count, heart_rate"},
                "days": {"type": "integer"},
            },
        },
    },
    {
        "name": "get_screen_time_summary",
        "description": "Liest die manuell eingetragene Bildschirmzeit-Historie.",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer"}},
        },
    },
    {
        "name": "log_screen_time",
        "description": "Trägt die Bildschirmzeit für einen Tag ein (in Minuten).",
        "input_schema": {
            "type": "object",
            "properties": {
                "minutes": {"type": "integer"},
                "date": {"type": "string", "description": "ISO-Datum, Standard: heute"},
            },
            "required": ["minutes"],
        },
    },
    {
        "name": "get_training_plan",
        "description": "Liest den aktuellen wöchentlichen Trainingsplan.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_calendar_events",
        "description": "Liest anstehende Termine aus dem read-only TimeTree-Kalender-Feed.",
        "input_schema": {
            "type": "object",
            "properties": {"days": {"type": "integer"}},
        },
    },
    {
        "name": "get_time",
        "description": "Gibt die aktuelle Uhrzeit zurück.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_date",
        "description": "Gibt das heutige Datum zurück.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "tell_joke",
        "description": "Erzählt einen Witz.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

_DISPATCH: dict[str, ToolFunc] = {
    "get_weather": weather_tool.get_weather,
    "open_url": browser.open_url,
    "open_youtube_video": browser.open_youtube_video,
    "search_web": browser.search_web,
    "get_health_summary": health.get_health_summary,
    "get_screen_time_summary": screen_time.get_screen_time_summary,
    "log_screen_time": screen_time.log_screen_time,
    "get_training_plan": training.get_training_plan,
    "get_calendar_events": calendar.get_calendar_events,
    "get_time": basics.get_time,
    "get_date": basics.get_date,
    "tell_joke": basics.tell_joke,
}


class UnknownToolError(Exception):
    pass


async def call_tool(name: str, arguments: dict) -> tuple[str, list[dict]]:
    """Executes a tool by name, returning (result_text, actions)."""
    func = _DISPATCH.get(name)
    if func is None:
        raise UnknownToolError(f"Unbekanntes Tool: {name}")

    result = await func(**arguments)

    if isinstance(result, dict) and "result" in result:
        return result["result"], result.get("actions", [])
    if isinstance(result, str):
        return result, []
    return json.dumps(result, ensure_ascii=False), []
