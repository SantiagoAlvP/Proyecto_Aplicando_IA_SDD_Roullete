import logging
from collections.abc import Sequence
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    # FASTAPI SETTINGS
    TITLE: str = "project_jackpot"
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
    DB_NAME: str = "project_jackpot_db"

    # PRINT LOGS
    ENABLE_LOGS: bool = True

    CORS_ALLOWED_ORIGINS: Sequence[str] = []

    # GENERATE PROJECT SETTINGS
    CANDIDATES: int = 2

    # LLM CONSTANTS LMSTUDIO
    BASE_URL_LMSTUDIO: str = "http://localhost:1234/v1"
    API_KEY_LMSTUDIO: str = "lm-studio"
    LMSTUDIO_MODEL: str = "gemma4:E2B"
    TEMPERATURE: float = 0.7

    # LLM CONSTANTS OLLAMA
    OLLAMA_MODEL: str = "gemma4:E2B"
    OLLAMA_HOST: str = "http://localhost:11434"

    @property
    def db_url(self) -> str:
        if self.DB_PASSWORD:
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return (
            f"postgresql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @staticmethod
    def message_base(prompt) -> list:
        return [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]


def setup_logging(settings: AppSettings) -> None:
    if not settings.ENABLE_LOGS:
        logging.disable(logging.CRITICAL)
    else:
        logging.disable(logging.NOTSET)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    )
