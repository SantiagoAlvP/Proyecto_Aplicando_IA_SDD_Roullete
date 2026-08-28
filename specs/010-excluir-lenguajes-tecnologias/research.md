# Research: Excluir lenguajes y tecnologías antes de girar

## Summary

The repository already has a single catalog and a single generation flow. The new requirement fits best as a small extension of the existing reel-selection flow instead of a separate feature domain.

## Findings

### 1) Current source of truth

The app gets catalog data from `CatalogRepository` and the generation flow uses it in `ProjectGeneratorService._pick_random_base()` and `_pick_random_extras()`. The user-facing slot machine in `frontend/src/App.tsx` chooses values from the same catalog and then posts the fixed values to the generation endpoint.

### 2) Best-fit persistence model

The project has no user identity, authentication, or profiles. Since the requirement is fundamentally personal preference (“never show technologies I do not want to learn”), localStorage on the browser is the least complex and still satisfies the persistence requirement.

### 3) Filtering strategy

The most reliable approach is to filter the candidate list before random selection and before the user is allowed to lock a value. This prevents a forbidden item from ever being chosen and ensures the UI and the generation logic remain aligned.

### 4) Backward compatibility

If the catalog is empty, or the exclusion list contains invalid names, the feature should degrade gracefully: the app continues to work with the default catalog and no additional error screen is required.

## Decision

Implement the exclusion feature as a front-end persistence layer plus a generation filter layer that strips excluded values from the available catalog options before each spin. Backend validation remains strict but tolerant: it accepts the final values but ignores empty or invalid exclusions instead of breaking the request.
