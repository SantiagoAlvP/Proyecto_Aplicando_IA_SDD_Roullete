class TestGetProgrammingLanguages:
    URL = "/catalog/programming-languages"

    def test_status_ok(self, client, mock_service, LANGUAGES):
        mock_service.get_programming_languages.return_value = LANGUAGES
        assert client.get(self.URL).status_code == 200

    def test_returns_list(self, client, mock_service, LANGUAGES):
        mock_service.get_programming_languages.return_value = LANGUAGES
        assert client.get(self.URL).json() == LANGUAGES

    def test_returns_empty_list(self, client, mock_service):
        mock_service.get_programming_languages.return_value = []
        assert client.get(self.URL).json() == []

    def test_calls_service_once(self, client, mock_service):
        mock_service.get_programming_languages.return_value = []
        client.get(self.URL)
        mock_service.get_programming_languages.assert_called_once()


class TestGetTechnologies:
    URL = "/catalog/technologies"

    def test_status_ok(self, client, mock_service, TECHS):
        mock_service.get_technologies.return_value = TECHS
        assert client.get(self.URL).status_code == 200

    def test_returns_list(self, client, mock_service, TECHS):
        mock_service.get_technologies.return_value = TECHS
        assert client.get(self.URL).json() == TECHS

    def test_returns_empty_list(self, client, mock_service):
        mock_service.get_technologies.return_value = []
        assert client.get(self.URL).json() == []

    def test_calls_service_once(self, client, mock_service):
        mock_service.get_technologies.return_value = []
        client.get(self.URL)
        mock_service.get_technologies.assert_called_once()


class TestGetAddons:
    URL = "/catalog/addons"

    def test_status_ok(self, client, mock_service, ADDONS):
        mock_service.get_addons.return_value = ADDONS
        assert client.get(self.URL).status_code == 200

    def test_returns_list(self, client, mock_service, ADDONS):
        mock_service.get_addons.return_value = ADDONS
        assert client.get(self.URL).json() == ADDONS

    def test_returns_empty_list(self, client, mock_service):
        mock_service.get_addons.return_value = []
        assert client.get(self.URL).json() == []

    def test_calls_service_once(self, client, mock_service):
        mock_service.get_addons.return_value = []
        client.get(self.URL)
        mock_service.get_addons.assert_called_once()


class TestGetRandomProgrammingLanguage:
    URL = "/catalog/programming-languages/random"
    PAYLOAD = {"programming_language": {"id": 1, "name": "Python"}}

    def test_status_ok(self, client, mock_service):
        mock_service.get_random_programming_language.return_value = self.PAYLOAD
        assert client.get(self.URL).status_code == 200

    def test_returns_wrapped_item(self, client, mock_service):
        mock_service.get_random_programming_language.return_value = self.PAYLOAD
        assert client.get(self.URL).json() == self.PAYLOAD

    def test_returns_null_when_catalog_is_empty(self, client, mock_service):
        mock_service.get_random_programming_language.return_value = None
        assert client.get(self.URL).json() is None

    def test_calls_service_once(self, client, mock_service):
        mock_service.get_random_programming_language.return_value = None
        client.get(self.URL)
        mock_service.get_random_programming_language.assert_called_once()


class TestGetRandomTechnology:
    URL = "/catalog/technologies/random"
    PAYLOAD = {"technology": {"id": 1, "name": "FastAPI"}}

    def test_status_ok(self, client, mock_service):
        mock_service.get_random_technology.return_value = self.PAYLOAD
        assert client.get(self.URL).status_code == 200

    def test_returns_wrapped_item(self, client, mock_service):
        mock_service.get_random_technology.return_value = self.PAYLOAD
        assert client.get(self.URL).json() == self.PAYLOAD

    def test_returns_null_when_catalog_is_empty(self, client, mock_service):
        mock_service.get_random_technology.return_value = None
        assert client.get(self.URL).json() is None

    def test_calls_service_once(self, client, mock_service):
        mock_service.get_random_technology.return_value = None
        client.get(self.URL)
        mock_service.get_random_technology.assert_called_once()


class TestGetRandomAddon:
    URL = "/catalog/addons/random"
    PAYLOAD = {"addon": {"id": 1, "name": "Docker"}}

    def test_status_ok(self, client, mock_service):
        mock_service.get_random_addon.return_value = self.PAYLOAD
        assert client.get(self.URL).status_code == 200

    def test_returns_wrapped_item(self, client, mock_service):
        mock_service.get_random_addon.return_value = self.PAYLOAD
        assert client.get(self.URL).json() == self.PAYLOAD

    def test_returns_null_when_catalog_is_empty(self, client, mock_service):
        mock_service.get_random_addon.return_value = None
        assert client.get(self.URL).json() is None

    def test_calls_service_once(self, client, mock_service):
        mock_service.get_random_addon.return_value = None
        client.get(self.URL)
        mock_service.get_random_addon.assert_called_once()
