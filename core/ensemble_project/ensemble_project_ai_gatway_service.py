import json
from strands import Agent
from strands.models.ollama import OllamaModel
from core.ensemble_project.api.ensemble_project_models import (
    BestIndex,
    ValidationResult,
)

from core.settings.default import AppSettings

settings = AppSettings()


class ProjectGeneratorAIGateway:
    def __init__(self):
        model = OllamaModel(
            host=settings.OLLAMA_HOST,
            model_id=settings.OLLAMA_MODEL,
        )

        self._validator_agent = Agent(
            model=model,
            system_prompt=(
                "You are a senior software architect. "
                "Evaluate whether a given tech stack is coherent and appropriate "
                "for the stated skill level. "
                "Respond ONLY via the validation tool – never add extra prose."
            ),
        )

        self._chooser_agent = Agent(
            model=model,
            system_prompt=(
                "You are a senior software architect. "
                "Choose the most coherent, practical, and learnable project "
                "from the provided candidates. "
                "Respond ONLY via the best-index tool – never add extra prose."
            ),
        )

        self._describer_agent = Agent(
            model=model,
            system_prompt=(
                "You are a software project mentor. "
                "Write concise, motivating project descriptions in plain text. "
                "No lists, no markdown, strictly under 400 characters."
            ),
        )

    async def validate_project(self, project: dict) -> tuple[bool, str]:
        prompt = (
            f"Evaluate this tech stack:\n"
            f"- Language  : {project.get('programming_language')}\n"
            f"- Technology: {project.get('technologies')}\n"
            f"- Addon     : {project.get('addons')}\n"
            f"- Level     : {project.get('level')} (1=Beginner, 5=Expert)\n"
            f"- Extras    : {project.get('extras', [])}\n\n"
            "VALID examples: Python+FastAPI+PostgreSQL (any level), "
            "Java+Spring Boot+Kafka (intermediate/advanced), Rust+Axum+PostgreSQL (advanced).\n"
            "INVALID examples: Prolog+CI/CD only (no real stack), "
            "COBOL+React Native (anachronistic), Level 1+Kubernetes+Kafka+CQRS (too complex)."
        )
        try:
            result = self._validator_agent(
                prompt,
                structured_output_model=ValidationResult,
            )
            data = result.structured_output
            if not isinstance(data, ValidationResult):
                return False, "Validation error: no structured output returned"
            return data.valid, data.reason
        except Exception as exc:
            return False, f"Validation error: {exc}"

    async def choose_best_project(self, projects: list[dict]) -> dict:
        listed = "\n".join(f"{i + 1}. {json.dumps(p)}" for i, p in enumerate(projects))
        prompt = (
            f"Choose the most coherent, practical, and learnable project "
            f"from the candidates below.\n\nCandidates:\n{listed}"
        )
        try:
            result = self._chooser_agent(
                prompt,
                structured_output_model=BestIndex,
            )
            data = result.structured_output
            if not isinstance(data, BestIndex):
                return projects[0]
            idx = data.best_index - 1  # convert to 0-based
            return projects[max(0, min(idx, len(projects) - 1))]
        except Exception:
            return projects[0]

    async def generate_description(self, project: dict) -> str:
        prompt = (
            f"Write a concise, motivating description (2-4 sentences, "
            f"strictly under 400 characters) for a developer working on:\n"
            f"- Language  : {project.get('programming_language')}\n"
            f"- Technology: {project.get('technologies')}\n"
            f"- Addon     : {project.get('addons')}\n"
            f"- Level     : {project.get('level')} (1=Beginner, 5=Expert)\n"
            f"- Extras    : {project.get('extras', [])}\n\n"
            "Explain WHAT they will build and WHAT they will learn. "
            "Plain text only – no lists, no markdown."
        )
        try:
            result = self._describer_agent(prompt)
            return str(result).strip()
        except Exception as exc:
            return f"Description unavailable: {exc}"
