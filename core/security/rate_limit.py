"""Abuse controls: request rate and request size.

The generation endpoints call an LLM with a limited free-tier quota, so an
unthrottled loop of requests does not just slow the service down - it takes the
whole application offline for everybody (HU-09).

Known limitation, documented rather than hidden: counters live in process
memory. With several replicas the effective limit multiplies, and a restart
resets it. That is an acceptable best-effort defence for a single free-tier
replica; moving to Redis is already tracked for the next iteration.
"""

import time
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from core.settings.default import AppSettings


def client_identifier(request: Request) -> str:
    """Best-effort client identity.

    Behind Railway's proxy the socket address is the proxy, so the first hop in
    X-Forwarded-For is the closest thing to the real caller we have.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Sliding window counter, per client, in memory."""

    def __init__(self, app, settings: AppSettings | None = None) -> None:
        super().__init__(app)
        self._settings = settings or AppSettings()
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def _is_exempt(self, request: Request) -> bool:
        if request.method == "OPTIONS":
            # CORS preflight is not a real request; charging it would halve the
            # effective budget of every browser client.
            return True
        return request.url.path in self._settings.rate_limit_exempt_paths

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if not self._settings.RATE_LIMIT_ENABLED or self._is_exempt(request):
            return await call_next(request)

        window = self._settings.RATE_LIMIT_WINDOW_SECONDS
        limit = self._settings.RATE_LIMIT_REQUESTS
        now = time.monotonic()

        hits = self._hits[client_identifier(request)]
        while hits and now - hits[0] >= window:
            hits.popleft()

        if len(hits) >= limit:
            retry_after = max(1, int(window - (now - hits[0])))
            return JSONResponse(
                status_code=429,
                content={
                    "detail": (
                        "Too many requests. This service runs on a free AI tier; "
                        "please slow down."
                    ),
                    "retry_after_seconds": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        hits.append(now)
        response = await call_next(request)
        response.headers.setdefault("X-RateLimit-Limit", str(limit))
        response.headers.setdefault(
            "X-RateLimit-Remaining", str(max(0, limit - len(hits)))
        )
        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject oversized payloads before anything tries to parse them."""

    def __init__(self, app, settings: AppSettings | None = None) -> None:
        super().__init__(app)
        self._settings = settings or AppSettings()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        declared = request.headers.get("content-length")
        if declared is not None:
            try:
                size = int(declared)
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid Content-Length header."},
                )
            if size > self._settings.MAX_BODY_BYTES:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": (
                            "Request body too large. Maximum allowed is "
                            f"{self._settings.MAX_BODY_BYTES} bytes."
                        )
                    },
                )
        return await call_next(request)
