# API Contract: Get Project by ID

> Nota de implementación (2026-08-28): la spec original asumía IDs tipo
> UUID. La implementación real usa el `id` entero autoincremental del
> modelo `Project` (core/database/models.py), consistente con el resto del
> catálogo. Este contrato se actualizó para reflejar el comportamiento real
> en lugar del asumido inicialmente.

Endpoint: GET /api/v1/projects/{project_id}

Request
- Path parameter: project_id (integer, primary key of the `projects` table)
- Headers: optional Authorization: Bearer <token> when accessing private projects
  (current auth dependency is a stub that always returns "unauthenticated";
  see core/security/auth.py — real token parsing is a follow-up)

Responses
- 200 OK
  - Content-Type: application/json
  - Body (fields actually present on the `Project` model today):
    - id: integer
    - description: string | null
    - is_favorite: boolean
    - level: integer | null
    - owner_id: integer | null
    - owner_name: string | null
    - is_public: boolean
    - programming_language / tech / addon: related objects (see data-model.md)
  - Note: `name`, `slug`, `tags`, `metadata`, `created_at`, `updated_at` were
    in the original spec draft but do not exist on the current model. Add
    them to the model first if the consuming client needs them.

- 401 Unauthorized
  - When requesting a private project without authentication
- 403 Forbidden
  - When authenticated but lacking permission (not owner, no `ver_proyecto`
    permission) to view the private project
- 404 Not Found
  - When no project exists with the provided id
- 422 Unprocessable Entity
  - When project_id is not a valid integer (FastAPI's automatic path-param
    validation; this replaces the "400 Bad Request" originally assumed for
    UUID-format validation)

Observability
- Every access to a private project (granted or denied) is audit-logged via
  `audit.projects` (see core/projects/api/projects_router.py).
- Outcome counters (granted / not_found / unauthorized / forbidden) are
  exposed at GET /api/health/metrics for quick operational visibility.

Notes
- Fields marked should not expose internal secrets or sensitive configuration.
