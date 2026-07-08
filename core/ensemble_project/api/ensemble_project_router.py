from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import Session
from core.database.database import get_db
from core.ensemble_project.api.ensemble_project_models import (
    GenerateProjectByValueRequest,
    Level,
    ProjectResponse,
)
from core.catalog.catalog_repository import CatalogRepository
from core.ensemble_project.ensemble_project_repository import EnsembleProjectRepository
from core.ensemble_project.ensemble_project_service import ProjectGeneratorService
from core.settings.clojure_settings import ClojureProjectGeneratorAIGateway

router = APIRouter(prefix="/ensemble_project", tags=["ensemble_project"])


def get_project_service(db: Session = Depends(get_db)) -> ProjectGeneratorService:
    # ai_gateway = ProjectGeneratorAIGateway()
    ai_gateway = ClojureProjectGeneratorAIGateway()
    catalog_repo = CatalogRepository(db)
    project_repo = EnsembleProjectRepository(db)
    return ProjectGeneratorService(ai_gateway, catalog_repo, project_repo)


@router.post(
    "/generate_project_by_value",
    status_code=status.HTTP_201_CREATED,
)
async def generate_project_by_value(
    payload: GenerateProjectByValueRequest,
    service: ProjectGeneratorService = Depends(get_project_service),
):
    try:
        return await service.generate_by_value(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/generate_project_by_level",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_project_by_level(
    payload: Level,
    service: ProjectGeneratorService = Depends(get_project_service),
):
    return await service.generate_by_level(payload)


@router.post(
    "/generate_project_totally_random",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_project_totally_random(
    service: ProjectGeneratorService = Depends(get_project_service),
):
    return await service.generate_random()
