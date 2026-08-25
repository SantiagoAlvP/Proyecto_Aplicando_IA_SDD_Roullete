"""Tests for the AI generation toggle (HU-21).

When AI_GENERATION_ENABLED is false, every generation call routes to the
deterministic stub — no external provider is contacted and the project is
still persisted with all its fields.
"""

import pytest

from core.ai_gateway.ai_gateway import AIGateway
from core.ensemble_project.ai_project_advisor import AIProjectAdvisor
from core.settings.default import AppSettings


CANDIDATES = [
    {"programming_language": "Rust", "technologies": "Cache", "addons": "Docker"},
    {"programming_language": "Go", "technologies": "Queue", "addons": "pytest"},
]

PROJECT = {
    "programming_language": "Rust",
    "technologies": "Cache",
    "addons": "Docker",
    "level": 3,
    "extras": [],
}


class SpyGateway(AIGateway):
    """Records calls without actually doing anything useful."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        raise AssertionError("Gateway should NOT be called when toggle is off")


class ScriptedGateway(AIGateway):
    """Returns a canned response and records the call."""

    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.calls: list[str] = []

    async def generate(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self._reply


# ── US1: toggle disabled ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_description_returns_fallback_when_toggle_off() -> None:
    settings = AppSettings(AI_GENERATION_ENABLED=False)
    spy = SpyGateway()
    advisor = AIProjectAdvisor(spy, settings=settings)

    description = await advisor.generate_description(PROJECT)

    assert description, "Description must not be empty"
    assert "Rust" in description, "Fallback must mention the language"
    assert len(spy.calls) == 0, "Real gateway must not be contacted"


@pytest.mark.asyncio
async def test_selection_uses_first_candidate_when_toggle_off() -> None:
    settings = AppSettings(AI_GENERATION_ENABLED=False)
    spy = SpyGateway()
    advisor = AIProjectAdvisor(spy, settings=settings)

    selection = await advisor.choose_valid_project(CANDIDATES)

    assert selection.best_index == 1
    assert selection.valid is True
    assert len(spy.calls) == 0, "Real gateway must not be contacted"


# ── US2: toggle enabled (default) ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_description_calls_gateway_when_toggle_on() -> None:
    gw = ScriptedGateway("A Rust project using Cache.")
    advisor = AIProjectAdvisor(gw)

    description = await advisor.generate_description(PROJECT)

    assert description == "A Rust project using Cache."
    assert len(gw.calls) == 1, "Gateway must be called exactly once"


@pytest.mark.asyncio
async def test_selection_calls_gateway_when_toggle_on() -> None:
    gw = ScriptedGateway('{"best_index": 2, "valid": true, "reason": ""}')
    advisor = AIProjectAdvisor(gw)

    selection = await advisor.choose_valid_project(CANDIDATES)

    assert selection.best_index == 2
    assert selection.valid is True
    assert len(gw.calls) == 1, "Gateway must be called exactly once"


# ── US3: diagnostics toggle field ───────────────────────────────────────────


def diagnostics_of(settings: AppSettings) -> dict:
    from fastapi.testclient import TestClient
    from core.main import boostrap

    client = TestClient(boostrap(settings))
    return client.get("/api/health/diagnostics").json()


def test_diagnostics_reports_ai_generation_enabled_true_by_default() -> None:
    body = diagnostics_of(AppSettings())
    assert body["ai"]["ai_generation_enabled"] is True


def test_diagnostics_reports_ai_generation_enabled_false_when_off() -> None:
    body = diagnostics_of(AppSettings(AI_GENERATION_ENABLED=False))
    assert body["ai"]["ai_generation_enabled"] is False
