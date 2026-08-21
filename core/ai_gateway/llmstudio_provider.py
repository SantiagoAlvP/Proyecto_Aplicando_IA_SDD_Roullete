from openai import AsyncOpenAI

from core.ai_gateway.ai_gateway import AIGateway
from core.settings.default import AppSettings

settings = AppSettings()


class OpenAIGateway(AIGateway):
    def __init__(
        self,
        base_url: str = settings.BASE_URL_LMSTUDIO,
        api_key: str = settings.API_KEY_LMSTUDIO,
        model: str = settings.LMSTUDIO_MODEL,
    ):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=settings.message_base(prompt),  # ty: ignore[invalid-argument-type]
            temperature=settings.TEMPERATURE,
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Model returned no text.")

        return content
