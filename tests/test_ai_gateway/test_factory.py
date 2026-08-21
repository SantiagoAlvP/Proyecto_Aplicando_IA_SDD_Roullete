"""The provider is configuration, not architecture (spec 001, D-01)."""

from core.ai_gateway.factory import get_ai_gateway
from core.ai_gateway.stub_provider import StubGateway
from core.settings.default import AppSettings


def test_auto_resolves_to_groq_when_a_key_is_present() -> None:
    settings = AppSettings(AI_PROVIDER="auto", GROQ_API_KEY="gsk-test-not-a-real-key")
    assert settings.resolved_ai_provider == "groq"


def test_auto_resolves_to_the_stub_without_a_key() -> None:
    settings = AppSettings(AI_PROVIDER="auto", GROQ_API_KEY=None)
    assert settings.resolved_ai_provider == "stub"


def test_explicit_provider_wins_over_auto_detection() -> None:
    settings = AppSettings(AI_PROVIDER="stub", GROQ_API_KEY="gsk-test-not-a-real-key")
    assert settings.resolved_ai_provider == "stub"


def test_stub_provider_is_returned_for_the_stub_setting() -> None:
    gateway = get_ai_gateway(AppSettings(AI_PROVIDER="stub"))
    assert isinstance(gateway, StubGateway)


def test_groq_is_returned_when_configured() -> None:
    gateway = get_ai_gateway(
        AppSettings(AI_PROVIDER="groq", GROQ_API_KEY="gsk-test-not-a-real-key")
    )
    assert type(gateway).__name__ == "GroqGateway"


def test_a_provider_that_cannot_start_degrades_instead_of_crashing() -> None:
    """Missing optional credentials must never stop the app from booting."""
    gateway = get_ai_gateway(AppSettings(AI_PROVIDER="groq", GROQ_API_KEY=None))
    assert isinstance(gateway, StubGateway)
