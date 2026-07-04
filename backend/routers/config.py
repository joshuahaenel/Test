from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from backend import runtime_config
from backend.config import get_settings

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigUpdate(BaseModel):
    default_location: str | None = None
    auto_speak: bool | None = None


def _current_config() -> dict:
    settings = get_settings()
    return {
        "default_location": runtime_config.get(
            "default_location", settings.default_weather_location
        ),
        "model_name": settings.anthropic_model,
        "auto_speak": runtime_config.get("auto_speak", True),
    }


@router.get("")
async def read_config() -> dict:
    return _current_config()


@router.post("")
async def update_config(update: ConfigUpdate) -> dict:
    if update.default_location is not None:
        runtime_config.set("default_location", update.default_location)
    if update.auto_speak is not None:
        runtime_config.set("auto_speak", update.auto_speak)
    return _current_config()
