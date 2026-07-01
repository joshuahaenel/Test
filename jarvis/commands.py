"""Individual command handlers used by the assistant.

Each handler is a plain function that takes the parsed command text (and
optional dependencies for testing) and returns the string Jarvis should
speak/print back. Keeping handlers side-effect-light and dependency-injected
makes them straightforward to unit test.
"""

from __future__ import annotations

import datetime as _datetime
import random
import webbrowser

JOKES = [
    "Warum können Geister so schlecht lügen? Weil man durch sie hindurchsieht.",
    "Ich habe eine Diät auf Lebenszeit angefangen... die letzten drei Stunden liefen super.",
    "Was ist ein Keks unter einem Baum? Ein schattiges Plätzchen.",
]


def greet() -> str:
    return "Hallo, ich bin Jarvis. Wie kann ich helfen?"


def get_time(now: _datetime.datetime | None = None) -> str:
    now = now or _datetime.datetime.now()
    return f"Es ist {now.strftime('%H:%M')} Uhr."


def get_date(today: _datetime.date | None = None) -> str:
    today = today or _datetime.date.today()
    return f"Heute ist der {today.strftime('%d.%m.%Y')}."


def tell_joke(rng: random.Random | None = None) -> str:
    rng = rng or random
    return rng.choice(JOKES)


def web_search(query: str, opener=webbrowser.open) -> str:
    query = query.strip()
    if not query:
        return "Wonach soll ich suchen?"
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    opener(url)
    return f"Ich suche im Web nach: {query}"


def unknown(text: str) -> str:
    return f"Das habe ich nicht verstanden: '{text}'."
