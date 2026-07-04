from __future__ import annotations

from backend import runtime_config, weather_client
from backend.config import get_settings


async def get_weather(location: str | None = None, units: str = "metric", **kwargs) -> dict:
    resolved = (
        location
        or runtime_config.get("default_location")
        or get_settings().default_weather_location
    )
    return await weather_client.get_weather(resolved, units=units)
