"""HU-09, Historia 4: reject oversized input before it reaches the LLM."""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from core.ensemble_project.api.ensemble_project_models import (
    MAX_EXTRAS,
    MAX_NAME_LENGTH,
    Extras,
    GenerateProjectByValueRequest,
    Level,
)
from core.settings.default import AppSettings
from tests.test_security.conftest import build_app


def valid_payload(**overrides) -> dict:
    payload = {
        "programming_language": "Rust",
        "technologies": "Distributed Cache",
        "addons": "Docker",
        "extras": [],
        "level": Level(level=3),
    }
    payload.update(overrides)
    return payload


def test_a_name_longer_than_the_bound_is_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerateProjectByValueRequest(
            **valid_payload(technologies="x" * (MAX_NAME_LENGTH + 1))
        )


def test_too_many_extras_are_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerateProjectByValueRequest(
            **valid_payload(extras=[Extras() for _ in range(MAX_EXTRAS + 1)])
        )


def test_the_maximum_allowed_extras_are_accepted() -> None:
    request = GenerateProjectByValueRequest(
        **valid_payload(extras=[Extras() for _ in range(MAX_EXTRAS)])
    )
    assert len(request.extras) == MAX_EXTRAS


@pytest.mark.parametrize("level", [0, 6, -1, 99])
def test_level_outside_one_to_five_is_rejected(level: int) -> None:
    with pytest.raises(ValidationError):
        Level(level=level)


def test_oversized_body_is_rejected_before_parsing() -> None:
    settings = AppSettings(
        ENVIRONMENT="development",
        RATE_LIMIT_ENABLED=False,
        MAX_BODY_BYTES=512,
    )
    client = TestClient(build_app(settings), raise_server_exceptions=False)

    response = client.post("/api/v1/thing", json={"blob": "x" * 5000})
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_body_within_the_limit_is_accepted() -> None:
    settings = AppSettings(
        ENVIRONMENT="development",
        RATE_LIMIT_ENABLED=False,
        MAX_BODY_BYTES=512,
    )
    client = TestClient(build_app(settings), raise_server_exceptions=False)
    assert client.post("/api/v1/thing", json={"blob": "x"}).status_code == 200
