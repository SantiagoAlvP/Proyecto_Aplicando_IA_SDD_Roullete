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
from core.ensemble_project.api.ensemble_project_models import Entity, HistoryEntry


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

        return project

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
                    programming_language=_name_of(project.programming_language),
                    technologies=_name_of(project.tech),
                    addons=_name_of(project.addon),
                    description=project.description or "",
                )
            )
        return entries


def _name_of(entity: object) -> str:
    """A catalog row may be missing on legacy data; never return None."""
    name = getattr(entity, "name", None)
    return str(name) if name else "Unknown"
