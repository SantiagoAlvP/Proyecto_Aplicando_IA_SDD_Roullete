import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from core.catalog.catalog_repository import CatalogRepository
from core.catalog.catalog_service import CatalogService, DefaultCatalogService
from core.database.database import get_db
from core.monitoring.metrics import record_project_access
from core.security.auth import get_optional_current_user, is_owner, has_permission

router = APIRouter(prefix="/projects", tags=["projects"])

# Dedicated logger for auditing access to protected resources. Kept separate
# from the module-level app logger so it can be filtered/shipped independently
# (e.g. to a security audit sink) without pulling in unrelated request noise.
audit_logger = logging.getLogger("audit.projects")


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
        record_project_access("not_found")
        raise HTTPException(status_code=404, detail="Not found.")

    # Enforce visibility: if project has is_public and is False, require auth
    if getattr(project, "is_public", True) is False:
        requester_id = getattr(user, "id", None)

        # Not authenticated
        if user is None:
            audit_logger.warning(
                "private_project_access_denied",
                extra={"project_id": project_id, "reason": "unauthenticated"},
            )
            record_project_access("unauthorized")
            raise HTTPException(status_code=401, detail="Unauthorized.")

        # Owner allowed
        if is_owner(user, getattr(project, "owner_id", None)):
            audit_logger.info(
                "private_project_access_granted",
                extra={
                    "project_id": project_id,
                    "user_id": requester_id,
                    "reason": "owner",
                },
            )
            record_project_access("granted")
            return project

        # Permission check
        if has_permission(user, "ver_proyecto"):
            audit_logger.info(
                "private_project_access_granted",
                extra={
                    "project_id": project_id,
                    "user_id": requester_id,
                    "reason": "permission",
                },
            )
            record_project_access("granted")
            return project

        audit_logger.warning(
            "private_project_access_denied",
            extra={
                "project_id": project_id,
                "user_id": requester_id,
                "reason": "forbidden",
            },
        )
        record_project_access("forbidden")
        raise HTTPException(status_code=403, detail="Forbidden.")

    record_project_access("granted")
    return project
