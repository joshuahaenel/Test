"""POST /api/chat — the Claude tool-use conversation loop.

A `tool_use` block Claude emits must be replayed alongside its matching
`tool_result` on the next call, or subsequent turns break — this is why the
raw (serialized) content-block structure is stored in history, not just the
final text.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from backend import conversation
from backend.claude_client import build_client, create_message
from backend.tools.registry import TOOL_SCHEMAS, call_tool

router = APIRouter(prefix="/api/chat", tags=["chat"])

MAX_TOOL_ITERATIONS = 5


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    actions: list[dict] = []


def _serialize_block(block) -> dict:
    if block.type == "text":
        return {"type": "text", "text": block.text}
    if block.type == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    raise ValueError(f"Unsupported content block type: {block.type}")


async def run_chat_turn(session_id: str, message: str) -> tuple[str, list[dict]]:
    client = build_client()
    history = conversation.get_history(session_id)
    history.append({"role": "user", "content": message})

    all_actions: list[dict] = []
    for _ in range(MAX_TOOL_ITERATIONS):
        response = await create_message(client, history, TOOL_SCHEMAS)
        assistant_content = [_serialize_block(block) for block in response.content]
        history.append({"role": "assistant", "content": assistant_content})

        if response.stop_reason != "tool_use":
            final_text = "".join(
                block["text"] for block in assistant_content if block["type"] == "text"
            )
            return final_text, all_actions

        tool_results = []
        for block in assistant_content:
            if block["type"] != "tool_use":
                continue
            try:
                text, actions = await call_tool(block["name"], block["input"])
                all_actions.extend(actions)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block["id"], "content": text}
                )
            except Exception as exc:  # a failing tool must not crash the chat endpoint
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": f"Fehler: {exc}",
                        "is_error": True,
                    }
                )
        history.append({"role": "user", "content": tool_results})

    return "Entschuldigung, das dauert zu lange - bitte versuch es noch einmal.", all_actions


@router.post("")
async def chat(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or str(uuid.uuid4())
    reply, actions = await run_chat_turn(session_id, request.message)
    return ChatResponse(session_id=session_id, reply=reply, actions=actions)
