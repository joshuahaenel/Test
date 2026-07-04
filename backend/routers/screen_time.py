from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from backend import screen_time_store

router = APIRouter(prefix="/api/screen-time", tags=["screen-time"])


class ScreenTimeEntry(BaseModel):
    minutes: int
    date: str | None = None


@router.get("")
async def read_history(days: int = 7) -> list[dict]:
    return screen_time_store.get_history(days=days)


@router.post("")
async def create_entry(entry: ScreenTimeEntry) -> dict:
    return screen_time_store.log_entry(entry.minutes, entry_date=entry.date)
