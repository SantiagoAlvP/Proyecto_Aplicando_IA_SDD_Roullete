from sqlmodel import Session
from core.ensemble_project.api.ensemble_project_models import Entity


def _resolve_id(session: Session, crud, name: str) -> int:
    entity = crud.get_by_name(session, name) or crud.create(session, name)
    return Entity.model_validate(entity).id


def optional_id(session: Session, crud, name: str | None) -> int | None:
    if not name:
        return None
    return _resolve_id(session, crud, name)


def get_or_create_id(session: Session, crud, name: str | None) -> int | None:
    if not name:
        return None
    return _resolve_id(session, crud, name)


def fill_or_random(value: str | None, getter, field_name: str) -> str:
    if value:
        return value
    entry = getter()
    if entry is None:
        raise ValueError(f"Catalog is empty: cannot pick a random {field_name}.")
    return entry.name
