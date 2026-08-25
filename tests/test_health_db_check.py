"""Tests for the database connectivity check in the health endpoint (HU-22).

The health and diagnostics endpoints must report the real DB connectivity status
while always returning HTTP 200 to preserve Railway compatibility.
"""

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from core.main import boostrap
from core.settings.default import AppSettings


def _make_client(
    *,
    db_connected: bool = True,
    db_configured: bool = True,
) -> TestClient:
    """Build a TestClient with a mocked database engine."""
    mock_engine = MagicMock()
    if db_connected:
        mock_engine.connect.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_engine.connect.return_value.__exit__ = MagicMock(return_value=False)
    else:
        mock_engine.connect.side_effect = ConnectionError("DB unreachable")

    if db_configured:
        settings = AppSettings(DATABASE_URL="postgresql://test:test@localhost/test")
    else:
        settings = AppSettings()
    app = boostrap(settings)

    def _get_engine():
        return mock_engine

    from core.health.api.health import get_engine

    app.dependency_overrides[get_engine] = _get_engine

    return TestClient(app, raise_server_exceptions=False)


# ── US1: /api/health reports database connectivity ───────────────────────────


class TestHealthEndpointDBCheck:
    def test_health_always_returns_200(self) -> None:
        client = _make_client(db_connected=False)
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_reports_connected_when_db_ok(self) -> None:
        client = _make_client(db_connected=True, db_configured=True)
        body = client.get("/api/health").json()
        assert body["status"] == "healthy"
        assert body["database"]["connected"] is True
        assert body["database"]["configured"] is True

    def test_health_reports_disconnected_when_db_down(self) -> None:
        client = _make_client(db_connected=False, db_configured=True)
        body = client.get("/api/health").json()
        assert body["status"] == "healthy"
        assert body["database"]["connected"] is False
        assert body["database"]["configured"] is True

    def test_health_reports_unconfigured_when_no_db_url(self) -> None:
        client = _make_client(db_connected=False, db_configured=False)
        body = client.get("/api/health").json()
        assert body["status"] == "healthy"
        assert body["database"]["connected"] is False
        assert body["database"]["configured"] is False

    def test_health_response_never_exposes_sql_errors(self) -> None:
        client = _make_client(db_connected=False)
        raw = client.get("/api/health").text
        assert "SELECT" not in raw
        assert "pg_" not in raw
        assert "traceback" not in raw.lower()


# ── US2: /api/health/diagnostics reports database connectivity ────────────────


class TestDiagnosticsEndpointDBCheck:
    def test_diagnostics_reports_connected_when_db_ok(self) -> None:
        client = _make_client(db_connected=True, db_configured=True)
        body = client.get("/api/health/diagnostics").json()
        assert body["database"]["connected"] is True
        assert body["database"]["configured"] is True

    def test_diagnostics_reports_disconnected_when_db_down(self) -> None:
        client = _make_client(db_connected=False, db_configured=True)
        body = client.get("/api/health/diagnostics").json()
        assert body["database"]["connected"] is False
        assert body["database"]["configured"] is True

    def test_diagnostics_preserves_using_platform_url(self) -> None:
        client = _make_client(db_connected=True)
        body = client.get("/api/health/diagnostics").json()
        assert "using_platform_url" in body["database"]
