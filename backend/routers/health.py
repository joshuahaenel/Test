from __future__ import annotations

import hmac

from fastapi import APIRouter, Header, HTTPException, Request

from backend import health_store
from backend.config import get_settings

router = APIRouter(prefix="/api/health", tags=["health"])


def _check_token(token: str | None) -> None:
    settings = get_settings()
    if not token or not hmac.compare_digest(token, settings.health_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook token")


@router.post("/webhook", status_code=204)
async def receive_webhook(
    request: Request, x_webhook_token: str | None = Header(default=None)
) -> None:
    _check_token(x_webhook_token)
    payload = await request.json()
    health_store.store_payload(payload)


@router.get("/latest")
async def read_latest() -> dict:
    return health_store.latest_summary()
