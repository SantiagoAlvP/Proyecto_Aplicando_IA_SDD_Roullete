# Tasks for get-project-by-id

Phase 1 — Setup

- [ ] T001 Initialize feature branch and directory (specs/006-get-project-by-id) 
- [ ] T002 Update API router registration if needed (core/routers.py)
- [ ] T003 Add contract and quickstart artifacts to spec directory (specs/006-get-project-by-id/contracts, quickstart.md)

Phase 2 — Foundational

- [x] T010 [P] [US1] Add Project data model fields or validate existing model to include: is_public, owner_id, owner_name (core/database/models.py) — confirmado presente
- [x] T011 [P] [US1] ~~Add DB seed for test projects~~ — N/A: data/data.yaml es el catálogo de lenguajes/techs/addons usado para GENERAR proyectos (core/database/load_database_data.py); los proyectos se crean dinámicamente vía el flujo de generación, no por seed estático. Los tests de T105 usan dobles de prueba en vez de depender de un seed.
- [x] T012 [P] ~~Implement utility to validate UUID format~~ — N/A: el modelo `Project` usa id entero, no UUID (ver data-model.md). FastAPI ya valida el tipo del path param automáticamente (422 si no es entero); no se necesita utilidad adicional.

Phase 3 — US1: Get project by id (P1)

- [x] T100 [US1] Implement Project repository method: get_by_id(project_id: UUID) -> Project | None (core/catalog/repository.py)
- [x] T101 [US1] Implement service method: get_project_by_id(project_id: UUID, user: Optional[User]) -> ProjectDTO (core/catalog/service.py)
- [x] T102 [US1] Implement endpoint: GET /api/v1/projects/{project_id} -> uses service, returns Project contract (core/projects/api/projects_router.py)
- [x] T103 [US1] Implement authorization checks in service or middleware to enforce is_public and permissions (core/security/auth.py)
- [x] T104 [US1] Write unit tests for repository, service, and endpoint (tests/unit/test_catalog_project.py)
- [x] T105 [US1] Add integration tests for quickstart scenarios (tests/test_integration/test_get_project_by_id.py)

Phase 4 — Polish & Cross-cutting

- [x] T200 [P] Document API contract in docs and update openapi if needed (specs/006-get-project-by-id/contracts/project_contract.md) — actualizado para reflejar id entero (no UUID) y 422 en vez de 400
- [x] T201 [P] Audit logging for accesses to private projects (core/projects/api/projects_router.py, logger "audit.projects") — nota: se implementó en el router en vez de un core/security/logging.py dedicado, ya que no existía ese módulo
- [x] T202 [P] Add telemetry/metrics for endpoint usage (core/monitoring/metrics.py, expuesto en GET /api/health/metrics)

Dependencies

- T100 -> T101 -> T102 -> T104
- T010 -> T100
- T011 -> T104/T105

MVP recommendation: Complete Phase 3 tasks T100–T104 and basic tests (T104) to consider the feature deliverable. Exact test coverage can be expanded later.
