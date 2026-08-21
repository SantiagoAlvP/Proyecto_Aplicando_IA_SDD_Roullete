"""Liveness endpoint.

Deliberately free of any dependency: the hosting platform uses it as the
deploy health check, and a cold database must not be able to fail a deploy
(spec 004, FR-005).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", include_in_schema=False)
@router.get("/")
async def health() -> dict[str, str]:
    return {"status": "healthy"}
