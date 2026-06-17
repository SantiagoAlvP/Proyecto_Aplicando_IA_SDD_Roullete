from fastapi import APIRouter, FastAPI

from core.health.health import router as health_router
from core.catalog.catalog_router import router as catalog_router
from core.ensable_project.ensable_project_router import router as ensable_project_router


def configure_routers(fast_api: FastAPI):
    api_router = APIRouter(prefix="/api")
    api_router.include_router(health_router)
    v1_router = APIRouter(prefix="/v1")
    v1_router.include_router(catalog_router)
    v1_router.include_router(ensable_project_router)
    api_router.include_router(v1_router)
    fast_api.include_router(api_router)
