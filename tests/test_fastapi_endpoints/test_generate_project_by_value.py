from core.ensable_project.api.ensable_project_models import Level

ENDPOINT = "/api/v1/ensable_project/generate_project_by_value"

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


def test_validate_project_is_called_with_correct_data(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks

    client.post(ENDPOINT, json=VALID_PAYLOAD)

    ai_gw.validate_project.assert_awaited_once()
    project_arg = ai_gw.validate_project.call_args[0][0]
    assert project_arg["programming_language"] == "Python"
    assert project_arg["technologies"] == "FastAPI"
    assert project_arg["addons"] == "PostgreSQL"
    assert project_arg["level"] == Level(level=3)


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


def test_project_repo_save_called_once(client_with_mocks):
    client, ai_gw, _, project_repo = client_with_mocks

    client.post(ENDPOINT, json=VALID_PAYLOAD)

    project_repo.save_project.assert_called_once()


def test_invalid_stack_returns_422(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    ai_gw.validate_project.return_value = (
        False,
        "COBOL + React Native is anachronistic.",
    )

    response = client.post(ENDPOINT, json=VALID_PAYLOAD)

    assert response.status_code == 422


def test_invalid_stack_error_message_in_detail(client_with_mocks):
    client, ai_gw, _, _ = client_with_mocks
    ai_gw.validate_project.return_value = (
        False,
        "Level 1 + Kubernetes is too complex.",
    )

    body = client.post(ENDPOINT, json=VALID_PAYLOAD).json()

    assert "Level 1 + Kubernetes is too complex." in body["detail"]


def test_invalid_stack_description_not_generated(client_with_mocks):
    """When validation fails, we must NOT call generate_description."""
    client, ai_gw, _, _ = client_with_mocks
    ai_gw.validate_project.return_value = (False, "Invalid stack.")

    client.post(ENDPOINT, json=VALID_PAYLOAD)

    ai_gw.generate_description.assert_not_awaited()


def test_invalid_stack_not_saved(client_with_mocks):
    """When validation fails, we must NOT persist the project."""
    client, ai_gw, _, project_repo = client_with_mocks
    ai_gw.validate_project.return_value = (False, "Invalid stack.")

    client.post(ENDPOINT, json=VALID_PAYLOAD)

    project_repo.save_project.assert_not_called()


def test_missing_required_fields_returns_422(client_with_mocks):
    client, _, _, _ = client_with_mocks

    response = client.post(
        ENDPOINT, json={"level": {"level": 3}}
    )  # missing language etc.

    assert response.status_code == 422


def test_level_out_of_range_returns_422(client_with_mocks):
    client, _, _, _ = client_with_mocks

    payload = {**VALID_PAYLOAD, "level": {"level": 6}}  # max is 5

    response = client.post(ENDPOINT, json=payload)

    assert response.status_code == 422
