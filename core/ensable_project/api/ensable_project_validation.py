from sqlmodel import Session
from core.ensable_project.api.ensable_project_models import Entity


def _resolve_id(session: Session, crud, name: str) -> int:
    entity = crud.get_by_name(session, name) or crud.create(session, name)
    return Entity.model_validate(entity).id


def optional_id(session: Session, crud, name: str | None) -> int | None:
    if not name:
        return None
    return _resolve_id(session, crud, name)


def get_or_create_id(session, crud, name):
    if not name:
        return None
    return _resolve_id(session, crud, name)
