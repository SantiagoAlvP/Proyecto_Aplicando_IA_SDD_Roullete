import logging
from collections.abc import Sequence
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # FASTAPI SETTINGS
    TITLE: str = "project_roulette"
    VERSION: str = "1.0.0"

    OPENAPI_URL: str = "/api/openapi.json"
    DOCS_URL: str = "/api/docs"
    REDOCS_URL: str = "/api/redocs"

    # DATA BASE SETTINGS
    DATA_YALM: str = "data/data.yaml"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5433"
    DB_NAME: str = "project_roulette_db"

    # PRINT LOGS
    ENABLE_LOGS: bool = True

    CORS_ALLOWED_ORIGINS: Sequence[str] = []

    @property
    def db_url(self) -> str:
        if self.DB_PASSWORD:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return (
            f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


def setup_logging(settings: AppSettings) -> None:
    if not settings.ENABLE_LOGS:
        logging.disable(logging.CRITICAL)
    else:
        logging.disable(logging.NOTSET)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
