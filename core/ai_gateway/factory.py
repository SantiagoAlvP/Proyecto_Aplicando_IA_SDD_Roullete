"""Resolve the AI provider from configuration.

This is the only place in the codebase allowed to import a concrete provider.
Services and routers depend on the :class:`AIGateway` interface, so changing
provider never touches business logic (Constitution, Principle II).
"""

import logging

from core.ai_gateway.ai_gateway import AIGateway
from core.ai_gateway.stub_provider import StubGateway
from core.settings.default import AppSettings

logger = logging.getLogger(__name__)


def get_ai_gateway(settings: AppSettings | None = None) -> AIGateway:
    """Return the gateway for the configured provider.

    Never raises because of a missing optional credential: an unusable provider
    degrades to the deterministic stub with a warning, so the application always
    boots (Constitution, Principle V).
    """
    settings = settings or AppSettings()
    provider = settings.resolved_ai_provider

    try:
        if provider == "groq":
            from core.ai_gateway.groq_provider import GroqGateway

            return GroqGateway(settings)

        if provider == "ollama":
            from core.ai_gateway.ollama_provider import OllamaGateway

            return OllamaGateway()

        if provider == "lmstudio":
            from core.ai_gateway.llmstudio_provider import OpenAIGateway

            return OpenAIGateway()

        if provider == "stub":
            return StubGateway()

        logger.warning(
            "Unknown AI_PROVIDER %r; falling back to the deterministic stub.",
            provider,
        )
    except Exception:  # noqa: BLE001 - a broken provider must not stop the boot
        logger.exception(
            "Could not initialise AI provider %r; falling back to the "
            "deterministic stub. Descriptions will be templated.",
            provider,
        )

    return StubGateway()
