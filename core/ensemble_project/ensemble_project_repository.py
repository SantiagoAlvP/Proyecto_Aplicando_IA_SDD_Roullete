from sqlmodel import Session
from core.database.crud import (
    AddonCRUD,
    ProgrammingLanguageCRUD,
    ProjectCRUD,
    ProjectExtraCRUD,
    TechCRUD,
)

from core.ensemble_project.api.ensemble_project_validation import (
    get_or_create_id,
    optional_id,
)
from core.ensemble_project.api.ensemble_project_models import (
    Entity,
    Extras,
    HistoryEntry,
    SharedProjectResponse,
)

# Legacy rows may predate AI descriptions; an empty hole would look broken on
# the public page (HU-20 edge case), so the shared view fills it with prose.
FALLBACK_DESCRIPTION = (
    "Este proyecto se generó antes de que la máquina escribiera "
    "descripciones automáticas."
)


class EnsembleProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_project(self, project: dict) -> dict:
        lang_id = get_or_create_id(
            self.session, ProgrammingLanguageCRUD, project["programming_language"]
        )
        tech_id = get_or_create_id(self.session, TechCRUD, project["technologies"])
        addon_id = get_or_create_id(self.session, AddonCRUD, project["addons"])
        if lang_id is None:
            raise ValueError("Failed to get or create programming_language id")
        saved = ProjectCRUD.create(
            session=self.session,
            programming_language_id=lang_id,
            description=project.get("description", "")[:500],
            project_tech_id=tech_id,
            project_addon_id=addon_id,
        )
        saved_id = Entity.model_validate(saved).id

        for extra in project.get("extras", []):
            extra_lang_name = (
                extra.get("programming_language") or project["programming_language"]
            )
            extra_lang_id = optional_id(
                self.session, ProgrammingLanguageCRUD, extra_lang_name
            )
            extra_tech_id = optional_id(
                self.session, TechCRUD, extra.get("technologies")
            )
            extra_addon_id = optional_id(self.session, AddonCRUD, extra.get("addons"))

            ProjectExtraCRUD.create(
                session=self.session,
                projects_id=saved_id,
                project_programming_language_id=extra_lang_id,
                project_tech_id=extra_tech_id,
                project_addon_id=extra_addon_id,
            )

        # The response must carry the persisted public identity (HU-20): the
        # UI offers "Compartir" on the fresh result without a second request.
        return {
            **project,
            "share_token": saved.share_token,
            "level": saved.level if saved.level is not None else project.get("level"),
        }

    def list_recent(self, limit: int) -> list[HistoryEntry]:
        """Return the latest projects as DTOs, never as ORM entities.

        Keeping SQLModel objects inside this layer is what allows the service
        and the router to be tested without a database.
        """
        projects = ProjectCRUD.get_recent(self.session, limit)
        entries: list[HistoryEntry] = []
        for project in projects:
            entries.append(
                HistoryEntry(
                    id=project.id or 0,
                    share_token=project.share_token,
                    programming_language=_name_of(project.programming_language),
                    technologies=_name_of(project.tech),
                    addons=_name_of(project.addon),
                    description=project.description or "",
                    level=project.level,
                )
            )
        return entries

    def get_by_share_token(self, share_token: str) -> SharedProjectResponse | None:
        """Full read-only view for a share link, or None if it dangles (HU-20)."""
        project = ProjectCRUD.get_by_share_token(self.session, share_token)
        if project is None:
            return None

        extras = [
            Extras(
                programming_language=_optional_name_of(extra.programming_language),
                technologies=_optional_name_of(extra.tech),
                addons=_optional_name_of(extra.addon),
            )
            for extra in ProjectExtraCRUD.get_by_project(self.session, project.id or 0)
        ]
        return SharedProjectResponse(
            share_token=project.share_token,
            programming_language=_name_of(project.programming_language),
            technologies=_name_of(project.tech),
            addons=_name_of(project.addon),
            extras=extras,
            level=project.level,
            description=project.description or FALLBACK_DESCRIPTION,
        )


def _name_of(entity: object) -> str:
    """A catalog row may be missing on legacy data; never return None."""
    name = getattr(entity, "name", None)
    return str(name) if name else "Unknown"


def _optional_name_of(entity: object) -> str | None:
    """Extras are optional per field: an absent relation stays null."""
    name = getattr(entity, "name", None)
    return str(name) if name else None
