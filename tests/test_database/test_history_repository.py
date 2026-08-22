"""HU-08: the repository hands out DTOs, never ORM entities."""

from unittest.mock import MagicMock

from core.ensemble_project.api.ensemble_project_models import HistoryEntry
from core.ensemble_project.ensemble_project_repository import EnsembleProjectRepository


def fake_project(
    project_id: int,
    *,
    language="Rust",
    description="A project.",
    level=3,
    extras=None,
    is_favorite=False,
):
    project = MagicMock()
    project.id = project_id
    project.description = description
    project.level = level
    project.extras = extras if extras is not None else []
    project.is_favorite = is_favorite
    project.programming_language.name = language
    project.tech.name = "Distributed Cache"
    project.addon.name = "Docker"
    return project


def fake_extra(*, language=None, tech=None, addon=None):
    extra = MagicMock()
    extra.programming_language = _named(language)
    extra.tech = _named(tech)
    extra.addon = _named(addon)
    return extra


def _named(name):
    if name is None:
        return None
    entity = MagicMock()
    entity.name = name
    return entity


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
    assert entry.level == 3
    assert entry.favorite is False


def test_a_missing_level_becomes_none_not_zero() -> None:
    """Legacy rows generated before spec 005 never persisted a level."""
    entry = repo_with([fake_project(1, level=None)]).list_recent(10)[0]
    assert entry.level is None


def test_favorite_reflects_is_favorite() -> None:
    entry = repo_with([fake_project(1, is_favorite=True)]).list_recent(10)[0]
    assert entry.favorite is True


def test_extras_are_read_from_the_orm_relationship_without_a_new_query() -> None:
    extras = [fake_extra(tech="Tokio"), fake_extra(language="Zig", addon="Docker")]
    entry = repo_with([fake_project(1, extras=extras)]).list_recent(10)[0]

    assert len(entry.extras) == 2
    assert entry.extras[0].technologies == "Tokio"
    assert entry.extras[0].programming_language is None
    assert entry.extras[1].programming_language == "Zig"
    assert entry.extras[1].addons == "Docker"


def test_no_extras_yields_an_empty_list_not_none() -> None:
    entry = repo_with([fake_project(1, extras=[])]).list_recent(10)[0]
    assert entry.extras == []


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


# --- list_favorites (spec 005, HU-12) -----------------------------------


def test_list_favorites_returns_dtos() -> None:
    entries = repo_with([fake_project(1, is_favorite=True)]).list_favorites(10)
    assert all(isinstance(e, HistoryEntry) for e in entries)
    assert entries[0].favorite is True


def test_list_favorites_empty_is_not_an_error() -> None:
    assert repo_with([]).list_favorites(10) == []


# --- set_favorite (spec 005, HU-11/HU-13) -------------------------------


def session_with(project) -> MagicMock:
    session = MagicMock()
    session.get.return_value = project
    return session


def test_set_favorite_true_marks_an_existing_project() -> None:
    project = fake_project(1, is_favorite=False)
    repo = EnsembleProjectRepository(session_with(project))

    entry = repo.set_favorite(1, True)

    assert entry is not None
    assert entry.favorite is True
    assert project.is_favorite is True


def test_set_favorite_false_unmarks_an_existing_project() -> None:
    project = fake_project(1, is_favorite=True)
    repo = EnsembleProjectRepository(session_with(project))

    entry = repo.set_favorite(1, False)

    assert entry is not None
    assert entry.favorite is False


def test_set_favorite_on_a_missing_project_returns_none() -> None:
    repo = EnsembleProjectRepository(session_with(None))

    assert repo.set_favorite(999, True) is None
