from sqlmodel import Session
import yaml

from core.database.crud import (
    ProgrammingLanguageCRUD,
    TechCRUD,
    AddonCRUD,
)


def seed_from_yaml(session: Session, yaml_path: str) -> dict[str, list[str]]:
    with open(yaml_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    inserted: dict[str, list[str]] = {
        "programming_languages": [],
        "techs": [],
        "addons": [],
    }

    for name in data.get("programming_languages", []):
        if name is None:
            continue
        name = str(name).strip()
        if not ProgrammingLanguageCRUD.get_by_name(session, name):
            ProgrammingLanguageCRUD.create(session, name)
            inserted["programming_languages"].append(name)

    for name in data.get("techs", []):
        if name is None:
            continue
        name = str(name).strip()
        if not TechCRUD.get_by_name(session, name):
            TechCRUD.create(session, name)
            inserted["techs"].append(name)

    for name in data.get("addons", []):
        if name is None:
            continue
        name = str(name).strip()
        if not AddonCRUD.get_by_name(session, name):
            AddonCRUD.create(session, name)
            inserted["addons"].append(name)

    return inserted
