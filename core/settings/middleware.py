#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project_jackpot

"""Middleware wiring.

Order matters and is deliberate. Starlette runs the *last added* middleware
first, so registering them innermost-first gives this outside-in chain:

    SecurityHeaders -> CORS -> RequestContext -> BodySizeLimit -> RateLimit

Read from the outside in:

* **SecurityHeaders** is outermost so that *every* response is hardened -
  including 429s from the limiter, 413s from the size guard and 500s.
* **CORS** wraps the rest so a browser can actually read a 429, and so its
  preflight is answered before the limiter ever sees it (a preflight is not a
  real request; charging it would halve every browser client's budget).
* **RequestContext** assigns the correlation id and converts an unhandled
  exception into an opaque 500 - inside the header and CORS layers, so the
  error response is hardened like any other.
* **BodySizeLimit** then **RateLimit** are the cheap rejections, done last so
  the request already has an id to log against.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.security.errors import RequestContextMiddleware
from core.security.headers import SecurityHeadersMiddleware
from core.security.rate_limit import BodySizeLimitMiddleware, RateLimitMiddleware
from core.settings.default import AppSettings


def configure_cors(app: FastAPI, settings: AppSettings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
        expose_headers=["X-Request-ID", "Retry-After"],
        max_age=600,
    )


def configure_middleware(app: FastAPI, settings: AppSettings) -> None:
    # Registered innermost-first; see the module docstring for the resulting
    # outside-in chain.
    app.add_middleware(RateLimitMiddleware, settings=settings)
    app.add_middleware(BodySizeLimitMiddleware, settings=settings)
    app.add_middleware(RequestContextMiddleware)
    configure_cors(app, settings)
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
