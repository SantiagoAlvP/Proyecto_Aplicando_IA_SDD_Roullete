import random
from random import randint


from core.catalog.catalog_repository import CatalogRepository
from core.ensemble_project.api.ensemble_project_models import (
    GenerateProjectByValueRequest,
    Level,
    ProjectResponse,
    Extras,
    NamedCatalogEntry,
)
from core.ensemble_project.ensemble_project_repository import EnsembleProjectRepository
from core.ensemble_project.ensemble_project_ai_gatway_service import (
    ProjectGeneratorAIGateway,
)
from core.settings.default import AppSettings

from core.settings.clojure_settings import ClojureProjectGeneratorAIGateway


class ProjectGeneratorService:
    def __init__(
        self,
        ai_gateway: ClojureProjectGeneratorAIGateway | ProjectGeneratorAIGateway,
        catalog_repo: CatalogRepository,
        project_repo: EnsembleProjectRepository,
    ):
        self.ai_gateway = ai_gateway
        self.catalog_repo = catalog_repo
        self.project_repo = project_repo

    async def generate_by_value(
        self, payload: GenerateProjectByValueRequest
    ) -> ProjectResponse:
        programming_language = payload.programming_language
        if not programming_language or programming_language == "string":
            lang = self.catalog_repo.get_random_programming_language()
            if lang is None:
                raise ValueError(
                    "Catalog is empty: cannot pick a random programming language."
                )
            programming_language = lang.name

        technologies = payload.technologies
        if not technologies or technologies == "string":
            tech = self.catalog_repo.get_random_technology()
            if tech is None:
                raise ValueError("Catalog is empty: cannot pick a random technology.")
            technologies = tech.name

        addons = payload.addons
        if not addons or addons == "string":
            addon = self.catalog_repo.get_random_addon()
            if addon is None:
                raise ValueError("Catalog is empty: cannot pick a random addon.")
            addons = addon.name

        level = (
            payload.level.level if isinstance(payload.level, Level) else payload.level
        )
        if level is None:
            level = randint(1, 5)

        extra_count = level * 2
        filled_extras = [self._fill_extra(e) for e in (payload.extras or [])]

        if len(filled_extras) < extra_count:
            filled_extras += self._pick_random_extras(extra_count - len(filled_extras))
        elif len(filled_extras) > extra_count:
            filled_extras = filled_extras[:extra_count]

        project = {
            "programming_language": programming_language,
            "technologies": technologies,
            "addons": addons,
            "extras": [e.model_dump() for e in filled_extras],
            "level": level,
        }

        selection = await self.ai_gateway.choose_valid_project([project])
        if not selection.valid:
            raise ValueError(
                selection.reason or "The tech stack is incoherent or impractical."
            )

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

        selection = await self.ai_gateway.choose_valid_project(candidates)
        if not selection.valid:
            raise ValueError(selection.reason or "No coherent project could be built.")

        best = candidates[selection.best_index - 1]
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

    def _fill_extra(self, extra: Extras) -> Extras:
        lang_name = extra.programming_language
        if not lang_name or lang_name == "string":
            lang = self.catalog_repo.get_random_programming_language()
            lang_name = lang.name if lang else None

        tech_name = extra.technologies
        if not tech_name or tech_name == "string":
            tech = self.catalog_repo.get_random_technology()
            tech_name = tech.name if tech else None

        addon_name = extra.addons
        if not addon_name or addon_name == "string":
            addon = self.catalog_repo.get_random_addon()
            addon_name = addon.name if addon else None

        return Extras(
            programming_language=lang_name,
            technologies=tech_name,
            addons=addon_name,
        )
