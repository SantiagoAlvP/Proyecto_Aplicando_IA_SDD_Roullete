from typing import Optional

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
            level=project.get("level"),
        )
        saved_id = Entity.model_validate(saved).id
        project["id"] = saved_id
        project["favorite"] = False

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
        return [_to_history_entry(project) for project in projects]

    def list_favorites(self, limit: int) -> list[HistoryEntry]:
        """Only favorited projects, most recent first (spec 005, HU-11)."""
        projects = ProjectCRUD.get_favorites(self.session, limit)
        return [_to_history_entry(project) for project in projects]

    def set_favorite(self, project_id: int, value: bool) -> Optional[HistoryEntry]:
        """Mark or unmark a project as favorite. `None` if it does not exist."""
        project = ProjectCRUD.set_favorite(self.session, project_id, value)
        if project is None:
            return None
        return _to_history_entry(project)


def _to_history_entry(project: object) -> HistoryEntry:
    return HistoryEntry(
        id=getattr(project, "id", None) or 0,
        programming_language=_name_of(getattr(project, "programming_language", None)),
        technologies=_name_of(getattr(project, "tech", None)),
        addons=_name_of(getattr(project, "addon", None)),
        level=getattr(project, "level", None),
        extras=_extras_of(project),
        description=getattr(project, "description", None) or "",
        favorite=bool(getattr(project, "is_favorite", False)),
    )


def _name_of(entity: object) -> str:
    """A catalog row may be missing on legacy data; never return None."""
    name = getattr(entity, "name", None)
    return str(name) if name else "Unknown"


def _extra_name_of(entity: object) -> str | None:
    """Unlike the project's own catalog fields, an extra's sub-field is
    legitimately optional: `None` here means "not set", not "missing data".
    """
    name = getattr(entity, "name", None)
    return str(name) if name else None


def _extras_of(project: object) -> list[Extras]:
    """Read from the ORM relationship already loaded on `project.extras` -
    no additional query needed (spec 005, D-06)."""
    return [
        Extras(
            programming_language=_extra_name_of(
                getattr(extra, "programming_language", None)
            ),
            technologies=_extra_name_of(getattr(extra, "tech", None)),
            addons=_extra_name_of(getattr(extra, "addon", None)),
        )
        for extra in getattr(project, "extras", None) or []
    ]
