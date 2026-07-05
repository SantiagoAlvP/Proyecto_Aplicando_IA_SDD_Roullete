import json
from strands import Agent
from strands.models.ollama import OllamaModel
from core.ensemble_project.api.ensemble_project_models import ProjectSelection

from core.settings.default import AppSettings

settings = AppSettings()


class ProjectGeneratorAIGateway:
    def __init__(self):
        model = OllamaModel(
            host=settings.OLLAMA_HOST,
            model_id=settings.OLLAMA_MODEL,
        )

        self._selector_agent = Agent(
            model=model,
            system_prompt=(
                "You are a senior software architect evaluating candidate tech stacks "
                "for build FEASIBILITY, not conventionality. "
                "A stack is VALID as long as it is technically possible to build the "
                "stated kind of project with those tools — even if the combination is "
                "unusual, hard, low-level, or non-idiomatic for that language. "
                "Novelty, difficulty, or an unconventional pairing is NOT a reason to "
                "reject a stack. Only reject a stack if there is a genuine technical "
                "impossibility or a total mismatch between the tools and the goal "
                "(e.g. the language/runtime fundamentally cannot do the required job, "
                "or the 'stack' isn't a stack at all — just an unrelated tool with no "
                "way to build the actual project). "
                "Among the valid candidates, pick the single best one for its stated "
                "skill level. "
                "Respond ONLY via the project-selection tool – never add extra prose."
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

    async def choose_valid_project(self, projects: list[dict]) -> ProjectSelection:
        listed = "\n".join(f"{i + 1}. {json.dumps(p)}" for i, p in enumerate(projects))
        prompt = (
            "Evaluate the candidate tech stacks below. Each entry includes "
            "programming_language, technologies, addons, level (1=Beginner..5=Expert) "
            "and extras.\n\n"
            "Judge VALIDITY purely on feasibility: can this project actually be built "
            "with these tools, in principle? Unusual, advanced, or creative combos "
            "are still VALID as long as they're possible.\n\n"
            "VALID examples (unusual but buildable):\n"
            "- URL shortener in Prolog (just needs logic + persistence, doable)\n"
            "- Bootloader in Rust (real, common systems-programming use case)\n"
            "- Blockchain toy implementation in Haskell (pure logic, no blocker)\n"
            "- Python+PostgreSQL web app (any level)\n"
            "- Java+Spring Boot service (intermediate/advanced)\n"
            "- Rust+Axum+PostgreSQL API (advanced)\n\n"
            "INVALID examples (genuinely not buildable / not a real stack):\n"
            "- Operating system in pure Python (no runtime-free execution; Python "
            "needs an interpreter/OS underneath it, can't be the OS itself)\n"
            "- Full online shop in COBOL (no viable HTTP/web/e-commerce tooling exists)\n"
            "- Prolog + CI/CD only (CI/CD isn't a project target, there's nothing to build)\n"
            "- COBOL + React Native (no interop path between them for one project)\n\n"
            f"Candidates:\n{listed}\n\n"
            "Pick the best_index (1-based) among the FEASIBLE candidates. "
            "If none are feasible, set valid to false and explain why in reason "
            "(reason is required whenever valid is false)."
        )
        result = self._selector_agent(prompt, structured_output_model=ProjectSelection)
        output = result.structured_output
        if not isinstance(output, ProjectSelection):
            raise ValueError(
                "Selector agent did not return a valid ProjectSelection structured output"
            )
        return output

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
        result = self._describer_agent(prompt)
        return str(result).strip()
