from unittest.mock import patch

ENDPOINT = "/api/v1/ensemble_project/generate_project_totally_random"


def test_generate_random_returns_201(client_with_mocks):
    client, _, _, _ = client_with_mocks
    response = client.post(ENDPOINT)
    assert response.status_code == 201


def test_generate_random_no_body_required(client_with_mocks):
    client, _, _, _ = client_with_mocks
    response = client.post(ENDPOINT, json=None)
    assert response.status_code == 201


def test_generate_random_response_shape(client_with_mocks):
    client, _, _, _ = client_with_mocks
    body = client.post(ENDPOINT).json()
    for field in (
        "programming_language",
        "technologies",
        "addons",
        "level",
        "description",
    ):
        assert field in body, f"Missing field: {field}"


def test_generate_random_level_in_valid_range(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    with patch(
        "core.ensemble_project.ensemble_project_service.AppSettings"
    ) as mock_settings:
        mock_settings.return_value.CANDIDATES = 3
        for _ in range(10):
            client.post(ENDPOINT)
            candidates = ai_gw.choose_valid_project.call_args[0][0]
            level = candidates[0]["level"]
            assert 1 <= level <= 5, f"Level {level} is out of the 1-5 range"


def test_choose_valid_project_called(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    client.post(ENDPOINT)
    ai_gw.choose_valid_project.assert_awaited_once()


def test_generate_description_called(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    client.post(ENDPOINT)
    ai_gw.generate_description.assert_awaited_once()


def test_description_saved_in_project(client_with_mocks):
    client, ai_gw, _, project_repo = client_with_mocks
    ai_gw.generate_description.return_value = "Random project description."
    client.post(ENDPOINT)
    saved = project_repo.save_project.call_args[0][0]
    assert saved["description"] == "Random project description."


def test_project_repo_save_called_once(client_with_mocks):
    client, _, _, project_repo = client_with_mocks
    client.post(ENDPOINT)
    project_repo.save_project.assert_called_once()


def test_catalog_called_for_random_picks(client_with_mocks):
    client, _, catalog, _ = client_with_mocks
    client.post(ENDPOINT)
    catalog.get_random_programming_language.assert_called()
    catalog.get_random_technology.assert_called()
    catalog.get_random_addon.assert_called()


def test_each_call_triggers_independent_save(client_with_mocks):
    client, _, _, project_repo = client_with_mocks
    client.post(ENDPOINT)
    client.post(ENDPOINT)
    assert project_repo.save_project.call_count == 2


def test_fixed_level_via_randint_mock(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    with (
        patch("core.ensemble_project.ensemble_project_service.randint", return_value=2),
        patch(
            "core.ensemble_project.ensemble_project_service.AppSettings"
        ) as mock_settings,
    ):
        mock_settings.return_value.CANDIDATES = 2
        client.post(ENDPOINT)
    candidates = ai_gw.choose_valid_project.call_args[0][0]
    assert all(c["level"] == 2 for c in candidates)
