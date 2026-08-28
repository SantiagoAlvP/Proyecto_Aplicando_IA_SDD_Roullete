from core.catalog.catalog_service import DefaultCatalogService


class FakeRepo:
    def __init__(self):
        self.called = False

    def get_project_by_id(self, pid):
        self.called = True
        # construct a simple object with an id attribute
        class P:
            def __init__(self, id):
                self.id = id
                self.description = "fake"

        return P(pid)


def test_service_get_project_by_id():
    repo = FakeRepo()
    service = DefaultCatalogService(repo)
    p = service.get_project_by_id(123)
    assert repo.called
    assert p.id == 123
