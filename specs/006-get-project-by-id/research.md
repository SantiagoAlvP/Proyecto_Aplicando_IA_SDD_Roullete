# Research for get-project-by-id

Decision: Authorization policy = Híbrido (public/private)
Rationale: Balances ease-of-use for public content with protection of private data. Matches existing is_public field on Project entity.
Alternatives considered:
- Public-only: Simplest but risks exposing private data.
- Owner-only: Strong privacy but may be too restrictive for shared/private teams.

Decision: Identifier format = integer (existing DB primary key)
Rationale: The current system and Project model use an integer autoincrement primary key. To avoid breaking changes and extra migration risk, the spec adopts the existing integer id as canonical for the API. If a migration to UUIDs is desired in the future, it must be planned explicitly with a backfill strategy.
Alternatives considered:
- UUIDs: avoid guessability but require schema migration, backfill, and broader code changes.

Decision: Contract path = /api/v1/projects/{project_id}
Rationale: Consistent with existing router structure that mounts under /api/v1.
Alternatives considered: /api/v1/projects/by-id/{id} (redundant)
