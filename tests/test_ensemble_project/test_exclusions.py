from types import SimpleNamespace
from unittest.mock import MagicMock

from core.ensemble_project.ensemble_project_service import ProjectGeneratorService


def named(value: str) -> SimpleNamespace:
    return SimpleNamespace(name=value)


def make_service() -> ProjectGeneratorService:
    catalog = MagicMock()
    catalog.get_programming_languages.return_value = [named("Python"), named("Rust")]
    catalog.get_technologies.return_value = [named("FastAPI"), named("Docker")]
    catalog.get_addons.return_value = [named("Postman")]
    return ProjectGeneratorService(MagicMock(), catalog, MagicMock())


def test_normalize_excluded_keeps_only_known_languages_and_technologies() -> None:
    service = make_service()

    result = service._normalize_excluded(
        [" Rust ", "FASTAPI", "Rust", "Postman", "Unknown", ""]
    )

    assert result == {"rust", "fastapi"}


def test_random_extras_never_use_excluded_language_or_technology() -> None:
    service = make_service()

    extras = service._pick_random_extras(10, {"rust", "docker"})

    for extra in extras:
        assert extra.programming_language != "Rust"
        assert extra.technologies != "Docker"
        assert extra.addons in {None, "Postman"}
