"""Spec 004, HU-04: one origin serves the SPA, the API and the docs."""

from fastapi.testclient import TestClient

from core.main import FRONTEND_DIST, configure_frontend
from core.settings.default import AppSettings

from fastapi import FastAPI


def build_app() -> FastAPI:
    app = FastAPI()

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    configure_frontend(app)
    return app


def test_the_api_still_wins_over_the_spa_catch_all() -> None:
    client = TestClient(build_app())
    assert client.get("/api/health").json() == {"status": "healthy"}


def test_an_unknown_api_path_is_a_404_not_the_spa_shell() -> None:
    """Returning the HTML shell with a 200 would hide typos in API routes."""
    if not FRONTEND_DIST.is_dir():
        return  # No build present (backend-only CI job); nothing to assert.
    client = TestClient(build_app())
    assert client.get("/api/v1/does-not-exist").status_code == 404


def test_the_root_serves_the_spa_when_a_build_exists() -> None:
    if not FRONTEND_DIST.is_dir():
        return
    client = TestClient(build_app())
    response = client.get("/")
    assert response.status_code == 200
    assert '<div id="root">' in response.text


def test_an_unknown_page_falls_back_to_the_spa_shell() -> None:
    if not FRONTEND_DIST.is_dir():
        return
    client = TestClient(build_app())
    assert client.get("/whatever/deep/link").status_code == 200


def test_the_api_boots_without_a_frontend_build() -> None:
    """CI and backend-only development must not need Node."""
    app = FastAPI()
    configure_frontend(app)  # must not raise, whatever the build state
    assert AppSettings().TITLE
