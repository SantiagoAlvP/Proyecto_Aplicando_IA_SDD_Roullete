"""HTTP layer for project generation.

The router owns exactly two things: translating HTTP into DTOs, and translating
domain errors into status codes. It never touches the database and never picks
an AI provider itself (Constitution, Principle II).
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from core.ai_gateway.factory import get_ai_gateway
from core.catalog.catalog_repository import CatalogRepository
from core.database.database import get_db
from core.ensemble_project.ai_project_advisor import AIProjectAdvisor
from core.ensemble_project.api.ensemble_project_models import (
    GenerateProjectByValueRequest,
    HistoryEntry,
    Level,
    ProjectResponse,
    RegenerationResponse,
)
from core.ensemble_project.ensemble_project_repository import EnsembleProjectRepository
from core.ensemble_project.ensemble_project_service import (
    ProjectGeneratorService,
    ProjectNotFoundError,
)
from core.settings.default import AppSettings

router = APIRouter(prefix="/ensemble_project", tags=["ensemble_project"])

settings = AppSettings()


def get_project_service(db: Session = Depends(get_db)) -> ProjectGeneratorService:
    """Assemble the service with the provider chosen by configuration.

    Swapping Ollama for Groq is AI_PROVIDER=groq - no code change here.
    """
    advisor = AIProjectAdvisor(get_ai_gateway(settings), settings)
    return ProjectGeneratorService(
        advisor,
        CatalogRepository(db),
        EnsembleProjectRepository(db),
    )


@router.post(
    "/generate_project_by_value",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_project_by_value(
    payload: GenerateProjectByValueRequest,
    service: ProjectGeneratorService = Depends(get_project_service),
):
    try:
        return await service.generate_by_value(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/generate_project_by_level",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_project_by_level(
    payload: Level,
    service: ProjectGeneratorService = Depends(get_project_service),
):
    try:
        return await service.generate_by_level(payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/generate_project_totally_random",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_project_totally_random(
    service: ProjectGeneratorService = Depends(get_project_service),
):
    try:
        return await service.generate_random()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/history", response_model=list[HistoryEntry])
async def get_history(
    limit: int = Query(
        default=10,
        ge=1,
        le=50,
        description="How many of the most recent projects to return.",
    ),
    service: ProjectGeneratorService = Depends(get_project_service),
) -> list[HistoryEntry]:
    """Most recently generated projects, newest first."""
    return service.get_history(limit)


@router.post(
    "/{project_id}/regenerate_description",
    response_model=RegenerationResponse,
    status_code=status.HTTP_200_OK,
)
async def regenerate_description(
    project_id: int = Path(ge=1),
    service: ProjectGeneratorService = Depends(get_project_service),
) -> RegenerationResponse:
    try:
        return await service.regenerate_description(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
