"""Liveness and runtime diagnostics.

`/api/health` stays a bare liveness probe with a stable contract: the hosting
platform gates deploys on it, so it must never depend on the database, on an
external provider, or on anything that can be slow.

`/api/health/diagnostics` answers the question that cost us three deploy cycles:
"which AI provider is this instance actually using right now?". It reports
configuration, never secrets - the API key is reduced to a boolean.
"""

from fastapi import APIRouter, Depends, Request

from core.monitoring.metrics import get_metrics_snapshot
from core.settings.default import AppSettings

router = APIRouter(prefix="/health", tags=["health"])


def get_settings(request: Request) -> AppSettings:
    return request.app.state.settings


@router.get("", include_in_schema=False)
@router.get("/")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


@router.get("/diagnostics")
async def diagnostics(
    settings: AppSettings = Depends(get_settings),
) -> dict[str, object]:
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
        },
        "database": {
            "using_platform_url": bool(settings.DATABASE_URL),
        },
        "security": {
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
            "rate_limit_requests": settings.RATE_LIMIT_REQUESTS,
            "cors_origins": settings.cors_origins,
        },
    }


@router.get("/metrics")
async def metrics() -> dict[str, object]:
    """In-process counters for endpoint usage.

    Lightweight telemetry (see core/monitoring/metrics.py): no external
    dependency, resets on restart. Useful for a quick operational check,
    not a replacement for a real metrics backend at scale.
    """
    return {"counters": get_metrics_snapshot()}
