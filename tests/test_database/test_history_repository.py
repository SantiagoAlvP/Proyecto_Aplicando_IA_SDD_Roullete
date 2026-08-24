"""HU-08: the repository hands out DTOs, never ORM entities."""

from unittest.mock import MagicMock

from core.ensemble_project.api.ensemble_project_models import HistoryEntry
from core.ensemble_project.ensemble_project_repository import EnsembleProjectRepository


def fake_project(project_id: int, *, language="Rust", description="A project."):
    project = MagicMock()
    project.id = project_id
    project.description = description
    project.share_token = f"tok{project_id}en-share"
    project.level = 3 if project_id % 2 == 0 else None
    project.programming_language.name = language
    project.tech.name = "Distributed Cache"
    project.addon.name = "Docker"
    return project


def repo_with(projects) -> EnsembleProjectRepository:
    session = MagicMock()
    session.exec.return_value.all.return_value = projects
    return EnsembleProjectRepository(session)


def test_returns_dtos_not_orm_objects() -> None:
    entries = repo_with([fake_project(1)]).list_recent(10)
    assert all(isinstance(e, HistoryEntry) for e in entries)


def test_maps_every_field() -> None:
    entry = repo_with([fake_project(7, language="Zig")]).list_recent(10)[0]
    assert entry.id == 7
    assert entry.programming_language == "Zig"
    assert entry.technologies == "Distributed Cache"
    assert entry.addons == "Docker"


def test_a_missing_description_becomes_empty_text_not_none() -> None:
    entry = repo_with([fake_project(1, description=None)]).list_recent(10)[0]
    assert entry.description == ""


def test_a_missing_catalog_relation_does_not_crash() -> None:
    """Legacy rows can point at a language that no longer resolves."""
    project = fake_project(1)
    project.programming_language = None
    entry = repo_with([project]).list_recent(10)[0]
    assert entry.programming_language == "Unknown"


def test_no_projects_yields_an_empty_list() -> None:
    assert repo_with([]).list_recent(10) == []
