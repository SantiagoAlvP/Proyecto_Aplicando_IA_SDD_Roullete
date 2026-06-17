import random
from abc import ABC, abstractmethod

from sqlmodel import Session

from core.database.crud import AddonCRUD, ProgrammingLanguageCRUD, TechCRUD
from core.database.models import ProjectAddon, ProjectProgrammingLanguage, ProjectTech


class CatalogRepository(ABC):
    @abstractmethod
    def get_programming_languages(self) -> list[ProjectProgrammingLanguage]: ...

    @abstractmethod
    def get_technologies(self) -> list[ProjectTech]: ...

    @abstractmethod
    def get_addons(self) -> list[ProjectAddon]: ...

    @abstractmethod
    def get_random_programming_language(self) -> ProjectProgrammingLanguage | None: ...

    @abstractmethod
    def get_random_technology(self) -> ProjectTech | None: ...

    @abstractmethod
    def get_random_addon(self) -> ProjectAddon | None: ...


class SQLModelCatalogRepository(CatalogRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_programming_languages(self) -> list[ProjectProgrammingLanguage]:
        return list(ProgrammingLanguageCRUD.get_all(self.session))

    def get_technologies(self) -> list[ProjectTech]:
        return list(TechCRUD.get_all(self.session))

    def get_addons(self) -> list[ProjectAddon]:
        return list(AddonCRUD.get_all(self.session))

    def get_random_programming_language(self) -> ProjectProgrammingLanguage | None:
        langs = list(ProgrammingLanguageCRUD.get_all(self.session))
        return random.choice(langs) if langs else None

    def get_random_technology(self) -> ProjectTech | None:
        techs = list(TechCRUD.get_all(self.session))
        return random.choice(techs) if techs else None

    def get_random_addon(self) -> ProjectAddon | None:
        addons = list(AddonCRUD.get_all(self.session))
        return random.choice(addons) if addons else None
