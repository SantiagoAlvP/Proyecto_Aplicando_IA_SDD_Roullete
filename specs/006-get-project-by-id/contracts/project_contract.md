# API Contract: Get Project by ID

Endpoint: GET /api/v1/projects/{project_id}

Request
- Path parameter: project_id (UUID)
- Headers: optional Authorization: Bearer <token> when accessing private projects

Responses
- 200 OK
  - Content-Type: application/json
  - Body:
    - id: string (UUID)
    - name: string
    - description: string
    - slug: string | null
    - owner: object
      - id: string
      - name: string
    - is_public: boolean
    - tags: array[string]
    - metadata: object
    - created_at: string (RFC3339 timestamp)
    - updated_at: string (RFC3339 timestamp)

- 400 Bad Request
  - Invalid id format
- 401 Unauthorized
  - When requesting a private project without authentication
- 403 Forbidden
  - When authenticated but lacking permission to view the private project
- 404 Not Found
  - When no project exists with provided id

Notes
- Fields marked should not expose internal secrets or sensitive configuration.
