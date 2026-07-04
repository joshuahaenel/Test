from __future__ import annotations

from backend import training_store


async def get_training_plan(**kwargs) -> dict:
    return training_store.get_plan()
