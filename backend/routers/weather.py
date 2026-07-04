from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend import runtime_config, weather_client
from backend.config import get_settings

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("")
async def read_weather(
    location: str | None = Query(default=None),
    units: str = Query(default="metric", pattern="^(metric|imperial)$"),
):
    resolved_location = (
        location
        or runtime_config.get("default_location")
        or get_settings().default_weather_location
    )
    try:
        return await weather_client.get_weather(resolved_location, units=units)
    except weather_client.LocationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
