import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from core.catalog.catalog_repository import CatalogRepository
from core.catalog.catalog_router import get_catalog_service, router
from core.catalog.catalog_service import CatalogService, DefaultCatalogService


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
