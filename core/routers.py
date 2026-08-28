#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project_jackpot - jero98772

from fastapi import APIRouter, FastAPI

from core.health.api.health import router as health_router
from core.catalog.api.catalog_router import router as catalog_router
from core.ensemble_project.api.ensemble_project_router import (
    router as ensemble_project_router,
)
from core.projects.api.projects_router import router as projects_router


def configure_routers(fast_api: FastAPI):
    api_router = APIRouter(prefix="/api")
    api_router.include_router(health_router)
    v1_router = APIRouter(prefix="/v1")
    v1_router.include_router(catalog_router)
    v1_router.include_router(ensemble_project_router)
    v1_router.include_router(projects_router)
    api_router.include_router(v1_router)
    fast_api.include_router(api_router)
