from abc import ABC, abstractmethod

from core.catalog.catalog_repository import CatalogRepository
from core.database.models import ProjectAddon, ProjectProgrammingLanguage, ProjectTech


class CatalogService(ABC):
    @abstractmethod
    def get_programming_languages(self) -> list[ProjectProgrammingLanguage]: ...

    @abstractmethod
    def get_technologies(self) -> list[ProjectTech]: ...

    @abstractmethod
    def get_addons(self) -> list[ProjectAddon]: ...

    @abstractmethod
    def get_random_programming_language(self) -> dict | None: ...

    @abstractmethod
    def get_random_technology(self) -> dict | None: ...

    @abstractmethod
    def get_random_addon(self) -> dict | None: ...

    @abstractmethod
    def get_project_by_id(self, project_id: int): ...


class DefaultCatalogService(CatalogService):
    def __init__(self, repo: CatalogRepository):
        self.repo = repo

    def get_programming_languages(self) -> list[ProjectProgrammingLanguage]:
        return self.repo.get_programming_languages()

    def get_technologies(self) -> list[ProjectTech]:
        return self.repo.get_technologies()

    def get_addons(self) -> list[ProjectAddon]:
        return self.repo.get_addons()

    def get_random_programming_language(self) -> dict | None:
        result = self.repo.get_random_programming_language()
        return {"programming_language": result} if result else None

    def get_random_technology(self) -> dict | None:
        result = self.repo.get_random_technology()
        return {"technology": result} if result else None

    def get_random_addon(self) -> dict | None:
        result = self.repo.get_random_addon()
        return {"addon": result} if result else None

    def get_project_by_id(self, project_id: int):
        """Return the Project model instance or None if not found."""
        return self.repo.get_project_by_id(project_id)
