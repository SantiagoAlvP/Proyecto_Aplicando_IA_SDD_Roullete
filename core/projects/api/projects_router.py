from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.catalog.catalog_repository import CatalogRepository
from core.catalog.catalog_service import CatalogService, DefaultCatalogService
from core.database.database import get_db
from core.security.auth import get_optional_current_user, is_owner, has_permission

router = APIRouter(prefix="/projects", tags=["projects"])


def get_catalog_service(db: Session = Depends(get_db)) -> CatalogService:
    repo = CatalogRepository(db)
    return DefaultCatalogService(repo)


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    service: CatalogService = Depends(get_catalog_service),
    user: Optional[object] = Depends(get_optional_current_user),
):
    project = service.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Not found.")

    # Enforce visibility: if project has is_public and is False, require auth
    if getattr(project, "is_public", True) is False:
        # Not authenticated
        if user is None:
            raise HTTPException(status_code=401, detail="Unauthorized.")
        # Owner allowed
        if is_owner(user, getattr(project, "owner_id", None)):
            return project
        # Permission check
        if has_permission(user, "ver_proyecto"):
            return project
        raise HTTPException(status_code=403, detail="Forbidden.")

    return project
