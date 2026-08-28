from core.ensemble_project.api.ensemble_project_models import ProjectSelection
from unittest.mock import MagicMock

ENDPOINT = "/api/v1/ensemble_project/generate_project_by_value"

VALID_PAYLOAD = {
    "programming_language": "Python",
    "technologies": "FastAPI",
    "addons": "PostgreSQL",
    "extras": [],
    "level": {"level": 3},
}


def test_generate_by_value_returns_201(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    response = client.post(ENDPOINT, json=VALID_PAYLOAD)
    assert response.status_code == 201


def test_generate_by_value_response_shape(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    body = client.post(ENDPOINT, json=VALID_PAYLOAD).json()
    assert body["programming_language"] == "Python"
    assert body["technologies"] == "FastAPI"
    assert body["addons"] == "PostgreSQL"
    assert body["level"] == 3
    assert "description" in body
    assert isinstance(body["description"], str)


def test_generate_by_value_with_extras(client_with_mocks):
    client, ai_gw, _, project_repo = client_with_mocks

    payload = {
        **VALID_PAYLOAD,
        "extras": [
            {"programming_language": "TypeScript", "technologies": None, "addons": None}
        ],
    }
    project_repo.save_project.return_value = {
        "id": 1,
        "programming_language": "Python",
        "technologies": "FastAPI",
        "addons": "PostgreSQL",
        "extras": [
            {"programming_language": "TypeScript", "technologies": None, "addons": None}
        ],
        "level": 3,
        "description": "Build a REST API.",
    }

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 201
    saved_arg = project_repo.save_project.call_args[0][0]
    assert any(
        e.get("programming_language") == "TypeScript" for e in saved_arg["extras"]
    )


def test_choose_valid_project_is_called_with_correct_data(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks

    client.post(ENDPOINT, json=VALID_PAYLOAD)

    ai_gw.choose_valid_project.assert_awaited_once()
    projects_arg = ai_gw.choose_valid_project.call_args[0][0]
    project_arg = projects_arg[0]
    assert project_arg["programming_language"] == "Python"
    assert project_arg["technologies"] == "FastAPI"
    assert project_arg["addons"] == "PostgreSQL"
    assert project_arg["level"] == 3


def test_description_is_generated(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    client.post(ENDPOINT, json=VALID_PAYLOAD)
    ai_gw.generate_description.assert_awaited_once()


def test_description_is_persisted(client_with_mocks):
    client, ai_gw, _, project_repo = client_with_mocks
    ai_gw.generate_description.return_value = "Custom description."
    client.post(ENDPOINT, json=VALID_PAYLOAD)
    saved = project_repo.save_project.call_args[0][0]
    assert saved["description"] == "Custom description."


def test_excluded_values_are_ignored_when_randomising_reels(client_with_mocks):
    client, _, catalog, project_repo = client_with_mocks
    excluded = ["Rust", "Docker", "Sublime Text"]

    def named(value: str):
        item = MagicMock()
        item.name = value
        return item

    catalog.get_programming_languages.return_value = [
        named("Python"),
        named("Rust"),
    ]
    catalog.get_technologies.return_value = [
        named("FastAPI"),
        named("Docker"),
    ]
    catalog.get_addons.return_value = [
        named("PostgreSQL"),
        named("Sublime Text"),
    ]

    client.post(
        ENDPOINT,
        json={
            **VALID_PAYLOAD,
            "programming_language": "",
            "technologies": "",
            "addons": "",
            "excluded": excluded,
        },
    )

    saved = project_repo.save_project.call_args[0][0]
    assert saved["programming_language"] == "Python"
    assert saved["technologies"] == "FastAPI"
    assert saved["addons"] in {"PostgreSQL", "Sublime Text"}


def test_excluded_list_is_bounded(client_with_mocks):
    client, _, _, _ = client_with_mocks

    response = client.post(
        ENDPOINT,
        json={**VALID_PAYLOAD, "excluded": [f"value-{index}" for index in range(51)]},
    )

    assert response.status_code == 422


def test_project_repo_save_called_once(client_with_mocks):
    client, ai_gw, _, project_repo = client_with_mocks
    client.post(ENDPOINT, json=VALID_PAYLOAD)
    project_repo.save_project.assert_called_once()


def test_invalid_stack_returns_422(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    ai_gw.choose_valid_project.return_value = ProjectSelection(
        best_index=1, valid=False, reason="COBOL + React Native is anachronistic."
    )

    response = client.post(ENDPOINT, json=VALID_PAYLOAD)

    assert response.status_code == 422


def test_invalid_stack_error_message_in_detail(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    ai_gw.choose_valid_project.return_value = ProjectSelection(
        best_index=1, valid=False, reason="Level 1 + Kubernetes is too complex."
    )

    body = client.post(ENDPOINT, json=VALID_PAYLOAD).json()

    assert "Level 1 + Kubernetes is too complex." in body["detail"]


def test_invalid_stack_description_not_generated(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    ai_gw.choose_valid_project.return_value = ProjectSelection(
        best_index=1, valid=False, reason="Invalid stack."
    )
    client.post(ENDPOINT, json=VALID_PAYLOAD)
    ai_gw.generate_description.assert_not_awaited()


def test_invalid_stack_not_saved(client_with_mocks):
    client, ai_gw, _, project_repo = client_with_mocks
    ai_gw.choose_valid_project.return_value = ProjectSelection(
        best_index=1, valid=False, reason="Invalid stack."
    )
    client.post(ENDPOINT, json=VALID_PAYLOAD)
    project_repo.save_project.assert_not_called()


def test_missing_required_fields_returns_422(client_with_mocks):
    client, _, _, _ = client_with_mocks
    response = client.post(ENDPOINT, json={"level": {"level": 3}})
    assert response.status_code == 422


def test_level_out_of_range_returns_422(client_with_mocks):
    client, _, _, _ = client_with_mocks
    payload = {**VALID_PAYLOAD, "level": {"level": 6}}
    response = client.post(ENDPOINT, json=payload)
    assert response.status_code == 422


def test_extras_placeholder_values_are_filled(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks

    payload = {
        **VALID_PAYLOAD,
        "level": {"level": 1},
        "extras": [
            {
                "programming_language": "clojure",
                "technologies": "string",
                "addons": "string",
            }
        ],
    }
    client.post(ENDPOINT, json=payload)

    projects_arg = ai_gw.choose_valid_project.call_args[0][0]
    extras = projects_arg[0]["extras"]

    first = extras[0]
    assert first["programming_language"] == "clojure"  # untouched real value
    assert first["technologies"] != "string"
    assert first["addons"] != "string"
    assert first["technologies"] is not None
    assert first["addons"] is not None
