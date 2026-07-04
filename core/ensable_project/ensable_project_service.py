import random
from random import randint


from core.catalog.catalog_repository import CatalogRepository
from core.ensable_project.api.ensable_project_models import (
    GenerateProjectByValueRequest,
    Level,
    ProjectResponse,
    Extras,
    NamedCatalogEntry,
)
from core.ensable_project.ensable_project_repository import EnsableProjectRepository
from core.ensable_project.ensable_project_ai_gatway_service import (
    ProjectGeneratorAIGateway,
)
from core.settings.default import AppSettings


class ProjectGeneratorService:
    def __init__(
        self,
        ai_gateway: ProjectGeneratorAIGateway,
        catalog_repo: CatalogRepository,
        project_repo: EnsableProjectRepository,
    ):
        self.ai_gateway = ai_gateway
        self.catalog_repo = catalog_repo
        self.project_repo = project_repo

    async def generate_by_value(
        self, payload: GenerateProjectByValueRequest
    ) -> ProjectResponse:
        project = {
            "programming_language": payload.programming_language,
            "technologies": payload.technologies,
            "addons": payload.addons,
            "extras": [e.model_dump() for e in payload.extras],
            "level": payload.level,
        }
        is_valid, reason = await self.ai_gateway.validate_project(project)
        if not is_valid:
            raise ValueError(reason or "The tech stack is incoherent or impractical.")
        project["description"] = await self.ai_gateway.generate_description(project)
        saved = self.project_repo.save_project(project)
        return ProjectResponse(**saved)

    async def generate_by_level(self, payload: Level) -> ProjectResponse:
        return await self._build_best_project(payload.level)

    async def generate_random(self) -> ProjectResponse:
        return await self._build_best_project(randint(1, 5))

    async def _build_best_project(self, level: int) -> ProjectResponse:
        settings = AppSettings()

        candidates = [
            {
                **self._pick_random_base(level),
                "extras": [e.model_dump() for e in self._pick_random_extras(level * 2)],
            }
            for _ in range(settings.CANDIDATES)
        ]

        best = await self.ai_gateway.choose_best_project(candidates)
        best["description"] = await self.ai_gateway.generate_description(best)
        saved = self.project_repo.save_project(best)
        return ProjectResponse(**saved)

    def _pick_random_base(self, level: int) -> dict:
        lang = self.catalog_repo.get_random_programming_language()
        tech = self.catalog_repo.get_random_technology()
        addon = self.catalog_repo.get_random_addon()
        if lang is None or tech is None or addon is None:
            raise ValueError("Catalog is empty: cannot pick a random project base.")
        return {
            "programming_language": lang.name,
            "technologies": tech.name,
            "addons": addon.name,
            "level": level,
        }

    def _pick_random_extras(self, times: int) -> list[Extras]:
        fields = ["programming_language", "techs", "addons"]
        result = []
        remaining = times
        while remaining > 0:
            n_fields = random.randint(1, min(len(fields), remaining))
            selected = random.sample(fields, k=n_fields)
            remaining -= n_fields

            lang_name = None
            if "programming_language" in selected:
                lang_name = NamedCatalogEntry.model_validate(
                    self.catalog_repo.get_random_programming_language()
                ).name

            tech_name = None
            if "techs" in selected:
                tech_name = NamedCatalogEntry.model_validate(
                    self.catalog_repo.get_random_technology()
                ).name

            addon_name = None
            if "addons" in selected:
                addon_name = NamedCatalogEntry.model_validate(
                    self.catalog_repo.get_random_addon()
                ).name

            result.append(
                Extras(
                    programming_language=lang_name,
                    technologies=tech_name,
                    addons=addon_name,
                )
            )
        return result
