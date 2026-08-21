"""Input and output contracts.

Every externally supplied field carries an explicit bound. Validation is the
cheapest and most reliable defence we have: Pydantic rejects an abusive payload
before the service runs and therefore before a single LLM token is spent
(Constitution, Principle IV; spec 003, HU-09).
"""

from collections.abc import Sequence

from pydantic import BaseModel, ConfigDict, Field

MAX_NAME_LENGTH = 100
MAX_EXTRAS = 20
MAX_DESCRIPTION_LENGTH = 500
MIN_LEVEL = 1
MAX_LEVEL = 5

CatalogName = Field(default=None, max_length=MAX_NAME_LENGTH)


class Level(BaseModel):
    level: int = Field(ge=MIN_LEVEL, le=MAX_LEVEL)


class Extras(BaseModel):
    programming_language: str | None = Field(default=None, max_length=MAX_NAME_LENGTH)
    technologies: str | None = Field(default=None, max_length=MAX_NAME_LENGTH)
    addons: str | None = Field(default=None, max_length=MAX_NAME_LENGTH)


class GenerateProjectByValueRequest(BaseModel):
    # The three reels are required but may be empty: an empty value (or
    # Swagger's "string" placeholder) means "surprise me", which is exactly the
    # lock-one-reel behaviour of HU-03.
    programming_language: str = Field(max_length=MAX_NAME_LENGTH)
    technologies: str = Field(max_length=MAX_NAME_LENGTH)
    addons: str = Field(max_length=MAX_NAME_LENGTH)
    extras: Sequence[Extras] = Field(default_factory=list, max_length=MAX_EXTRAS)
    level: Level


class ProjectResponse(BaseModel):
    programming_language: str
    technologies: str
    addons: str
    extras: list[Extras] = []
    level: int
    description: str


class HistoryEntry(BaseModel):
    """One previously generated project, as shown in the history panel."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    programming_language: str
    technologies: str
    addons: str
    description: str


class ValidationResult(BaseModel):
    valid: bool = Field(description="Whether the tech stack is coherent and practical")
    reason: str = Field(
        default="",
        description="Short explanation when valid is False; empty string otherwise",
    )


class BestIndex(BaseModel):
    best_index: int = Field(
        description="1-based index of the most coherent, practical, and learnable candidate",
    )


class Entity(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class NamedCatalogEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str


class ProjectSelection(BaseModel):
    best_index: int
    valid: bool
    reason: str | None = None
