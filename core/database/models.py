from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


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

    programming_language: Optional[ProjectProgrammingLanguage] = Relationship(
        back_populates="projects"
    )
    tech: ProjectTech = Relationship(back_populates="projects")
    addon: ProjectAddon = Relationship(back_populates="projects")
    extras: list[ProjectExtra] = Relationship(back_populates="project")
