from pydantic import BaseModel, Field, ConfigDict
from collections.abc import Sequence


class Level(BaseModel):
    level: int = Field(ge=1, le=5)


class Extras(BaseModel):
    programming_language: str | None = None
    technologies: str | None = None
    addons: str | None = None


class GenerateProjectByValueRequest(BaseModel):
    programming_language: str
    technologies: str
    addons: str
    extras: Sequence[Extras]
    level: Level


class ProjectResponse(BaseModel):
    programming_language: str
    technologies: str
    addons: str
    extras: list[Extras] = []
    level: int
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
