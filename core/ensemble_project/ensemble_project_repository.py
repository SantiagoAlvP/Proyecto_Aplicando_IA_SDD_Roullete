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
from core.ensemble_project.api.ensemble_project_models import Entity


class EnsembleProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def save_project(self, project: dict) -> dict:
        lang_id = get_or_create_id(
            self.session, ProgrammingLanguageCRUD, project["programming_language"]
        )
        tech_id = get_or_create_id(self.session, TechCRUD, project["technologies"])
        addon_id = get_or_create_id(self.session, AddonCRUD, project["addons"])

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
