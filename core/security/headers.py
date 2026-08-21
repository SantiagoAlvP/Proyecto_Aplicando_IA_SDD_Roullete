"""Response hardening headers.

Cheap, configuration-level mitigations for MIME sniffing, clickjacking and
script injection. Applied to every response, including error responses
(Constitution, Principle IV).
"""

from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.settings.default import AppSettings

# 'unsafe-inline' is required for styles because React injects them; scripts
# stay locked to same-origin and 'unsafe-eval' is never allowed.
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "font-src 'self' data:; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'"
)

BASE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
    "Content-Security-Policy": CONTENT_SECURITY_POLICY,
}

HSTS_HEADER = "max-age=31536000; includeSubDomains"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: AppSettings | None = None) -> None:
        super().__init__(app)
        self._settings = settings or AppSettings()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)

        for header, value in BASE_HEADERS.items():
            response.headers.setdefault(header, value)

        # HSTS only where TLS is actually terminated; sending it over plain
        # HTTP in development would lock developers out of localhost.
        if self._settings.is_production:
            response.headers.setdefault("Strict-Transport-Security", HSTS_HEADER)

        # Swagger UI needs the docs pages to be framable by nothing, but it also
        # must not be cached by shared proxies.
        if request.url.path.startswith("/api"):
            response.headers.setdefault("Cache-Control", "no-store")

        return response
