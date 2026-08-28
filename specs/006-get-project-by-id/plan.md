# Implementation Plan: Get Project by ID

Technical context

- This feature exposes a read-only resource "Project" identified by the database integer primary key (id). The API surface will follow the repository's /api/v1 prefix and be reachable at GET /api/v1/projects/{project_id}.
- Existing code contains a catalog module (core/catalog) housing repository and service responsibilities; routers for catalog live under /catalog. To keep resources discoverable and avoid mixing concerns, a dedicated projects router will be added under core/projects/api/projects_router.py and registered in core/routers.py.
- Authorization: projects with is_public=true are accessible without auth; is_public=false requires authentication and authorization (owner or permission 'ver_proyecto'). Auth logic will live in core/security/auth.py and be invoked by the service layer (service raises domain exceptions) or by a small helper dependency injected into the endpoint.

Architecture & key decisions

- Router: create core/projects/api/projects_router.py with APIRouter(prefix='/projects', tags=['projects']). Register via core/routers.configure_routers alongside existing catalog router.
- Repository/Service: reuse core/catalog/catalog_repository.py and core/catalog/catalog_service.py if they already implement Project operations; otherwise extend them with get_by_id. Repository signature: get_by_id(db_session, project_id: int) -> Optional[ProjectModel]. Service returns DTOs; it performs business authorization checks by calling auth helpers or raising domain exceptions.
- Auth module: create core/security/auth.py implementing token->user resolution and permission check helpers: is_owner(user, project) and has_permission(user, 'ver_proyecto'). Service uses these helpers; routers translate domain exceptions into HTTP 401/403 via existing core.security.errors handlers.
- Validation: enforce project_id is an integer (DB primary key). FastAPI's path-parameter typing validates the type and returns 422 for invalid values, so a custom UUID validator is not required. Document this behavior in the contract and tests.

Data & migrations

- Data-model: assume Project model exists in core/database/models or equivalent. Ensure fields: id (integer autoincrement primary key), name, description, slug (nullable), owner_id, owner_name, is_public (boolean), tags, metadata, created_at, updated_at.
- If is_public column missing, add migration (alembic) and seed data update. Migration tasks belong to implementation phase only if necessary.

Testing strategy

- Follow constitution: tests before merging. Unit tests for repository, service and router; contract test for response shape (200, 400, 401/403, 404); integration tests using test DB seed entries (data/data.yaml). Use test doubles for external dependencies.
- Quickstart.md contains curl examples for manual verification.

Gates & checks

- Must pass: uv run pytest -q, uv run ruff check --fix optional in pre-commit, uv run ty check.
- No secrets in repository; validate .env handling.

Complexity tracking

- Creating a new router (core/projects) and auth module is low complexity but changes multiple files: core/routers.py, core/projects/api/projects_router.py, core/security/auth.py, core/catalog/catalog_service.py (augmentation). Document rationale and alternative (reuse /catalog route) in this plan.

Phases & mapping to tasks

- Phase 1 (Foundational): Ensure Project model fields (is_public) are present, and confirm path-param validation relies on FastAPI typing (no custom UUID helper). Add DB seed entries if needed for integration tests.
- Phase 2 (Implementation): Repository method get_by_id, service method get_project_by_id, auth helpers, router endpoint GET /api/v1/projects/{project_id}.
- Phase 3 (Tests & polish): Unit tests, integration tests, contract update, logging, telemetry.

Files to create/modify

- Create: core/projects/api/projects_router.py, core/security/auth.py, core/utils/validation.py (if missing)
- Modify: core/routers.py (register new router), core/catalog/catalog_service.py (add service method or provide adapter), data/data.yaml (test seeds), specs/006-get-project-by-id/tasks.md (align paths)

Rollback plan

- If auth integration causes regressions, revert by disabling auth check to return 403 for private projects and open a follow-up ticket to harden security. Any revert must keep tests green.

Notes

- Decision: create projects router (keeps resource separation). Alternative (reuse /catalog) is acceptable if team prefers a single module for related resources; document if chosen.
