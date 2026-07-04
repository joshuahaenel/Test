"""FastAPI application factory for the Jarvis backend."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from backend.routers import calendar, chat, config, health, screen_time, training, weather

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def create_app() -> FastAPI:
    app = FastAPI(title="Jarvis")

    @app.get("/healthz")
    async def healthz() -> dict:
        return {"status": "ok"}

    app.include_router(weather.router)
    app.include_router(health.router)
    app.include_router(screen_time.router)
    app.include_router(training.router)
    app.include_router(calendar.router)
    app.include_router(chat.router)
    app.include_router(config.router)

    if FRONTEND_DIR.exists():
        app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

    return app


app = create_app()
