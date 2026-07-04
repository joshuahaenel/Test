from __future__ import annotations

from backend import health_store


async def get_health_summary(metric: str | None = None, days: int = 1, **kwargs) -> dict:
    if metric:
        return {"samples": health_store.recent_samples(metric=metric, days=days)}
    return health_store.latest_summary()
