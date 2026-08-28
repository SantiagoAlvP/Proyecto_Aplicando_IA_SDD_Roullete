"""Integration tests for GET /api/v1/projects/{project_id}.

Mirrors the scenarios in specs/006-get-project-by-id/quickstart.md end to
end through the real FastAPI app + router wiring (only the catalog service
and the current-user dependency are swapped for test doubles - no real DB
or auth backend is required to validate the HTTP contract).
"""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.monitoring.metrics import get_metrics_snapshot, reset_metrics
from core.projects.api.projects_router import get_catalog_service, router
from core.security.auth import User, get_optional_current_user


def make_project(
    *,
    id_: int = 1,
    is_public: bool = True,
    owner_id: int | None = None,
    description: str = "A project",
):
    project = MagicMock()
    project.id = id_
    project.is_public = is_public
    project.owner_id = owner_id
    project.description = description
    return project


@pytest.fixture(autouse=True)
def _reset_metrics():
    reset_metrics()
    yield
    reset_metrics()


@pytest.fixture
def app_factory():
    """Build a fresh app with overridable service/user dependencies."""

    def _build(*, project, current_user=None):
        service = MagicMock()
        service.get_project_by_id.return_value = project

        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        app.dependency_overrides[get_catalog_service] = lambda: service
        app.dependency_overrides[get_optional_current_user] = lambda: current_user
        return TestClient(app)

    return _build


class TestGetProjectById:
    def test_public_project_returns_200(self, app_factory):
        """Escenario A: proyecto público, sin autenticación -> 200."""
        project = make_project(id_=1, is_public=True)
        client = app_factory(project=project, current_user=None)

        response = client.get("/api/v1/projects/1")

        assert response.status_code == 200
        assert get_metrics_snapshot().get("projects.get_by_id.granted") == 1

    def test_missing_project_returns_404(self, app_factory):
        """Escenario B: proyecto inexistente -> 404."""
        client = app_factory(project=None, current_user=None)

        response = client.get("/api/v1/projects/999")

        assert response.status_code == 404
        assert get_metrics_snapshot().get("projects.get_by_id.not_found") == 1

    def test_private_project_without_auth_returns_401(self, app_factory):
        """Proyecto privado sin autenticación -> 401."""
        project = make_project(id_=2, is_public=False, owner_id=42)
        client = app_factory(project=project, current_user=None)

        response = client.get("/api/v1/projects/2")

        assert response.status_code == 401
        assert get_metrics_snapshot().get("projects.get_by_id.unauthorized") == 1

    def test_private_project_authenticated_without_permission_returns_403(
        self, app_factory
    ):
        """Escenario: autenticado pero sin permiso ni dueño -> 403."""
        project = make_project(id_=3, is_public=False, owner_id=42)
        other_user = User(user_id=99, name="Someone Else")
        client = app_factory(project=project, current_user=other_user)

        response = client.get("/api/v1/projects/3")

        assert response.status_code == 403
        assert get_metrics_snapshot().get("projects.get_by_id.forbidden") == 1

    def test_private_project_owner_returns_200(self, app_factory):
        """El dueño de un proyecto privado sí puede verlo -> 200."""
        project = make_project(id_=4, is_public=False, owner_id=42)
        owner = User(user_id=42, name="Owner")
        client = app_factory(project=project, current_user=owner)

        response = client.get("/api/v1/projects/4")

        assert response.status_code == 200
        assert get_metrics_snapshot().get("projects.get_by_id.granted") == 1

    def test_invalid_id_format_returns_422(self, app_factory):
        """Id con formato inválido (no entero).

        Nota: la spec original (contracts/project_contract.md) asumía IDs
        tipo UUID y un 400 para formato inválido. La implementación real usa
        IDs enteros autoincrementales (core/database/models.py), así que
        FastAPI valida el tipo de la ruta automáticamente y responde 422,
        no 400. Este test documenta el comportamiento real; ver el contrato
        actualizado para el detalle.
        """
        project = make_project(id_=1, is_public=True)
        client = app_factory(project=project, current_user=None)

        response = client.get("/api/v1/projects/not-an-id")

        assert response.status_code == 422
