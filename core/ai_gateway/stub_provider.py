"""Deterministic gateway - used by tests and as the degraded-mode fallback.

A demo that dies because a third-party LLM is rate limiting us costs more than
an imperfect description (Constitution, Principle V). This gateway needs no
network, no credentials and no latency, and always answers.
"""

import json
import re

from core.ai_gateway.ai_gateway import AIGateway

_SELECTION_HINT = "project-selection"


class StubGateway(AIGateway):
    """Answers prompts with template text derived from the prompt itself."""

    async def generate(self, prompt: str) -> str:
        if _SELECTION_HINT in prompt or "best_index" in prompt:
            return json.dumps({"best_index": 1, "valid": True, "reason": ""})
        return self._describe(prompt)

    @staticmethod
    def _describe(prompt: str) -> str:
        def field(name: str) -> str:
            match = re.search(rf"{name}\s*:\s*(.+)", prompt)
            return match.group(1).strip() if match else "your stack"

        language = field("Language")
        technology = field("Technology")
        addon = field("Addon")
        return (
            f"Build a {technology} project in {language}, using {addon} as a "
            f"supporting tool. You will practise designing the core domain, "
            f"wiring the pieces together and testing them end to end, which is "
            f"exactly the kind of work that turns a tutorial-level developer "
            f"into someone who can ship."
        )
