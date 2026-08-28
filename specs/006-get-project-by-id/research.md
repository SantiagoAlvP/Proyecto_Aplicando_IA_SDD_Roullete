# Research for get-project-by-id

Decision: Authorization policy = Híbrido (public/private)
Rationale: Balances ease-of-use for public content with protection of private data. Matches existing is_public field on Project entity.
Alternatives considered:
- Public-only: Simplest but risks exposing private data.
- Owner-only: Strong privacy but may be too restrictive for shared/private teams.

Decision: Identifier format = UUID
Rationale: UUIDs avoid guessing and are consistent with other services in the repository. If the system uses integer ids, convert validation rules accordingly.
Alternatives considered:
- Integer IDs: simpler but can be enumerable and expose data by sequential ids.

Decision: Contract path = /api/v1/projects/{project_id}
Rationale: Consistent with existing router structure that mounts under /api/v1.
Alternatives considered: /api/v1/projects/by-id/{id} (redundant)
