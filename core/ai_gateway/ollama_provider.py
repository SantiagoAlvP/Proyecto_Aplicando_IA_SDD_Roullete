import asyncio

from strands import Agent
from strands.models.ollama import OllamaModel

from core.ai_gateway.ai_gateway import AIGateway
from core.settings.default import AppSettings

settings = AppSettings()


class OllamaGateway(AIGateway):
    def __init__(self, model: str = settings.OLLAMA_MODEL):
        self._ollama_model = OllamaModel(
            host=settings.OLLAMA_HOST,
            model_id=model,
        )
        self._agent = Agent(model=self._ollama_model)

    async def generate(self, prompt: str) -> str:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._agent, prompt)
        return str(result)
