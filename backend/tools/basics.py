"""Thin async wrappers around the existing jarvis.commands handlers."""

from __future__ import annotations

from jarvis import commands


async def get_time(**kwargs) -> str:
    return commands.get_time()


async def get_date(**kwargs) -> str:
    return commands.get_date()


async def tell_joke(**kwargs) -> str:
    return commands.tell_joke()
