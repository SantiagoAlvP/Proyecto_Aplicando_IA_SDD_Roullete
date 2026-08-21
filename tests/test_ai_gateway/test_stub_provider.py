"""Degraded mode must still produce a usable answer."""

import json

import pytest

from core.ai_gateway.stub_provider import StubGateway

DESCRIBE_PROMPT = (
    "- Language  : Rust\n- Technology: Distributed Cache\n- Addon     : Docker\n"
)


@pytest.mark.asyncio
async def test_selection_prompts_get_valid_json() -> None:
    payload = json.loads(await StubGateway().generate("choose the best_index please"))
    assert payload["best_index"] == 1
    assert payload["valid"] is True


@pytest.mark.asyncio
async def test_description_mentions_the_actual_stack() -> None:
    text = await StubGateway().generate(DESCRIBE_PROMPT)
    assert "Rust" in text
    assert "Distributed Cache" in text
    assert "Docker" in text


@pytest.mark.asyncio
async def test_description_is_plain_prose() -> None:
    text = await StubGateway().generate(DESCRIBE_PROMPT)
    assert "\n" not in text
    assert not text.startswith(("-", "*", "#"))


@pytest.mark.asyncio
async def test_unknown_fields_do_not_crash_it() -> None:
    assert await StubGateway().generate("nothing useful here")
