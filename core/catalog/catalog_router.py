from fastapi import APIRouter, Depends
from sqlmodel import Session

from core.catalog.catalog_repository import SQLModelCatalogRepository
from core.catalog.catalog_service import CatalogService, DefaultCatalogService
from core.database.database import get_db

router = APIRouter(prefix="/catalog", tags=["catalog"])


def get_catalog_service(db: Session = Depends(get_db)) -> CatalogService:
    repo = SQLModelCatalogRepository(db)
    return DefaultCatalogService(repo)


@router.get("/programming-languages")
async def get_programming_languages(
    service: CatalogService = Depends(get_catalog_service),
):
    return service.get_programming_languages()


@router.get("/technologies")
async def get_technologies(
    service: CatalogService = Depends(get_catalog_service),
):
    return service.get_technologies()


@router.get("/addons")
async def get_addons(
    service: CatalogService = Depends(get_catalog_service),
):
    return service.get_addons()


@router.get("/programming-languages/random")
async def get_random_programming_language(
    service: CatalogService = Depends(get_catalog_service),
):
    return service.get_random_programming_language()


@router.get("/technologies/random")
async def get_random_technology(
    service: CatalogService = Depends(get_catalog_service),
):
    return service.get_random_technology()


@router.get("/addons/random")
async def get_random_addon(
    service: CatalogService = Depends(get_catalog_service),
):
    return service.get_random_addon()
