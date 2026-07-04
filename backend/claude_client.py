"""Wraps the Anthropic SDK for Jarvis's conversation loop."""

from __future__ import annotations

from anthropic import AsyncAnthropic

from backend.config import get_settings

SYSTEM_PROMPT = (
    "Du bist Jarvis, ein hilfsbereiter, präziser persönlicher Assistent. "
    "Antworte auf Deutsch, kurz und freundlich. Nutze die verfügbaren Tools, "
    "wenn eine Anfrage aktuelle Daten braucht (Wetter, Gesundheit, Kalender, "
    "Bildschirmzeit, Trainingsplan) oder eine Aktion auslösen soll "
    "(Webseite oder YouTube-Video öffnen)."
)

MAX_TOKENS = 1024


def build_client() -> AsyncAnthropic:
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY ist nicht gesetzt. Bitte in backend/.env eintragen."
        )
    return AsyncAnthropic(api_key=settings.anthropic_api_key)


async def create_message(client: AsyncAnthropic, messages: list[dict], tools: list[dict]):
    settings = get_settings()
    return await client.messages.create(
        model=settings.anthropic_model,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        tools=tools,
        messages=messages,
    )
