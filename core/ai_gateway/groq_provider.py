"""Groq provider - the production gateway.

Groq exposes an OpenAI-compatible API with a free tier, which is what lets the
whole system run at USD 0.00 (Constitution, Principle V). Ollama cannot be used
in production because serving a model needs gigabytes of RAM that no free tier
offers; because the LLM sits behind :class:`AIGateway`, swapping it is a single
environment variable.
"""

import logging

from openai import AsyncOpenAI

from core.ai_gateway.ai_gateway import AIGateway
from core.settings.default import AppSettings

logger = logging.getLogger(__name__)


class GroqGateway(AIGateway):
    def __init__(self, settings: AppSettings | None = None) -> None:
        self._settings = settings or AppSettings()
        if not self._settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is required to use the groq provider. "
                "Set it as an environment variable, never in source control."
            )
        self._client = AsyncOpenAI(
            base_url=self._settings.GROQ_BASE_URL,
            api_key=self._settings.GROQ_API_KEY,
            timeout=self._settings.AI_TIMEOUT_SECONDS,
            max_retries=1,
        )
        self._model = self._settings.GROQ_MODEL

    async def generate(self, prompt: str) -> str:
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=self._settings.message_base(prompt),  # ty: ignore[invalid-argument-type]
            temperature=self._settings.TEMPERATURE,
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Groq returned an empty completion.")
        return content.strip()
