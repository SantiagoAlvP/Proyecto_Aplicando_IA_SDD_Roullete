"""HU-20 / US1: contract of the public read-only project endpoint.

The endpoint hands a project to anyone holding the link, so its contract is
double: the happy shape AND absolute neutrality on failure (FR-008,
Constitution IV - no stack traces, no table names, no file paths).
"""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.ensemble_project.api.ensemble_project_models import (
    Extras,
    SharedProjectResponse,
)
from core.ensemble_project.api.ensemble_project_router import (
    get_project_service,
    router,
)

ENDPOINT = "/api/v1/ensemble_project/shared"

EXPECTED_SHAPE = {
    "share_token",
    "programming_language",
    "technologies",
    "addons",
    "extras",
    "level",
    "description",
}


def shared_project(token: str = "kX9m2LpQ_vR4wBn7") -> SharedProjectResponse:
    return SharedProjectResponse(
        share_token=token,
        programming_language="Python",
        technologies="FastAPI",
        addons="PostgreSQL",
        extras=[
            Extras(programming_language="SQL", technologies=None, addons=None),
        ],
        level=3,
        description="Build a REST API.",
    )


@pytest.fixture
def client_and_service():
    service = MagicMock()
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_project_service] = lambda: service
    with TestClient(app) as client:
        yield client, service


def test_returns_the_full_readonly_shape(client_and_service) -> None:
    client, service = client_and_service
    service.get_shared_project.return_value = shared_project()

    response = client.get(f"{ENDPOINT}/kX9m2LpQ_vR4wBn7")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == EXPECTED_SHAPE
    assert body["share_token"] == "kX9m2LpQ_vR4wBn7"
    assert body["level"] == 3
    assert body["description"] == "Build a REST API."
    service.get_shared_project.assert_called_once_with("kX9m2LpQ_vR4wBn7")


def test_unknown_but_well_formed_token_is_a_neutral_404(client_and_service) -> None:
    client, service = client_and_service
    from core.ensemble_project.ensemble_project_service import ProjectNotFoundError

    service.get_shared_project.side_effect = ProjectNotFoundError("db says no")

    response = client.get(f"{ENDPOINT}/wellformedtoken123")

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail == "Proyecto no disponible."
    # The internal reason must never reach the client.
    assert "db says no" not in detail


@pytest.mark.parametrize(
    "bad_token",
    ["short", "with spaces and way too many characters to be valid!!"],
)
def test_malformed_tokens_are_rejected_before_the_service(
    client_and_service, bad_token: str
) -> None:
    """Out-of-bounds tokens die at validation; the service is never called."""
    client, service = client_and_service

    response = client.get(f"{ENDPOINT}/{bad_token}")

    assert response.status_code == 422
    service.get_shared_project.assert_not_called()


def test_a_slash_can_never_smuggle_extra_segments(client_and_service) -> None:
    """Tokens are URL-safe by construction: `no/slashes` is another 404 path."""
    client, service = client_and_service

    response = client.get(f"{ENDPOINT}/no/slashes")

    assert response.status_code == 404
    service.get_shared_project.assert_not_called()


def test_error_responses_leak_no_internal_details(client_and_service) -> None:
    client, service = client_and_service
    from core.ensemble_project.ensemble_project_service import ProjectNotFoundError

    service.get_shared_project.side_effect = ProjectNotFoundError(
        "SELECT failed on projects table at /core/database/crud.py"
    )

    body = client.get(f"{ENDPOINT}/wellformedtoken123").json()

    serialized = str(body)
    for leak in ("projects", "crud.py", "SELECT", "/", "traceback"):
        assert leak not in serialized.replace("Proyecto no disponible.", "")
