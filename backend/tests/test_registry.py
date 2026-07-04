import pytest

from backend.tools import registry


def test_every_schema_has_a_dispatch_entry():
    schema_names = {schema["name"] for schema in registry.TOOL_SCHEMAS}
    assert schema_names == set(registry._DISPATCH.keys())


async def test_call_tool_normalizes_dict_with_result_and_actions():
    async def fake_tool(**kwargs):
        return {"result": "ok", "actions": [{"type": "noop"}]}

    registry._DISPATCH["_fake"] = fake_tool
    try:
        text, actions = await registry.call_tool("_fake", {})
        assert text == "ok"
        assert actions == [{"type": "noop"}]
    finally:
        del registry._DISPATCH["_fake"]


async def test_call_tool_normalizes_plain_string():
    async def fake_tool(**kwargs):
        return "hallo"

    registry._DISPATCH["_fake"] = fake_tool
    try:
        text, actions = await registry.call_tool("_fake", {})
        assert text == "hallo"
        assert actions == []
    finally:
        del registry._DISPATCH["_fake"]


async def test_call_tool_normalizes_other_types_to_json():
    async def fake_tool(**kwargs):
        return [1, 2, 3]

    registry._DISPATCH["_fake"] = fake_tool
    try:
        text, actions = await registry.call_tool("_fake", {})
        assert text == "[1, 2, 3]"
        assert actions == []
    finally:
        del registry._DISPATCH["_fake"]


async def test_call_tool_unknown_tool_raises():
    with pytest.raises(registry.UnknownToolError):
        await registry.call_tool("does_not_exist", {})


async def test_get_time_and_tell_joke_via_registry():
    from jarvis import commands

    text, actions = await registry.call_tool("get_time", {})
    assert "Uhr" in text
    assert actions == []

    text, _ = await registry.call_tool("tell_joke", {})
    assert text in commands.JOKES
