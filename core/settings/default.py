#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project_jackpot

"""Application configuration.

Every value here is overridable through environment variables, which is what
makes a single container image usable in local, CI and production
(Constitution, Principle VI). No secret ever has a real default.
"""

import logging
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "production"]
AIProvider = Literal["auto", "groq", "ollama", "lmstudio", "clojure", "stub"]


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # ── FASTAPI ──────────────────────────────────────────────────────────────
    TITLE: str = "project_jackpot"
    VERSION: str = "1.0.0"

    OPENAPI_URL: str = "/api/openapi.json"
    DOCS_URL: str = "/api/docs"
    REDOCS_URL: str = "/api/redocs"

    # ── ENVIRONMENT ──────────────────────────────────────────────────────────
    ENVIRONMENT: Environment = "development"
    PORT: int = 9600
    HOST: str = "0.0.0.0"  # noqa: S104 - the container is the security boundary

    # ── DATABASE ─────────────────────────────────────────────────────────────
    # Managed platforms (Railway, Render, Neon...) inject a single DATABASE_URL.
    # Local development uses the discrete components below.
    DATABASE_URL: str | None = None

    DATA_YALM: str = "data/data.yaml"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5433"
    DB_NAME: str = "project_jackpot_db"

    # ── LOGGING ──────────────────────────────────────────────────────────────
    ENABLE_LOGS: bool = True
    LOG_LEVEL: str = "INFO"

    # ── SECURITY ─────────────────────────────────────────────────────────────
    # Comma-separated whitelist. "*" is rejected at startup in production.
    CORS_ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 20
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_EXEMPT_PATHS: str = (
        "/api/health,/api/health/,/api/docs,/api/redocs,/api/openapi.json"
    )

    MAX_BODY_BYTES: int = 64 * 1024  # 64 KiB is generous for our largest payload

    # ── PROJECT GENERATION ───────────────────────────────────────────────────
    CANDIDATES: int = 2
    MAX_EXTRAS: int = 20
    MAX_NAME_LENGTH: int = 100
    MAX_DESCRIPTION_LENGTH: int = 500
    HISTORY_MAX_LIMIT: int = 50

    # ── AI GATEWAY ───────────────────────────────────────────────────────────
    # "auto" resolves to groq when GROQ_API_KEY is present, and to the
    # deterministic stub otherwise, so the app never fails to boot because an
    # optional credential is missing (Constitution, Principle V).
    AI_PROVIDER: AIProvider = "auto"
    AI_TIMEOUT_SECONDS: float = 30.0
    TEMPERATURE: float = 0.7

    # Groq (free tier, OpenAI-compatible) - production
    GROQ_API_KEY: str | None = None
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # LM Studio - local desktop
    BASE_URL_LMSTUDIO: str = "http://localhost:1234/v1"
    API_KEY_LMSTUDIO: str = "lm-studio"
    LMSTUDIO_MODEL: str = "gemma4:E2B"

    # Ollama - local development
    OLLAMA_MODEL: str = "gemma4:E2B"
    OLLAMA_HOST: str = "http://localhost:11434"

    # ── DERIVED VALUES ───────────────────────────────────────────────────────
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def db_url(self) -> str:
        """Full SQLAlchemy URL.

        A platform-provided DATABASE_URL always wins. Some providers still hand
        out the legacy ``postgres://`` scheme, which SQLAlchemy rejected in 1.4;
        normalising it here saves a production-only failure.
        """
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url

        if self.DB_PASSWORD:
            return (
                f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
        return (
            f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def cors_origins(self) -> list[str]:
        """Explicit allow-list, never a wildcard in production.

        Failing loudly at startup is preferable to silently serving a
        world-open API (Constitution, Principle IV).
        """
        origins = [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]
        if self.is_production and "*" in origins:
            raise ValueError(
                "CORS_ALLOWED_ORIGINS must not contain '*' in production. "
                "List the exact allowed origins instead."
            )
        return origins

    @property
    def rate_limit_exempt_paths(self) -> frozenset[str]:
        return frozenset(
            p.strip() for p in self.RATE_LIMIT_EXEMPT_PATHS.split(",") if p.strip()
        )

    @property
    def resolved_ai_provider(self) -> str:
        """Turn "auto" into a concrete provider name."""
        if self.AI_PROVIDER != "auto":
            return self.AI_PROVIDER
        if self.GROQ_API_KEY:
            return "groq"
        return "stub"

    @staticmethod
    def message_base(prompt: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]


def setup_logging(settings: AppSettings) -> None:
    if not settings.ENABLE_LOGS:
        logging.disable(logging.CRITICAL)
        return

    logging.disable(logging.NOTSET)
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
