"""HU-09, Historia 2: errors must not hand an attacker a map of the system."""

from fastapi.testclient import TestClient

LEAKY_FRAGMENTS = (
    "Traceback",
    "secret internal detail",
    "table users",
    "/srv/app/db.py",
    "RuntimeError",
    "core/security",
)


def test_unhandled_error_returns_a_neutral_500(client: TestClient) -> None:
    response = client.get("/api/v1/boom")
    assert response.status_code == 500
    assert response.json()["detail"] == (
        "An internal error occurred. Quote the request id when reporting it."
    )


def test_unhandled_error_leaks_nothing(client: TestClient) -> None:
    body = client.get("/api/v1/boom").text
    for fragment in LEAKY_FRAGMENTS:
        assert fragment not in body, f"response leaked {fragment!r}"


def test_error_carries_a_correlation_id(client: TestClient) -> None:
    response = client.get("/api/v1/boom")
    assert response.json()["request_id"]
    assert response.headers["X-Request-ID"] == response.json()["request_id"]


def test_every_response_carries_a_correlation_id(client: TestClient) -> None:
    assert client.get("/api/v1/thing").headers["X-Request-ID"]


def test_incoming_correlation_id_is_honoured(client: TestClient) -> None:
    """Lets a caller trace one request across the whole system."""
    response = client.get("/api/v1/thing", headers={"X-Request-ID": "trace-me-123"})
    assert response.headers["X-Request-ID"] == "trace-me-123"


def test_the_failure_is_logged_with_its_id(client: TestClient, caplog) -> None:
    with caplog.at_level("ERROR"):
        response = client.get("/api/v1/boom")
    request_id = response.json()["request_id"]
    assert request_id in caplog.text
    # The detail the client did NOT get must be in the log.
    assert "secret internal detail" in caplog.text
