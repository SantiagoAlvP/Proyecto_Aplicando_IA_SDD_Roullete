import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from core.catalog.catalog_repository import CatalogRepository
from core.catalog.api.catalog_router import get_catalog_service, router
from core.catalog.catalog_service import CatalogService, DefaultCatalogService

SAVED_PROJECT = {
    "programming_language": "Python",
    "technologies": "FastAPI",
    "addons": "PostgreSQL",
    "extras": [],
    "level": 3,
    "description": "Build a REST API with FastAPI and PostgreSQL.",
}

MOCK_DESCRIPTION = "Build a REST API with FastAPI and PostgreSQL."


@pytest.fixture
def session():
    mock = MagicMock()
    mock.exec.return_value.first.return_value = None
    mock.exec.return_value.all.return_value = []
    return mock


@pytest.fixture
def mock_cursor():
    return MagicMock()


@pytest.fixture
def yaml_file(tmp_path):
    content = """
programming_languages:
  - Python
  - Rust
  - C++
techs:
  - Git
  - Docker
  - Kubernetes
addons:
  - VSCode
  - Sublime Text
  - Postman
"""
    path = tmp_path / "skills.yaml"
    path.write_text(content)
    return str(path)


@pytest.fixture
def empty_yaml_file(tmp_path):
    content = """
programming_languages: []
techs: []
addons: []
"""
    path = tmp_path / "empty_skills.yaml"
    path.write_text(content)
    return str(path)


@pytest.fixture
def LANGUAGES():
    return [{"id": 1, "name": "Python"}, {"id": 2, "name": "Rust"}]


@pytest.fixture
def TECHS():
    return [{"id": 1, "name": "Docker"}, {"id": 2, "name": "Kubernetes"}]


@pytest.fixture
def ADDONS():
    return [{"id": 1, "name": "VSCode"}, {"id": 2, "name": "Postman"}]


@pytest.fixture
def mock_service():
    return MagicMock(spec=CatalogService)


@pytest.fixture
def client(mock_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_catalog_service] = lambda: mock_service
    return TestClient(app)


@pytest.fixture
def mock_repo():
    return MagicMock(spec=CatalogRepository)


@pytest.fixture
def service(mock_repo):
    return DefaultCatalogService(repo=mock_repo)


def make_catalog_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_random_programming_language.return_value = MagicMock(name_attr="Python")
    repo.get_random_programming_language.return_value.name = "Python"
    repo.get_random_technology.return_value = MagicMock()
    repo.get_random_technology.return_value.name = "FastAPI"
    repo.get_random_addon.return_value = MagicMock()
    repo.get_random_addon.return_value.name = "PostgreSQL"
    return repo


def make_project_repo(saved: dict | None = None) -> MagicMock:
    repo = MagicMock()
    repo.save_project.return_value = saved or SAVED_PROJECT
    return repo


# ── AI gateway stub ──────────────────────────────────────────────────────────


def make_ai_gateway(
    *,
    valid: bool = True,
    reason: str = "",
    best_index: int = 0,
    description: str = MOCK_DESCRIPTION,
) -> MagicMock:
    gw = MagicMock()
    gw.validate_project = AsyncMock(return_value=(valid, reason))
    gw.choose_best_project = AsyncMock(
        side_effect=lambda projects: projects[best_index]
    )
    gw.generate_description = AsyncMock(return_value=description)
    return gw


@pytest.fixture()
def client_with_mocks(tmp_path):
    from fastapi import FastAPI

    from core.ensemble_project.api.ensemble_project_router import (
        router,
        get_project_service,
    )
    from core.ensemble_project.ensemble_project_service import ProjectGeneratorService

    ai_gw = make_ai_gateway()
    catalog = make_catalog_repo()
    project_repo = make_project_repo()

    def override_service():
        return ProjectGeneratorService(ai_gw, catalog, project_repo)

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_project_service] = override_service

    with TestClient(app) as c:
        yield c, ai_gw, catalog, project_repo
