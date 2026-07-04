import pytest

from backend.tools import browser


async def test_open_url_calls_opener():
    calls = []
    result = await browser.open_url("https://example.com", opener=calls.append)
    assert calls == ["https://example.com"]
    assert "example.com" in result["result"]


async def test_search_web_calls_opener_with_query():
    calls = []
    result = await browser.search_web("python tutorials", opener=calls.append)
    assert calls == ["https://www.google.com/search?q=python+tutorials"]
    assert "python tutorials" in result["result"]


async def test_open_youtube_video_with_url_embeds_without_opening_browser():
    calls = []
    result = await browser.open_youtube_video(
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ", opener=calls.append
    )
    assert calls == []
    assert result["actions"][0]["video_id"] == "dQw4w9WgXcQ"
    assert result["actions"][0]["embed_url"] == "https://www.youtube.com/embed/dQw4w9WgXcQ"


async def test_open_youtube_video_with_bare_id_embeds():
    calls = []
    result = await browser.open_youtube_video("dQw4w9WgXcQ", opener=calls.append)
    assert calls == []
    assert result["actions"][0]["video_id"] == "dQw4w9WgXcQ"


async def test_open_youtube_video_with_free_text_opens_search():
    calls = []
    result = await browser.open_youtube_video("lofi beats zum lernen", opener=calls.append)
    assert len(calls) == 1
    assert "youtube.com/results" in calls[0]
    assert "actions" not in result
