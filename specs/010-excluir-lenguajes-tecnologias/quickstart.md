# Quickstart: Excluir lenguajes y tecnologías antes de girar

## Goal

Verify that the user can hide generic or undesired technologies from the catalog and keep those settings until they are explicitly removed.

## Steps

1. Open the app and wait for the catalog to load.
2. Select one or more values in the new exclusions panel.
3. Confirm that the hidden technologies are no longer present in the available reel options.
4. Press “¡Girar!” and verify the generated project never contains any excluded technology.
5. Refresh the page and confirm that the same exclusions remain active.
6. Remove one or all exclusions and verify that the full catalog is restored.
7. Optionally send a direct generation request with every language or technology excluded and verify that the API returns `422` without generating a forbidden project.

## Expected outcomes

- Excluded values disappear from the possible random choices.
- No generated project includes a blocked language or stack.
- Unblocking a value restores it immediately for future spins.
- Empty exclusions keep the old behavior unchanged.
- A direct client that exhausts a required category receives a controlled `422` response.

## Automated verification

- `uv run pytest -q`: 260 passed, 3 deselected.
- `uv run ruff check`: passed.
- `uv run ruff format --check`: passed.
- `uv run ty check`: passed.
- `cd frontend && npm run build`: passed.

The browser-only checks for persistence after reload, removing one exclusion, and clearing all exclusions remain manual because the project has no frontend test runner configured.
