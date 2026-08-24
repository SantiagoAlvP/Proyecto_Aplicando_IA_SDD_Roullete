"""HU-08: history endpoint contract."""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.ensemble_project.api.ensemble_project_models import HistoryEntry
from core.ensemble_project.api.ensemble_project_router import (
    get_project_service,
    router,
)

ENDPOINT = "/api/v1/ensemble_project/history"


def entry(entry_id: int) -> HistoryEntry:
    return HistoryEntry(
        id=entry_id,
        share_token=f"token{entry_id}abcde",
        programming_language="Rust",
        technologies="Distributed Cache",
        addons="Docker",
        description=f"Project number {entry_id}.",
        level=3 if entry_id % 2 == 0 else None,
    )


@pytest.fixture
def client_and_service():
    service = MagicMock()
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_project_service] = lambda: service
    with TestClient(app) as client:
        yield client, service


def test_returns_the_most_recent_projects(client_and_service) -> None:
    client, service = client_and_service
    service.get_history.return_value = [entry(3), entry(2), entry(1)]

    response = client.get(ENDPOINT)

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [3, 2, 1]


def test_default_limit_is_ten(client_and_service) -> None:
    client, service = client_and_service
    service.get_history.return_value = []

    client.get(ENDPOINT)

    service.get_history.assert_called_once_with(10)


def test_limit_is_passed_through(client_and_service) -> None:
    client, service = client_and_service
    service.get_history.return_value = []

    client.get(ENDPOINT, params={"limit": 25})

    service.get_history.assert_called_once_with(25)


@pytest.mark.parametrize("limit", [0, -1, 51, 1000])
def test_out_of_range_limits_are_rejected(client_and_service, limit: int) -> None:
    """An unbounded SELECT is a denial-of-service waiting to happen."""
    client, _ = client_and_service
    assert client.get(ENDPOINT, params={"limit": limit}).status_code == 422


def test_no_projects_yields_an_empty_list_not_a_404(client_and_service) -> None:
    client, service = client_and_service
    service.get_history.return_value = []

    response = client.get(ENDPOINT)

    assert response.status_code == 200
    assert response.json() == []


def test_entries_expose_the_expected_shape(client_and_service) -> None:
    client, service = client_and_service
    service.get_history.return_value = [entry(1)]

    body = client.get(ENDPOINT).json()[0]

    assert set(body) == {
        "id",
        "share_token",
        "programming_language",
        "technologies",
        "addons",
        "description",
        "level",
    }


def test_every_entry_carries_its_share_link_identity(client_and_service) -> None:
    """HU-20: the history is a sharing surface, not just a list."""
    client, service = client_and_service
    service.get_history.return_value = [entry(2), entry(1)]

    body = client.get(ENDPOINT).json()

    assert [item["share_token"] for item in body] == [
        "token2abcde",
        "token1abcde",
    ]
    # Legacy rows never persisted a level; it must read as null, not 0.
    assert [item["level"] for item in body] == [3, None]


def test_generated_responses_carry_the_token_too(client_with_mocks) -> None:
    """HU-20: 'Compartir' over a fresh result needs its token right away."""
    client, *_ = client_with_mocks

    response = client.post("/api/v1/ensemble_project/generate_project_totally_random")

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["share_token"], str) and len(body["share_token"]) >= 10
    assert body["level"] == 3
