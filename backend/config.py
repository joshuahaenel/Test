"""Application settings, loaded from environment variables / .env."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"
    health_webhook_secret: str = "changeme"
    timetree_ics_url: str | None = None
    jarvis_port: int = 8000
    default_weather_location: str = "Berlin"


@lru_cache
def get_settings() -> Settings:
    return Settings()
