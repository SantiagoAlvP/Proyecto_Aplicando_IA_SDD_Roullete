from core.database.crud import (
    AddonCRUD,
    ProgrammingLanguageCRUD,
    ProjectCRUD,
    ProjectExtraCRUD,
    TechCRUD,
)
from core.database.models import (
    Project,
    ProjectAddon,
    ProjectExtra,
    ProjectProgrammingLanguage,
    ProjectTech,
)


class TestProgrammingLanguageCRUD:
    def test_create_adds_and_commits(self, session):
        result = ProgrammingLanguageCRUD.create(session, "Python")

        session.add.assert_called_once()
        session.commit.assert_called_once()
        session.refresh.assert_called_once()
        assert result.name == "Python"

    def test_create_returns_correct_type(self, session):
        result = ProgrammingLanguageCRUD.create(session, "Rust")
        assert isinstance(result, ProjectProgrammingLanguage)

    def test_get_calls_session_get(self, session):
        session.get.return_value = ProjectProgrammingLanguage(id=1, name="Python")

        result = ProgrammingLanguageCRUD.get(session, 1)

        session.get.assert_called_once_with(ProjectProgrammingLanguage, 1)
        assert result is not None
        assert result.name == "Python"

    def test_get_returns_none_when_not_found(self, session):
        session.get.return_value = None

        result = ProgrammingLanguageCRUD.get(session, 99)

        assert result is None

    def test_get_by_name_returns_match(self, session):
        lang = ProjectProgrammingLanguage(id=1, name="Python")
        session.exec.return_value.first.return_value = lang

        result = ProgrammingLanguageCRUD.get_by_name(session, "Python")
        assert result is not None
        assert result.name == "Python"

    def test_get_by_name_returns_none_when_missing(self, session):
        session.exec.return_value.first.return_value = None

        result = ProgrammingLanguageCRUD.get_by_name(session, "COBOL")

        assert result is None

    def test_get_all_returns_list(self, session):
        langs = [
            ProjectProgrammingLanguage(id=1, name="Python"),
            ProjectProgrammingLanguage(id=2, name="Rust"),
            ProjectProgrammingLanguage(id=3, name="Go"),
            ProjectProgrammingLanguage(id=4, name="Lisp"),
            ProjectProgrammingLanguage(id=5, name="Clojure"),
        ]
        session.exec.return_value.all.return_value = langs

        result = ProgrammingLanguageCRUD.get_all(session)

        assert len(result) == 5
        assert result[1].name == "Rust"

    def test_get_all_returns_empty_list(self, session):
        session.exec.return_value.all.return_value = []

        result = ProgrammingLanguageCRUD.get_all(session)

        assert result == []


class TestTechCRUD:
    def test_create_returns_tech(self, session):
        result = TechCRUD.create(session, "Docker")

        assert isinstance(result, ProjectTech)
        assert result.name == "Docker"
        session.add.assert_called_once()
        session.commit.assert_called_once()

    def test_get_by_name_found(self, session):
        tech = ProjectTech(id=1, name="Docker")
        session.exec.return_value.first.return_value = tech

        result = TechCRUD.get_by_name(session, "Docker")
        assert result is not None
        assert result.name == "Docker"

    def test_get_by_name_not_found(self, session):
        result = TechCRUD.get_by_name(session, "NonExistent")
        assert result is None

    def test_get_returns_correct_record(self, session):
        tech = ProjectTech(id=5, name="Kubernetes")
        session.get.return_value = tech

        result = TechCRUD.get(session, 5)

        session.get.assert_called_once_with(ProjectTech, 5)
        assert result is not None
        assert result.name == "Kubernetes"

    def test_get_all(self, session):
        techs = [ProjectTech(id=1, name="Git"), ProjectTech(id=2, name="Docker")]
        session.exec.return_value.all.return_value = techs

        result = TechCRUD.get_all(session)

        assert len(result) == 2


class TestAddonCRUD:
    def test_create_returns_addon(self, session):
        result = AddonCRUD.create(session, "VSCode")

        assert isinstance(result, ProjectAddon)
        assert result.name == "VSCode"

    def test_get_by_name_found(self, session):
        addon = ProjectAddon(id=1, name="VSCode")
        session.exec.return_value.first.return_value = addon

        result = AddonCRUD.get_by_name(session, "VSCode")
        assert result is not None
        assert result.name == "VSCode"

    def test_get_by_name_not_found(self, session):
        result = AddonCRUD.get_by_name(session, "Vim")
        assert result is None

    def test_get_returns_none_for_missing_id(self, session):
        session.get.return_value = None

        result = AddonCRUD.get(session, 999)

        assert result is None

    def test_get_all_empty(self, session):
        result = AddonCRUD.get_all(session)
        assert result == []


class TestProjectCRUD:
    def test_create_with_required_fields_only(self, session):
        result = ProjectCRUD.create(session, programming_language_id=1)

        assert isinstance(result, Project)
        assert result.programming_language_id == 1
        assert result.description is None
        assert result.project_tech_id is None
        assert result.project_addon_id is None
        session.add.assert_called_once()
        session.commit.assert_called_once()

    def test_create_with_all_fields(self, session):
        result = ProjectCRUD.create(
            session,
            programming_language_id=1,
            description="My API",
            project_tech_id=2,
            project_addon_id=3,
        )

        assert result.description == "My API"
        assert result.project_tech_id == 2
        assert result.project_addon_id == 3

    def test_get_returns_project(self, session):
        project = Project(id=1, programming_language_id=1)
        session.get.return_value = project

        result = ProjectCRUD.get(session, 1)

        session.get.assert_called_once_with(Project, 1)
        assert result is project

    def test_get_returns_none_when_not_found(self, session):
        session.get.return_value = None

        result = ProjectCRUD.get(session, 42)

        assert result is None

    def test_get_all_returns_projects(self, session):
        projects = [
            Project(id=1, programming_language_id=1),
            Project(id=2, programming_language_id=2),
        ]
        session.exec.return_value.all.return_value = projects

        result = ProjectCRUD.get_all(session)

        assert len(result) == 2


class TestProjectExtraCRUD:
    def test_create_with_required_fields(self, session):
        result = ProjectExtraCRUD.create(
            session,
            projects_id=1,
            project_programming_language_id=2,
        )

        assert isinstance(result, ProjectExtra)
        assert result.projects_id == 1
        assert result.project_programming_language_id == 2
        assert result.project_tech_id is None
        assert result.project_addon_id is None

    def test_create_with_optional_fields(self, session):
        result = ProjectExtraCRUD.create(
            session,
            projects_id=1,
            project_programming_language_id=2,
            project_tech_id=3,
            project_addon_id=4,
        )

        assert result.project_tech_id == 3
        assert result.project_addon_id == 4

    def test_get_by_project_returns_extras(self, session):
        extras = [
            ProjectExtra(id=1, projects_id=5, project_programming_language_id=1),
            ProjectExtra(id=2, projects_id=5, project_programming_language_id=2),
        ]
        session.exec.return_value.all.return_value = extras

        result = ProjectExtraCRUD.get_by_project(session, 5)

        assert len(result) == 2
        assert all(e.projects_id == 5 for e in result)

    def test_get_by_project_returns_empty(self, session):
        session.exec.return_value.all.return_value = []

        result = ProjectExtraCRUD.get_by_project(session, 99)

        assert result == []
