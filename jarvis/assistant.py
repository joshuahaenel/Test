"""Core dispatch logic for Jarvis.

Jarvis.process(text) takes a single line of user input and returns the
response text. It is deliberately transport-agnostic: the same logic is
used whether the input came from the keyboard (text mode) or from speech
recognition (voice mode).
"""

from __future__ import annotations

from jarvis import commands

EXIT_WORDS = {"exit", "quit", "beende dich", "tschüss", "auf wiedersehen"}


class Jarvis:
    """Stateless-ish command router for the assistant."""

    def process(self, text: str) -> str:
        text = (text or "").strip()
        lowered = text.lower()

        if not lowered:
            return "Ich habe nichts gehört."

        if lowered in EXIT_WORDS:
            return "Auf Wiedersehen!"

        if any(word in lowered for word in ("hallo", "hi", "hey")):
            return commands.greet()

        if "uhrzeit" in lowered or "wie spät" in lowered:
            return commands.get_time()

        if "datum" in lowered or "welcher tag" in lowered:
            return commands.get_date()

        if "witz" in lowered:
            return commands.tell_joke()

        if lowered.startswith("suche nach ") or lowered.startswith("suche "):
            query = lowered.split("suche nach ", 1)[-1] if "suche nach " in lowered else lowered.split("suche ", 1)[-1]
            return commands.web_search(query)

        return commands.unknown(text)

    def is_exit(self, text: str) -> bool:
        return (text or "").strip().lower() in EXIT_WORDS
