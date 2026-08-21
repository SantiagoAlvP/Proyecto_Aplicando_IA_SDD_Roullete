"""HU-09, Historia 3: hardening headers on every response."""

from fastapi.testclient import TestClient

from core.security.headers import BASE_HEADERS
from core.settings.default import AppSettings
from tests.test_security.conftest import build_app

REQUIRED = (
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Content-Security-Policy",
)


def test_all_required_headers_are_present(client: TestClient) -> None:
    response = client.get("/api/v1/thing")
    for header in REQUIRED:
        assert header in response.headers, f"missing {header}"


def test_nosniff_and_deny_values(client: TestClient) -> None:
    headers = client.get("/api/v1/thing").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"


def test_csp_forbids_eval_and_foreign_scripts(client: TestClient) -> None:
    csp = client.get("/api/v1/thing").headers["Content-Security-Policy"]
    assert "'unsafe-eval'" not in csp
    assert "script-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp


def test_headers_are_present_on_error_responses_too(client: TestClient) -> None:
    response = client.get("/api/v1/boom")
    assert response.status_code == 500
    for header in REQUIRED:
        assert header in response.headers


def test_hsts_only_in_production(
    client: TestClient, prod_settings: AppSettings
) -> None:
    assert "Strict-Transport-Security" not in client.get("/api/v1/thing").headers

    prod_client = TestClient(build_app(prod_settings), raise_server_exceptions=False)
    assert "Strict-Transport-Security" in prod_client.get("/api/v1/thing").headers


def test_base_headers_are_not_empty() -> None:
    assert all(value for value in BASE_HEADERS.values())
