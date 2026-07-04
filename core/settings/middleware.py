#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project_jackpot - jero98772

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.settings.default import AppSettings


def configure_cors(app: FastAPI, settings: AppSettings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_middleware(app: FastAPI, settings: AppSettings) -> None:
    configure_cors(app, settings)
