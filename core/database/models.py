from datetime import datetime, timezone
from typing import Optional

from secrets import token_urlsafe

from sqlmodel import Field, Relationship, SQLModel


def _new_share_token() -> str:
    """Public identity of a project: opaque, unguessable, URL-safe.

    12 bytes of entropy (~96 bits) render as ~16 characters, which fits the
    `[A-Za-z0-9_-]{10,64}` contract enforced at the HTTP edge (HU-20, D-01).
    """
    return token_urlsafe(12)


class ProjectProgrammingLanguage(SQLModel, table=True):
    __tablename__ = "project_programming_languages"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

    projects: list["Project"] = Relationship(back_populates="programming_language")
    extras: list["ProjectExtra"] = Relationship(back_populates="programming_language")


class ProjectTech(SQLModel, table=True):
    __tablename__ = "project_techs"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

    projects: list["Project"] = Relationship(back_populates="tech")
    extras: list["ProjectExtra"] = Relationship(back_populates="tech")


class ProjectAddon(SQLModel, table=True):
    __tablename__ = "project_addons"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, unique=True)

    projects: list["Project"] = Relationship(back_populates="addon")
    extras: list["ProjectExtra"] = Relationship(back_populates="addon")


class ProjectExtra(SQLModel, table=True):
    __tablename__ = "project_extras"

    id: Optional[int] = Field(default=None, primary_key=True)
    project_programming_language_id: int = Field(
        foreign_key="project_programming_languages.id", nullable=False
    )
    project_tech_id: Optional[int] = Field(default=None, foreign_key="project_techs.id")
    project_addon_id: Optional[int] = Field(
        default=None, foreign_key="project_addons.id"
    )
    projects_id: int = Field(foreign_key="projects.id", nullable=False)

    programming_language: Optional[ProjectProgrammingLanguage] = Relationship(
        back_populates="extras"
    )
    tech: Optional[ProjectTech] = Relationship(back_populates="extras")
    addon: Optional[ProjectAddon] = Relationship(back_populates="extras")
    project: Optional["Project"] = Relationship(back_populates="extras")


class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True)
    description: Optional[str] = Field(default=None, max_length=500)
    programming_language_id: int = Field(
        foreign_key="project_programming_languages.id", nullable=False
    )
    project_tech_id: int = Field(default=None, foreign_key="project_techs.id")
    project_addon_id: int = Field(default=None, foreign_key="project_addons.id")

    # HU-20: the share link is permanent (FR-006); the token lives and dies
    # with the project and is never regenerated.
    share_token: str = Field(
        default_factory=_new_share_token,
        unique=True,
        index=True,
        max_length=64,
        nullable=False,
    )
    level: Optional[int] = Field(
        default=None,
        description="Difficulty 1..5; NULL for rows created before HU-20.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    programming_language: Optional[ProjectProgrammingLanguage] = Relationship(
        back_populates="projects"
    )
    tech: ProjectTech = Relationship(back_populates="projects")
    addon: ProjectAddon = Relationship(back_populates="projects")
    extras: list[ProjectExtra] = Relationship(back_populates="project")
