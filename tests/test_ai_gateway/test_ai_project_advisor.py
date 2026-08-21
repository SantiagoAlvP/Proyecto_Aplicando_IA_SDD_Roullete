"""The advisor turns any gateway into project decisions - and never propagates
a provider failure to the user (spec 001, FR-009 and Edge Cases)."""

import pytest

from core.ai_gateway.ai_gateway import AIGateway
from core.ensemble_project.ai_project_advisor import AIProjectAdvisor

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


class ScriptedGateway(AIGateway):
    def __init__(self, reply: str) -> None:
        self._reply = reply

    async def generate(self, prompt: str) -> str:
        return self._reply


class BrokenGateway(AIGateway):
    async def generate(self, prompt: str) -> str:
        raise ConnectionError("provider is down")


@pytest.mark.asyncio
async def test_parses_a_clean_json_answer() -> None:
    advisor = AIProjectAdvisor(
        ScriptedGateway('{"best_index": 2, "valid": true, "reason": ""}')
    )
    selection = await advisor.choose_valid_project(CANDIDATES)
    assert selection.best_index == 2
    assert selection.valid is True


@pytest.mark.asyncio
async def test_extracts_json_wrapped_in_prose_or_fences() -> None:
    """Models pad their answers; the parser must not be fooled by it."""
    noisy = 'Sure! ```json\n{"best_index": 2, "valid": true}\n``` Hope that helps.'
    selection = await AIProjectAdvisor(ScriptedGateway(noisy)).choose_valid_project(
        CANDIDATES
    )
    assert selection.best_index == 2


@pytest.mark.asyncio
async def test_an_out_of_range_index_is_clamped_not_raised() -> None:
    advisor = AIProjectAdvisor(
        ScriptedGateway('{"best_index": 99, "valid": true, "reason": ""}')
    )
    selection = await advisor.choose_valid_project(CANDIDATES)
    assert selection.best_index == 1


@pytest.mark.asyncio
async def test_an_invalid_verdict_keeps_its_reason() -> None:
    advisor = AIProjectAdvisor(
        ScriptedGateway('{"best_index": 1, "valid": false, "reason": "not buildable"}')
    )
    selection = await advisor.choose_valid_project(CANDIDATES)
    assert selection.valid is False
    assert selection.reason == "not buildable"


@pytest.mark.asyncio
async def test_unparseable_output_degrades_to_the_first_candidate() -> None:
    selection = await AIProjectAdvisor(
        ScriptedGateway("I am afraid I cannot do that")
    ).choose_valid_project(CANDIDATES)
    assert selection.valid is True
    assert selection.best_index == 1


@pytest.mark.asyncio
async def test_a_dead_provider_does_not_break_selection() -> None:
    selection = await AIProjectAdvisor(BrokenGateway()).choose_valid_project(CANDIDATES)
    assert selection.valid is True


@pytest.mark.asyncio
async def test_a_dead_provider_still_produces_a_description() -> None:
    description = await AIProjectAdvisor(BrokenGateway()).generate_description(PROJECT)
    assert description
    assert "Rust" in description


@pytest.mark.asyncio
async def test_an_empty_answer_falls_back_instead_of_returning_nothing() -> None:
    description = await AIProjectAdvisor(ScriptedGateway("   ")).generate_description(
        PROJECT
    )
    assert description.strip()


@pytest.mark.asyncio
async def test_description_is_truncated_to_the_column_size() -> None:
    advisor = AIProjectAdvisor(ScriptedGateway("x" * 5000))
    assert len(await advisor.generate_description(PROJECT)) <= 500


@pytest.mark.asyncio
async def test_no_candidates_is_reported_as_invalid() -> None:
    selection = await AIProjectAdvisor(ScriptedGateway("{}")).choose_valid_project([])
    assert selection.valid is False
