"""Tools that open things for the user: URLs, web search, YouTube videos.

Without a YouTube Data API key, Claude cannot pick "the best video" for a
free-text topic and embed it directly (YouTube's search-results page also
can't be iframe-embedded). So: an exact URL/video ID gets embedded and played
in the dashboard's Now Playing widget; free text opens a YouTube search page
externally and the user picks.
"""

from __future__ import annotations

import re
import webbrowser

from jarvis import commands

YOUTUBE_ID_RE = re.compile(r"^[\w-]{11}$")
YOUTUBE_URL_RE = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]{11})")


def _extract_youtube_id(query: str) -> str | None:
    query = query.strip()
    match = YOUTUBE_URL_RE.search(query)
    if match:
        return match.group(1)
    if YOUTUBE_ID_RE.match(query):
        return query
    return None


async def open_url(url: str, opener=webbrowser.open, **kwargs) -> dict:
    opener(url)
    return {"result": f"Öffne {url} im Standardbrowser."}


async def search_web(query: str, opener=webbrowser.open, **kwargs) -> dict:
    return {"result": commands.web_search(query, opener=opener)}


async def open_youtube_video(query: str, opener=webbrowser.open, **kwargs) -> dict:
    video_id = _extract_youtube_id(query)
    if video_id:
        return {
            "result": f"Spiele YouTube-Video {video_id} ab.",
            "actions": [
                {
                    "type": "play_youtube",
                    "video_id": video_id,
                    "embed_url": f"https://www.youtube.com/embed/{video_id}",
                }
            ],
        }
    search_url = f"https://www.youtube.com/results?search_query={query.strip().replace(' ', '+')}"
    opener(search_url)
    return {
        "result": (
            f"Ich konnte kein bestimmtes Video für '{query}' erkennen, "
            "daher öffne ich die YouTube-Suche im Browser."
        )
    }
