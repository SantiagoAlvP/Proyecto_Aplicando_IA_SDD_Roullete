from fastapi.testclient import TestClient

from core.main import app, boostrap
from core.monitoring.metrics import record_project_access, reset_metrics
from core.settings.default import AppSettings

client = TestClient(app)


def test_health():
    response = client.get("/api/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_contract_is_stable_without_trailing_slash():
    """The platform polls this exact path as its liveness probe."""
    assert client.get("/api/health").json() == {"status": "healthy"}


# ── diagnostics ──────────────────────────────────────────────────────────────


def diagnostics_of(settings: AppSettings) -> dict:
    # Deliberately NOT a context manager: entering one runs the lifespan, which
    # calls init_db() and would make this test require a live Postgres
    # (Constitution, Principle III). app.state.settings is set by boostrap()
    # itself, so the endpoint has everything it needs.
    client = TestClient(boostrap(settings))
    return client.get("/api/health/diagnostics").json()


def test_diagnostics_reports_the_resolved_provider():
    body = diagnostics_of(AppSettings(AI_PROVIDER="stub", GROQ_API_KEY=None))
    assert body["ai"]["resolved_provider"] == "stub"
    assert body["ai"]["degraded"] is True


def test_diagnostics_flags_degraded_mode_even_when_groq_was_requested():
    """The whole point: AI_PROVIDER=groq with no key is silently degraded."""
    body = diagnostics_of(AppSettings(AI_PROVIDER="auto", GROQ_API_KEY=None))
    assert body["ai"]["configured_provider"] == "auto"
    assert body["ai"]["resolved_provider"] == "stub"
    assert body["ai"]["api_key_present"] is False
    assert body["ai"]["degraded"] is True


def test_diagnostics_reports_a_healthy_groq_setup():
    body = diagnostics_of(
        AppSettings(AI_PROVIDER="groq", GROQ_API_KEY="gsk-test-not-a-real-key")
    )
    assert body["ai"]["resolved_provider"] == "groq"
    assert body["ai"]["api_key_present"] is True
    assert body["ai"]["degraded"] is False
    assert body["ai"]["model"]


def test_diagnostics_never_leaks_the_api_key():
    secret = "gsk-super-secret-value-do-not-leak"
    body = diagnostics_of(AppSettings(AI_PROVIDER="groq", GROQ_API_KEY=secret))
    assert secret not in str(body)
    # The length is enough to spot a truncated paste, without exposing content.
    assert body["ai"]["api_key_length"] == len(secret)


def test_diagnostics_reports_security_configuration():
    body = diagnostics_of(
        AppSettings(
            ENVIRONMENT="production",
            CORS_ALLOWED_ORIGINS="https://example.up.railway.app",
            RATE_LIMIT_REQUESTS=42,
        )
    )
    assert body["environment"] == "production"
    assert body["security"]["rate_limit_requests"] == 42
    assert body["security"]["cors_origins"] == ["https://example.up.railway.app"]


# ── metrics ──────────────────────────────────────────────────────────────────


def test_metrics_reports_recorded_counters():
    reset_metrics()
    record_project_access("granted")
    record_project_access("granted")
    record_project_access("not_found")

    body = client.get("/api/health/metrics").json()

    assert body["counters"]["projects.get_by_id.granted"] == 2
    assert body["counters"]["projects.get_by_id.not_found"] == 1
    reset_metrics()


def test_metrics_starts_empty_when_nothing_recorded():
    reset_metrics()
    body = client.get("/api/health/metrics").json()
    assert body["counters"] == {}
