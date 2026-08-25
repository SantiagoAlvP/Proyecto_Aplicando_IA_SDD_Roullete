"""Project-level AI orchestration on top of any :class:`AIGateway`.

Two responsibilities, deliberately kept apart from the provider itself:

1. decide which candidate stack is buildable and best for the level,
2. write the description a developer will actually read.

Both degrade gracefully: if the model is unreachable, rate limited or returns
something unparseable, the caller still gets a correct answer built from the
same data (Constitution, Principle V). The incident is logged, not swallowed.
"""

import json
import logging
import re

from core.ai_gateway.ai_gateway import AIGateway
from core.ai_gateway.stub_provider import StubGateway
from core.ensemble_project.api.ensemble_project_models import ProjectSelection
from core.settings.default import AppSettings

logger = logging.getLogger(__name__)

_SELECTOR_RULES = """You are a senior software architect evaluating candidate tech stacks for build FEASIBILITY, not conventionality.

A stack is VALID as long as it is technically possible to build the stated kind of project with those tools, even if the combination is unusual, hard, low-level or non-idiomatic. Novelty or difficulty is NOT a reason to reject a stack. Reject only on genuine technical impossibility, or when the "stack" is not a stack at all.

VALID examples (unusual but buildable):
- URL shortener in Prolog
- Bootloader in Rust
- Toy blockchain in Haskell

INVALID examples (not buildable / not a real stack):
- An operating system in pure Python (Python needs an OS underneath it)
- A full online shop in COBOL (no viable web tooling)
- "Prolog + CI/CD only" (there is nothing to build)

Answer with the project-selection tool: a single JSON object and nothing else.
"""


class AIProjectAdvisor:
    """Wraps an :class:`AIGateway` with the project-generation prompts."""

    def __init__(
        self,
        gateway: AIGateway,
        settings: AppSettings | None = None,
    ) -> None:
        self._gateway = gateway
        self._settings = settings or AppSettings()
        self._fallback = StubGateway()

    @property
    def _active_gateway(self) -> AIGateway:
        if self._settings.ai_generation_enabled:
            return self._gateway
        return self._fallback

    # ── selection ────────────────────────────────────────────────────────────
    async def choose_valid_project(self, projects: list[dict]) -> ProjectSelection:
        if not projects:
            return ProjectSelection(
                best_index=1,
                valid=False,
                reason="No candidate projects were supplied.",
            )

        listed = "\n".join(f"{i + 1}. {json.dumps(p)}" for i, p in enumerate(projects))
        prompt = (
            f"{_SELECTOR_RULES}\n"
            "Each candidate has programming_language, technologies, addons, "
            "level (1=Beginner..5=Expert) and extras.\n\n"
            f"Candidates:\n{listed}\n\n"
            "Reply with exactly this JSON shape and nothing else: "
            '{"best_index": <1-based integer>, "valid": <true|false>, '
            '"reason": "<why it is invalid, empty string when valid>"}'
        )

        try:
            raw = await self._active_gateway.generate(prompt)
            selection = self._parse_selection(raw, len(projects))
        except Exception:  # noqa: BLE001 - degraded mode is a product requirement
            logger.exception(
                "AI selection failed; accepting the first candidate (degraded mode)."
            )
            return ProjectSelection(best_index=1, valid=True, reason=None)

        if selection is None:
            logger.warning(
                "AI selection returned unparseable output; accepting the first "
                "candidate (degraded mode)."
            )
            return ProjectSelection(best_index=1, valid=True, reason=None)

        return selection

    @staticmethod
    def _parse_selection(raw: str, candidate_count: int) -> ProjectSelection | None:
        """Extract the JSON object from the model output.

        Models like to wrap JSON in prose or fences, so we take the first
        balanced object rather than trusting the whole string.
        """
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        try:
            payload = json.loads(match.group(0))
        except json.JSONDecodeError:
            return None
        if not isinstance(payload, dict):
            return None

        try:
            best_index = int(payload.get("best_index", 1))
        except (TypeError, ValueError):
            best_index = 1

        # An out-of-range index from the model must not become an IndexError
        # for the caller.
        if not 1 <= best_index <= candidate_count:
            logger.warning(
                "AI returned best_index=%s outside 1..%s; clamping to 1.",
                best_index,
                candidate_count,
            )
            best_index = 1

        reason = payload.get("reason") or None
        return ProjectSelection(
            best_index=best_index,
            valid=bool(payload.get("valid", True)),
            reason=str(reason) if reason else None,
        )

    # ── description ──────────────────────────────────────────────────────────
    async def generate_description(self, project: dict) -> str:
        prompt = (
            "Write a concise, motivating description (2-4 sentences, strictly "
            "under 400 characters) for a developer working on:\n"
            f"- Language  : {project.get('programming_language')}\n"
            f"- Technology: {project.get('technologies')}\n"
            f"- Addon     : {project.get('addons')}\n"
            f"- Level     : {project.get('level')} (1=Beginner, 5=Expert)\n"
            f"- Extras    : {project.get('extras', [])}\n\n"
            "Explain WHAT they will build and WHAT they will learn. "
            "Plain text only - no lists, no markdown, no preamble."
        )

        try:
            text = await self._active_gateway.generate(prompt)
        except Exception:  # noqa: BLE001 - degraded mode is a product requirement
            logger.exception("AI description failed; using the deterministic fallback.")
            text = await self._fallback.generate(prompt)

        text = text.strip()
        if not text:
            text = await self._fallback.generate(prompt)

        return text[: self._settings.MAX_DESCRIPTION_LENGTH].strip()
