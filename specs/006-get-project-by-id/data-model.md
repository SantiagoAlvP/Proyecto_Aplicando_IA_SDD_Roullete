# Data model for get-project-by-id

Entities

- Project
  - id: UUID (string)
  - name: string
  - description: string
  - slug: string (nullable)
  - owner_id: UUID (string)
  - owner_name: string
  - is_public: boolean
  - tags: array[string]
  - metadata: object (free-form JSON)
  - created_at: timestamp
  - updated_at: timestamp

Validation rules

- id: must be a valid UUID
- name: non-empty, max 100 chars
- description: max 500 chars

Notes

- Assumed id is UUID for consistency; adapt if the system uses integer ids.
