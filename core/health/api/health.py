"""Liveness and runtime diagnostics.

`/api/health` stays a bare liveness probe with a stable contract: the hosting
platform gates deploys on it, so it must never depend on the database, on an
external provider, or on anything that can be slow.

`/api/health/diagnostics` answers the question that cost us three deploy cycles:
"which AI provider is this instance actually using right now?". It reports
configuration, never secrets - the API key is reduced to a boolean.
"""

from typing import Any

from fastapi import APIRouter, Depends, Request

from core.database.database import check_db_connectivity, engine
from core.settings.default import AppSettings

router = APIRouter(prefix="/health", tags=["health"])


def get_settings(request: Request) -> AppSettings:
    return request.app.state.settings


def get_engine() -> Any:
    return engine


def _db_status(settings: AppSettings, db_engine: Any) -> dict[str, bool]:
    configured = bool(settings.DATABASE_URL)
    connected = check_db_connectivity(db_engine) if configured else False
    return {"connected": connected, "configured": configured}


@router.get("", include_in_schema=False)
@router.get("/")
async def health(
    settings: AppSettings = Depends(get_settings),
    db_engine: Any = Depends(get_engine),
) -> dict[str, Any]:
    return {"status": "healthy", "database": _db_status(settings, db_engine)}


@router.get("/diagnostics")
async def diagnostics(
    settings: AppSettings = Depends(get_settings),
    db_engine: Any = Depends(get_engine),
) -> dict[str, Any]:
    """Effective runtime configuration, with every secret redacted.

    `ai_provider` is the *resolved* provider, so "stub" here means the instance
    is running in degraded mode no matter what AI_PROVIDER was set to.
    """
    provider = settings.resolved_ai_provider
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "ai": {
            "configured_provider": settings.AI_PROVIDER,
            "resolved_provider": provider,
            "model": settings.GROQ_MODEL if provider == "groq" else None,
            # Never the key itself: only whether one arrived, and how long it
            # is, which is enough to catch a truncated paste.
            "api_key_present": bool(settings.GROQ_API_KEY),
            "api_key_length": len(settings.GROQ_API_KEY or ""),
            "degraded": provider == "stub",
            "ai_generation_enabled": settings.ai_generation_enabled,
        },
        "database": {
            "using_platform_url": bool(settings.DATABASE_URL),
            **_db_status(settings, db_engine),
        },
        "security": {
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "rate_limit_requests": settings.RATE_LIMIT_REQUESTS,
            "cors_origins": settings.cors_origins,
        },
    }
