"""HU-11, HU-12, HU-13: mark, list and unmark favorite projects."""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.ensemble_project.api.ensemble_project_models import HistoryEntry
from core.ensemble_project.api.ensemble_project_router import (
    get_project_service,
    router,
)

FAVORITES_ENDPOINT = "/api/v1/ensemble_project/favorites"


def favorite_url(project_id: int) -> str:
    return f"/api/v1/ensemble_project/{project_id}/favorite"


def entry(entry_id: int, *, favorite: bool = True) -> HistoryEntry:
    return HistoryEntry(
        id=entry_id,
        programming_language="Rust",
        technologies="Distributed Cache",
        addons="Docker",
        level=3,
        extras=[],
        description=f"Project number {entry_id}.",
        favorite=favorite,
    )


@pytest.fixture
def client_and_service():
    service = MagicMock()
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_project_service] = lambda: service
    with TestClient(app) as client:
        yield client, service


# --- PUT /{project_id}/favorite (HU-11) ---------------------------------


def test_marking_an_existing_project_returns_it_as_favorite(client_and_service) -> None:
    client, service = client_and_service
    service.mark_favorite.return_value = entry(1, favorite=True)

    response = client.put(favorite_url(1))

    assert response.status_code == 200
    assert response.json()["favorite"] is True
    service.mark_favorite.assert_called_once_with(1)


def test_marking_twice_is_idempotent(client_and_service) -> None:
    """FR-005: repeating the operation must not fail or duplicate."""
    client, service = client_and_service
    service.mark_favorite.return_value = entry(1, favorite=True)

    first = client.put(favorite_url(1))
    second = client.put(favorite_url(1))

    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()


def test_marking_a_nonexistent_project_returns_404(client_and_service) -> None:
    """FR-008: an explicit error, nothing is altered."""
    client, service = client_and_service
    service.mark_favorite.side_effect = LookupError("Project 999 not found.")

    response = client.put(favorite_url(999))

    assert response.status_code == 404


@pytest.mark.parametrize("project_id", [0, -1])
def test_marking_a_non_positive_id_is_rejected(client_and_service, project_id) -> None:
    client, service = client_and_service

    response = client.put(favorite_url(project_id))

    assert response.status_code == 422
    service.mark_favorite.assert_not_called()


# --- DELETE /{project_id}/favorite (HU-13) ------------------------------


def test_unmarking_an_existing_favorite_returns_it_as_not_favorite(
    client_and_service,
) -> None:
    client, service = client_and_service
    service.unmark_favorite.return_value = entry(1, favorite=False)

    response = client.delete(favorite_url(1))

    assert response.status_code == 200
    assert response.json()["favorite"] is False
    service.unmark_favorite.assert_called_once_with(1)


def test_unmarking_twice_is_idempotent(client_and_service) -> None:
    """FR-006: repeating the operation must not produce an error."""
    client, service = client_and_service
    service.unmark_favorite.return_value = entry(1, favorite=False)

    first = client.delete(favorite_url(1))
    second = client.delete(favorite_url(1))

    assert first.status_code == second.status_code == 200


def test_unmarking_a_nonexistent_project_returns_404(client_and_service) -> None:
    client, service = client_and_service
    service.unmark_favorite.side_effect = LookupError("Project 999 not found.")

    response = client.delete(favorite_url(999))

    assert response.status_code == 404


@pytest.mark.parametrize("project_id", [0, -1])
def test_unmarking_a_non_positive_id_is_rejected(
    client_and_service, project_id
) -> None:
    client, service = client_and_service

    response = client.delete(favorite_url(project_id))

    assert response.status_code == 422
    service.unmark_favorite.assert_not_called()


# --- GET /favorites (HU-12) ---------------------------------------------


def test_returns_only_favorited_projects_newest_first(client_and_service) -> None:
    client, service = client_and_service
    service.get_favorites.return_value = [entry(3), entry(2), entry(1)]

    response = client.get(FAVORITES_ENDPOINT)

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [3, 2, 1]


def test_entries_include_level_and_extras(client_and_service) -> None:
    """FR-009: same information shown at generation time."""
    client, service = client_and_service
    service.get_favorites.return_value = [entry(1)]

    body = client.get(FAVORITES_ENDPOINT).json()[0]

    assert set(body) >= {"level", "extras"}
    assert body["level"] == 3


def test_default_limit_is_ten(client_and_service) -> None:
    client, service = client_and_service
    service.get_favorites.return_value = []

    client.get(FAVORITES_ENDPOINT)

    service.get_favorites.assert_called_once_with(10)


@pytest.mark.parametrize("limit", [0, -1, 51, 1000])
def test_out_of_range_limits_are_rejected(client_and_service, limit: int) -> None:
    client, _ = client_and_service
    assert client.get(FAVORITES_ENDPOINT, params={"limit": limit}).status_code == 422


def test_no_favorites_yields_an_empty_list_not_an_error(client_and_service) -> None:
    client, service = client_and_service
    service.get_favorites.return_value = []

    response = client.get(FAVORITES_ENDPOINT)

    assert response.status_code == 200
    assert response.json() == []
