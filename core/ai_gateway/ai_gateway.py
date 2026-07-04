from abc import ABC, abstractmethod


class AIGateway(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str: ...
