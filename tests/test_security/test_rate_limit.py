"""HU-09, Historia 1: the free AI tier must survive a scripted loop."""

from fastapi.testclient import TestClient

from core.settings.default import AppSettings
from tests.test_security.conftest import build_app

LIMIT = 5


def limited_client() -> TestClient:
    settings = AppSettings(
        ENVIRONMENT="development",
        RATE_LIMIT_ENABLED=True,
        RATE_LIMIT_REQUESTS=LIMIT,
        RATE_LIMIT_WINDOW_SECONDS=60,
    )
    return TestClient(build_app(settings), raise_server_exceptions=False)


def test_requests_under_the_limit_pass() -> None:
    client = limited_client()
    for _ in range(LIMIT):
        assert client.get("/api/v1/thing").status_code == 200


def test_request_over_the_limit_is_rejected_with_429() -> None:
    client = limited_client()
    for _ in range(LIMIT):
        client.get("/api/v1/thing")

    response = client.get("/api/v1/thing")
    assert response.status_code == 429


def test_rejection_tells_the_client_when_to_come_back() -> None:
    client = limited_client()
    for _ in range(LIMIT + 1):
        response = client.get("/api/v1/thing")

    assert response.status_code == 429
    assert int(response.headers["Retry-After"]) >= 1
    assert response.json()["retry_after_seconds"] >= 1


def test_clients_are_counted_independently() -> None:
    client = limited_client()
    for _ in range(LIMIT):
        client.get("/api/v1/thing", headers={"X-Forwarded-For": "10.0.0.1"})

    assert (
        client.get("/api/v1/thing", headers={"X-Forwarded-For": "10.0.0.1"}).status_code
        == 429
    )
    assert (
        client.get("/api/v1/thing", headers={"X-Forwarded-For": "10.0.0.2"}).status_code
        == 200
    )


def test_health_is_never_rate_limited() -> None:
    """The platform polls it as a liveness probe; limiting it kills deploys."""
    client = limited_client()
    for _ in range(LIMIT * 4):
        assert client.get("/api/health").status_code == 200


def test_remaining_budget_is_advertised() -> None:
    client = limited_client()
    response = client.get("/api/v1/thing")
    assert response.headers["X-RateLimit-Limit"] == str(LIMIT)
    assert int(response.headers["X-RateLimit-Remaining"]) == LIMIT - 1
