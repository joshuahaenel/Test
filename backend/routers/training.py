from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend import training_store

router = APIRouter(prefix="/api/training-plan", tags=["training-plan"])


class TrainingDayUpdate(BaseModel):
    day: str
    description: str


@router.get("")
async def read_plan() -> dict:
    return training_store.get_plan()


@router.put("")
async def update_day(update: TrainingDayUpdate) -> dict:
    try:
        return training_store.set_day(update.day, update.description)
    except training_store.InvalidDayError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
