"""Fixtures for the security suite.

Each test builds a tiny app with only the middleware under test, so a failure
points at one component instead of at "something in the stack".
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.security.errors import configure_exception_handlers
from core.settings.default import AppSettings
from core.settings.middleware import configure_middleware


def build_app(settings: AppSettings) -> FastAPI:
    app = FastAPI()

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    @app.get("/api/v1/thing")
    async def thing() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/api/v1/thing")
    async def create_thing(payload: dict) -> dict:
        return payload

    @app.get("/api/v1/boom")
    async def boom() -> dict:
        raise RuntimeError("secret internal detail: table users, /srv/app/db.py")

    configure_middleware(app, settings)
    configure_exception_handlers(app)
    return app


@pytest.fixture
def dev_settings() -> AppSettings:
    return AppSettings(ENVIRONMENT="development", RATE_LIMIT_ENABLED=False)


@pytest.fixture
def prod_settings() -> AppSettings:
    return AppSettings(
        ENVIRONMENT="production",
        RATE_LIMIT_ENABLED=False,
        CORS_ALLOWED_ORIGINS="https://project-jackpot.up.railway.app",
    )


@pytest.fixture
def client(dev_settings: AppSettings) -> TestClient:
    return TestClient(build_app(dev_settings), raise_server_exceptions=False)
