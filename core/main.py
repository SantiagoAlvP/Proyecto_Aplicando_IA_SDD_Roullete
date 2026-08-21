#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project_jackpot

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from core.database.database import init_db
from core.routers import configure_routers
from core.security.errors import configure_exception_handlers
from core.settings.default import AppSettings, setup_logging
from core.settings.middleware import configure_middleware

logger = logging.getLogger(__name__)

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: AppSettings = app.state.settings
    setup_logging(settings)
    logger.info(
        "Starting %s v%s | environment=%s | ai_provider=%s",
        settings.TITLE,
        settings.VERSION,
        settings.ENVIRONMENT,
        settings.resolved_ai_provider,
    )
    if settings.resolved_ai_provider == "stub":
        logger.warning(
            "No AI provider configured; running in degraded mode with "
            "deterministic descriptions. Set GROQ_API_KEY to enable the LLM."
        )
    init_db()
    yield


def configure_frontend(app: FastAPI) -> None:
    """Serve the compiled SPA from the same origin as the API.

    Mounted last and only at the root, so it can never shadow /api routes.
    Absent build output is not an error: the API must still boot in CI and in
    backend-only development.
    """
    if not FRONTEND_DIST.is_dir():
        logger.info("No frontend build found at %s; serving API only.", FRONTEND_DIST)
        return

    assets = FRONTEND_DIST / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    index = FRONTEND_DIST / "index.html"

    @app.get("/", include_in_schema=False)
    async def serve_index() -> FileResponse:
        return FileResponse(index)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str) -> FileResponse:
        # An unknown /api path is a genuine 404, not a page. Without this the
        # SPA shell would be returned with status 200 and clients could not
        # tell a typo from a working endpoint.
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found.")

        # Client-side routing: any other unknown path falls back to the shell.
        candidate = (FRONTEND_DIST / full_path).resolve()
        if candidate.is_file() and FRONTEND_DIST in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(index)


def boostrap(settings: AppSettings | None = None) -> FastAPI:
    if settings is None:
        settings = AppSettings()

    app = FastAPI(
        lifespan=lifespan,
        title=settings.TITLE,
        version=settings.VERSION,
        generate_unique_id_function=lambda route: route.name,
        openapi_url=settings.OPENAPI_URL,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOCS_URL,
    )
    app.state.settings = settings
    configure_routers(app)
    configure_middleware(app, settings)
    configure_exception_handlers(app)
    configure_frontend(app)
    return app


app = boostrap()
