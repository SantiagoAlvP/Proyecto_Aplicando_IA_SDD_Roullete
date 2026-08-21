"""Request correlation and leak-free error responses.

A stack trace in an HTTP response is a free map of the system for an attacker,
so the client gets a neutral message plus a correlation id, and the full detail
goes to the server log under that same id (Constitution, Principle IV).
"""

import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"

GENERIC_ERROR_MESSAGE = (
    "An internal error occurred. Quote the request id when reporting it."
)


def get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request id and log one structured line per request.

    The body is never logged: it is user input and could carry anything.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:12]
        request.state.request_id = request_id

        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # Handled here rather than through add_exception_handler(Exception)
            # because Starlette's ServerErrorMiddleware sits outside every user
            # middleware: a response produced there would escape without the
            # security headers. Catching it inside keeps the guarantee that
            # *every* response is hardened.
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.exception(
                "request_id=%s %s %s -> unhandled exception in %.1fms",
                request_id,
                request.method,
                request.url.path,
                elapsed_ms,
            )
            response = JSONResponse(
                status_code=500,
                content={
                    "detail": GENERIC_ERROR_MESSAGE,
                    "request_id": request_id,
                },
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response

        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "request_id=%s %s %s -> %s in %.1fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Deliberate errors keep their message: we wrote them, they are safe."""
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": request_id},
        headers={REQUEST_ID_HEADER: request_id},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Say which field is wrong, without exposing the internal model shape."""
    request_id = get_request_id(request)
    errors = [
        {
            "field": ".".join(str(part) for part in error.get("loc", ())[1:]) or "body",
            "message": error.get("msg", "Invalid value."),
        }
        for error in exc.errors()
    ]
    logger.info("request_id=%s validation rejected: %s", request_id, errors)
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Invalid request.",
            "errors": errors,
            "request_id": request_id,
        },
        headers={REQUEST_ID_HEADER: request_id},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Everything else becomes an opaque 500 plus a correlation id."""
    request_id = get_request_id(request)
    logger.exception("request_id=%s unhandled exception", request_id)
    return JSONResponse(
        status_code=500,
        content={"detail": GENERIC_ERROR_MESSAGE, "request_id": request_id},
        headers={REQUEST_ID_HEADER: request_id},
    )


def configure_exception_handlers(app: FastAPI) -> None:
    # Starlette types handlers against the base Exception while dispatching
    # the concrete subclass; the narrowing is correct at runtime.
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # ty: ignore[invalid-argument-type]
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # ty: ignore[invalid-argument-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)
