import logging
import random
import re
from random import randint
from typing import Protocol

from core.catalog.catalog_repository import CatalogRepository
from core.ensemble_project.api.ensemble_project_models import (
    Extras,
    GenerateProjectByValueRequest,
    HistoryEntry,
    Level,
    NamedCatalogEntry,
    ProjectResponse,
    ProjectSelection,
    RegenerationResponse,
)
from core.ensemble_project.ensemble_project_repository import EnsembleProjectRepository
from core.settings.default import AppSettings

logger = logging.getLogger(__name__)


class ProjectNotFoundError(ValueError):
    pass


class ProjectAIAdvisor(Protocol):
    """What this service needs from an AI collaborator - nothing more.

    Depending on a Protocol rather than on a concrete gateway is what keeps the
    Groq, Ollama, Clojure and stub implementations interchangeable, and what
    lets every test here run with a plain double (Constitution, Principle II).
    """

    async def choose_valid_project(self, projects: list[dict]) -> ProjectSelection: ...

    async def generate_description(self, project: dict) -> str: ...


class CatalogItem(Protocol):
    name: str


class ProjectGeneratorService:
    def __init__(
        self,
        ai_gateway: ProjectAIAdvisor,
        catalog_repo: CatalogRepository,
        project_repo: EnsembleProjectRepository,
    ):
        self.ai_gateway = ai_gateway
        self.catalog_repo = catalog_repo
        self.project_repo = project_repo

    def get_history(self, limit: int) -> list[HistoryEntry]:
        """Latest generated projects, most recent first (spec 002, HU-08)."""
        return self.project_repo.list_recent(limit)

    async def regenerate_description(self, project_id: int) -> RegenerationResponse:
        project = self.project_repo.get_project_for_regeneration(project_id)
        if project is None:
            raise ProjectNotFoundError("Project not found.")

        previous = str(project.get("description", "")).strip()
        try:
            generated = await self.ai_gateway.generate_description(project)
        except Exception:  # noqa: BLE001 - degraded mode is a product requirement
            logger.exception("AI regeneration failed; using deterministic fallback.")
            generated = self._fallback_description(project, previous)

        description = self._valid_alternative(generated, previous)
        if description is None:
            return RegenerationResponse(**project)

        updated = self.project_repo.update_description(project_id, description)
        return RegenerationResponse(**updated)

    @staticmethod
    def _valid_alternative(text: str, previous: str) -> str | None:
        candidate = str(text or "").strip()
        if not candidate or len(candidate) >= 400 or candidate == previous:
            return None
        if "\n- " in candidate or "```" in candidate:
            return None
        sentences = re.findall(r"[^.!?]+[.!?](?=\s|$)", candidate)
        if not 2 <= len(sentences) <= 4:
            return None
        return candidate

    @staticmethod
    def _fallback_description(project: dict, previous: str) -> str:
        candidate = (
            f"Construye un proyecto con {project.get('programming_language')}, "
            f"{project.get('technologies')} y {project.get('addons')}. "
            "Aprende a integrar sus piezas en una solución funcional."
        )
        if candidate == previous:
            candidate = candidate.replace(
                "solución funcional.", "una solución mantenible."
            )
        return candidate[:399]

    def get_favorites(self, limit: int) -> list[HistoryEntry]:
        """Only favorited projects, most recent first (spec 005, HU-11)."""
        return self.project_repo.list_favorites(limit)

    def mark_favorite(self, project_id: int) -> HistoryEntry:
        """Mark a project as favorite. Idempotent (spec 005, FR-005)."""
        entry = self.project_repo.set_favorite(project_id, True)
        if entry is None:
            raise LookupError(f"Project {project_id} not found.")
        return entry

    def unmark_favorite(self, project_id: int) -> HistoryEntry:
        """Unmark a project as favorite. Idempotent (spec 005, FR-006)."""
        entry = self.project_repo.set_favorite(project_id, False)
        if entry is None:
            raise LookupError(f"Project {project_id} not found.")
        return entry

    async def generate_by_value(
        self, payload: GenerateProjectByValueRequest
    ) -> ProjectResponse:
        excluded = self._normalize_excluded(payload.excluded)
        programming_language = payload.programming_language
        if not programming_language or programming_language == "string":
            lang = self._pick_random_programming_language(excluded)
            if lang is None:
                raise ValueError(
                    "Catalog is empty: cannot pick a random programming language."
                )
            programming_language = lang.name
        elif self._is_excluded(programming_language, excluded):
            lang = self._pick_random_programming_language(excluded)
            if lang is None:
                raise ValueError("No programming languages remain after exclusions.")
            programming_language = lang.name

        technologies = payload.technologies
        if not technologies or technologies == "string":
            tech = self._pick_random_technology(excluded)
            if tech is None:
                raise ValueError("Catalog is empty: cannot pick a random technology.")
            technologies = tech.name
        elif self._is_excluded(technologies, excluded):
            tech = self._pick_random_technology(excluded)
            if tech is None:
                raise ValueError("No technologies remain after exclusions.")
            technologies = tech.name

        addons = payload.addons
        if not addons or addons == "string":
            addon = self._pick_random_addon()
            if addon is None:
                raise ValueError("Catalog is empty: cannot pick a random addon.")
            addons = addon.name
        level = (
            payload.level.level if isinstance(payload.level, Level) else payload.level
        )
        if level is None:
            level = randint(1, 5)

        extra_count = level * 2
        filled_extras = [self._fill_extra(e, excluded) for e in (payload.extras or [])]

        if len(filled_extras) < extra_count:
            filled_extras += self._pick_random_extras(
                extra_count - len(filled_extras), excluded
            )
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
        excluded = self._normalize_excluded(getattr(payload, "excluded", []))
        return await self._build_best_project(payload.level, excluded)

    async def generate_random(self) -> ProjectResponse:
        return await self._build_best_project(randint(1, 5), set())

    async def _build_best_project(
        self, level: int, excluded: set[str] | None = None
    ) -> ProjectResponse:
        settings = AppSettings()
        excluded = excluded or set()

        candidates = [
            {
                **self._pick_random_base(level, excluded),
                "extras": [
                    e.model_dump()
                    for e in self._pick_random_extras(level * 2, excluded)
                ],
            }
            for _ in range(settings.CANDIDATES)
        ]

        selection = await self.ai_gateway.choose_valid_project(candidates)
        if not selection.valid:
            raise ValueError(selection.reason or "No coherent project could be built.")

        index = selection.best_index - 1
        if not 0 <= index < len(candidates):
            # A model can return anything; an IndexError here would surface as
            # a 500 for the user (spec 001, Edge Cases).
            index = 0
        best = candidates[index]
        best["description"] = await self.ai_gateway.generate_description(best)
        saved = self.project_repo.save_project(best)
        return ProjectResponse(**saved)

    def _pick_random_base(self, level: int, excluded: set[str] | None = None) -> dict:
        excluded = excluded or set()
        lang = self._pick_random_programming_language(excluded)
        tech = self._pick_random_technology(excluded)
        addon = self._pick_random_addon()
        if lang is None or tech is None or addon is None:
            raise ValueError("No eligible catalog values remain after exclusions.")
        return {
            "programming_language": lang.name,
            "technologies": tech.name,
            "addons": addon.name,
            "level": level,
        }

    def _pick_random_programming_language(
        self, excluded: set[str] | None = None
    ) -> CatalogItem | None:
        excluded = excluded or set()
        values = self.catalog_repo.get_programming_languages()
        if isinstance(values, list):
            allowed = [
                item
                for item in values
                if item is not None
                and str(getattr(item, "name", "")).strip().lower() not in excluded
            ]
            if allowed:
                return random.choice(allowed)

        fallback = self.catalog_repo.get_random_programming_language()
        if (
            fallback is not None
            and str(getattr(fallback, "name", "")).strip().lower() not in excluded
        ):
            return fallback
        return None

    def _pick_random_technology(
        self, excluded: set[str] | None = None
    ) -> CatalogItem | None:
        excluded = excluded or set()
        values = self.catalog_repo.get_technologies()
        if isinstance(values, list):
            allowed = [
                item
                for item in values
                if item is not None
                and str(getattr(item, "name", "")).strip().lower() not in excluded
            ]
            if allowed:
                return random.choice(allowed)

        fallback = self.catalog_repo.get_random_technology()
        if (
            fallback is not None
            and str(getattr(fallback, "name", "")).strip().lower() not in excluded
        ):
            return fallback
        return None

    def _pick_random_addon(self) -> CatalogItem | None:
        values = self.catalog_repo.get_addons()
        if isinstance(values, list):
            return random.choice(values) if values else None
        return self.catalog_repo.get_random_addon()

    def _pick_random_extras(
        self, times: int, excluded: set[str] | None = None
    ) -> list[Extras]:
        excluded = excluded or set()
        fields = ["programming_language", "techs", "addons"]
        result = []
        remaining = times
        while remaining > 0:
            n_fields = random.randint(1, min(len(fields), remaining))
            selected = random.sample(fields, k=n_fields)
            remaining -= n_fields

            lang_name = None
            if "programming_language" in selected:
                lang = self._pick_random_programming_language(excluded)
                if lang is not None:
                    lang_name = NamedCatalogEntry.model_validate(lang).name

            tech_name = None
            if "techs" in selected:
                tech = self._pick_random_technology(excluded)
                if tech is not None:
                    tech_name = NamedCatalogEntry.model_validate(tech).name

            addon_name = None
            if "addons" in selected:
                addon = self._pick_random_addon()
                if addon is not None:
                    addon_name = NamedCatalogEntry.model_validate(addon).name

            result.append(
                Extras(
                    programming_language=lang_name,
                    technologies=tech_name,
                    addons=addon_name,
                )
            )
        return result

    def _fill_extra(self, extra: Extras, excluded: set[str] | None = None) -> Extras:
        excluded = excluded or set()
        lang_name = extra.programming_language
        if not lang_name or lang_name == "string":
            lang = self._pick_random_programming_language(excluded)
            lang_name = lang.name if lang else None
        elif self._is_excluded(lang_name, excluded):
            lang = self._pick_random_programming_language(excluded)
            lang_name = lang.name if lang else None

        tech_name = extra.technologies
        if not tech_name or tech_name == "string":
            tech = self._pick_random_technology(excluded)
            tech_name = tech.name if tech else None
        elif self._is_excluded(tech_name, excluded):
            tech = self._pick_random_technology(excluded)
            tech_name = tech.name if tech else None

        addon_name = extra.addons
        if not addon_name or addon_name == "string":
            addon = self._pick_random_addon()
            addon_name = addon.name if addon else None

        return Extras(
            programming_language=lang_name,
            technologies=tech_name,
            addons=addon_name,
        )

    def _normalize_excluded(self, values: list[str] | None) -> set[str]:
        if not values:
            return set()
        known = {
            str(getattr(item, "name", "")).strip().lower()
            for items in (
                self.catalog_repo.get_programming_languages(),
                self.catalog_repo.get_technologies(),
            )
            for item in items
            if item is not None
        }
        return {
            str(value).strip().lower()
            for value in values
            if isinstance(value, str) and str(value).strip().lower() in known
        }

    @staticmethod
    def _is_excluded(value: str | None, excluded: set[str]) -> bool:
        return bool(value) and str(value).strip().lower() in excluded
