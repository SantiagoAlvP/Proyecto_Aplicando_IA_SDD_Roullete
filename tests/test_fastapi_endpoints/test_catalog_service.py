from core.database.models import ProjectAddon, ProjectProgrammingLanguage, ProjectTech


class TestGetProgrammingLanguages:
    def test_delegates_to_repo(self, service, mock_repo):
        expected = [ProjectProgrammingLanguage(id=1, name="Python")]
        mock_repo.get_programming_languages.return_value = expected
        assert service.get_programming_languages() == expected

    def test_calls_repo_once(self, service, mock_repo):
        mock_repo.get_programming_languages.return_value = []
        service.get_programming_languages()
        mock_repo.get_programming_languages.assert_called_once()

    def test_returns_empty_list(self, service, mock_repo):
        mock_repo.get_programming_languages.return_value = []
        assert service.get_programming_languages() == []


class TestGetTechnologies:
    def test_delegates_to_repo(self, service, mock_repo):
        expected = [ProjectTech(id=1, name="FastAPI")]
        mock_repo.get_technologies.return_value = expected
        assert service.get_technologies() == expected

    def test_calls_repo_once(self, service, mock_repo):
        mock_repo.get_technologies.return_value = []
        service.get_technologies()
        mock_repo.get_technologies.assert_called_once()

    def test_returns_empty_list(self, service, mock_repo):
        mock_repo.get_technologies.return_value = []
        assert service.get_technologies() == []


class TestGetAddons:
    def test_delegates_to_repo(self, service, mock_repo):
        expected = [ProjectAddon(id=1, name="Docker")]
        mock_repo.get_addons.return_value = expected
        assert service.get_addons() == expected

    def test_calls_repo_once(self, service, mock_repo):
        mock_repo.get_addons.return_value = []
        service.get_addons()
        mock_repo.get_addons.assert_called_once()

    def test_returns_empty_list(self, service, mock_repo):
        mock_repo.get_addons.return_value = []
        assert service.get_addons() == []


class TestGetRandomProgrammingLanguage:
    def test_wraps_result_under_correct_key(self, service, mock_repo):
        lang = ProjectProgrammingLanguage(id=1, name="Python")
        mock_repo.get_random_programming_language.return_value = lang
        assert service.get_random_programming_language() == {
            "programming_language": lang
        }

    def test_returns_none_when_catalog_is_empty(self, service, mock_repo):
        mock_repo.get_random_programming_language.return_value = None
        assert service.get_random_programming_language() is None

    def test_calls_repo_once(self, service, mock_repo):
        mock_repo.get_random_programming_language.return_value = None
        service.get_random_programming_language()
        mock_repo.get_random_programming_language.assert_called_once()


class TestGetRandomTechnology:
    def test_wraps_result_under_correct_key(self, service, mock_repo):
        tech = ProjectTech(id=1, name="FastAPI")
        mock_repo.get_random_technology.return_value = tech
        assert service.get_random_technology() == {"technology": tech}

    def test_returns_none_when_catalog_is_empty(self, service, mock_repo):
        mock_repo.get_random_technology.return_value = None
        assert service.get_random_technology() is None

    def test_calls_repo_once(self, service, mock_repo):
        mock_repo.get_random_technology.return_value = None
        service.get_random_technology()
        mock_repo.get_random_technology.assert_called_once()


class TestGetRandomAddon:
    def test_wraps_result_under_correct_key(self, service, mock_repo):
        addon = ProjectAddon(id=1, name="Docker")
        mock_repo.get_random_addon.return_value = addon
        assert service.get_random_addon() == {"addon": addon}

    def test_returns_none_when_catalog_is_empty(self, service, mock_repo):
        mock_repo.get_random_addon.return_value = None
        assert service.get_random_addon() is None

    def test_calls_repo_once(self, service, mock_repo):
        mock_repo.get_random_addon.return_value = None
        service.get_random_addon()
        mock_repo.get_random_addon.assert_called_once()
