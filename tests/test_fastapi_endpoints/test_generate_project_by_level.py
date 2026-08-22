import pytest
from unittest.mock import patch

ENDPOINT = "/api/v1/ensemble_project/generate_project_by_level"


@pytest.mark.parametrize("level", [1, 2, 3, 4, 5])
def test_generate_by_level_returns_201_for_all_valid_levels(client_with_mocks, level):
    client, _, _, _ = client_with_mocks

    response = client.post(ENDPOINT, json={"level": level})

    assert response.status_code == 201


def test_generate_by_level_response_shape(client_with_mocks):
    client, _, _, _ = client_with_mocks

    body = client.post(ENDPOINT, json={"level": 3}).json()

    required_fields = {
        "programming_language",
        "technologies",
        "addons",
        "level",
        "description",
    }
    assert required_fields.issubset(body.keys())


def test_generate_by_level_level_is_preserved(client_with_mocks):
    """The level in the saved project must match the requested level."""
    client, _, _, project_repo = client_with_mocks

    for lvl in [1, 3, 5]:
        project_repo.save_project.return_value = {
            "id": 1,
            "programming_language": "Python",
            "technologies": "FastAPI",
            "addons": "PostgreSQL",
            "extras": [],
            "level": lvl,
            "description": "desc",
        }
        body = client.post(ENDPOINT, json={"level": lvl}).json()
        assert body["level"] == lvl


# ── AI interactions ──────────────────────────────────────────────────────────


def test_choose_valid_project_is_called(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks

    client.post(ENDPOINT, json={"level": 3})

    ai_gw.choose_valid_project.assert_awaited_once()


def test_candidates_count_matches_settings(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks

    with patch(
        "core.ensemble_project.ensemble_project_service.AppSettings"
    ) as mock_settings:
        mock_settings.return_value.CANDIDATES = 4
        client.post(ENDPOINT, json={"level": 2})

    candidates_arg = ai_gw.choose_valid_project.call_args[0][0]
    assert len(candidates_arg) == 4


def test_candidates_all_have_correct_level(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks

    with patch(
        "core.ensemble_project.ensemble_project_service.AppSettings"
    ) as mock_settings:
        mock_settings.return_value.CANDIDATES = 3
        client.post(ENDPOINT, json={"level": 4})

    candidates = ai_gw.choose_valid_project.call_args[0][0]
    assert all(c["level"] == 4 for c in candidates)


def test_description_generated_for_chosen_project(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks

    client.post(ENDPOINT, json={"level": 3})

    ai_gw.generate_description.assert_awaited_once()


def test_chosen_project_gets_description_before_save(client_with_mocks):
    client, ai_gw, _, project_repo = client_with_mocks
    ai_gw.generate_description.return_value = "Generated desc."

    client.post(ENDPOINT, json={"level": 3})

    saved = project_repo.save_project.call_args[0][0]
    assert saved["description"] == "Generated desc."


def test_catalog_repo_queried_for_each_candidate(client_with_mocks):
    client, _, catalog, _ = client_with_mocks

    with patch(
        "core.ensemble_project.ensemble_project_service.AppSettings"
    ) as mock_settings:
        mock_settings.return_value.CANDIDATES = 3
        client.post(ENDPOINT, json={"level": 1})

    assert catalog.get_random_programming_language.call_count >= 3
    assert catalog.get_random_technology.call_count >= 3
    assert catalog.get_random_addon.call_count >= 3


@pytest.mark.parametrize("bad_level", [0, 6, -1, 100])
def test_level_out_of_range_returns_422(client_with_mocks, bad_level):
    client, _, _, _ = client_with_mocks

    response = client.post(ENDPOINT, json={"level": bad_level})

    assert response.status_code == 422


def test_missing_level_field_returns_422(client_with_mocks):
    client, _, _, _ = client_with_mocks

    response = client.post(ENDPOINT, json={})

    assert response.status_code == 422


def test_wrong_type_for_level_returns_422(client_with_mocks):
    client, _, _, _ = client_with_mocks

    response = client.post(ENDPOINT, json={"level": "senior"})  # must be int

    assert response.status_code == 422
