from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.ensemble_project.api.ensemble_project_models import RegenerationResponse
from core.ensemble_project.api.ensemble_project_router import (
    get_project_service,
    router,
)
from core.ensemble_project.ensemble_project_service import ProjectNotFoundError


ENDPOINT = "/api/v1/ensemble_project/7/regenerate_description"


def response() -> RegenerationResponse:
    return RegenerationResponse(
        id=7,
        programming_language="Python",
        technologies="FastAPI",
        addons="PostgreSQL",
        extras=[],
        level=3,
        description="Build the API. Learn persistence patterns.",
    )


@pytest.fixture
def client_and_service():
    service = MagicMock()
    service.regenerate_description = AsyncMock()
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_project_service] = lambda: service
    with TestClient(app) as client:
        yield client, service


def test_regeneration_returns_updated_project(client_and_service) -> None:
    client, service = client_and_service
    service.regenerate_description.return_value = response()

    result = client.post(ENDPOINT)

    assert result.status_code == 200
    assert result.json() == response().model_dump()
    service.regenerate_description.assert_awaited_once_with(7)


@pytest.mark.parametrize("project_id", [0, -1, "abc"])
def test_invalid_project_id_is_rejected_without_service_call(
    client_and_service, project_id
) -> None:
    client, service = client_and_service

    result = client.post(
        f"/api/v1/ensemble_project/{project_id}/regenerate_description"
    )

    assert result.status_code == 422
    service.regenerate_description.assert_not_called()


def test_missing_project_returns_404(client_and_service) -> None:
    client, service = client_and_service
    service.regenerate_description.side_effect = ProjectNotFoundError(
        "Project not found."
    )

    result = client.post(ENDPOINT)

    assert result.status_code == 404
