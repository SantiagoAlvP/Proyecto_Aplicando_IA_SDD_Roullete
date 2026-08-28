# Data Model: Exclusion preferences

## Core concept

`ExcludedCatalogChoice`

- `category`: one of `programming_language` or `technologies`
- `name`: canonical catalog value (for example: `Python`, `FastAPI`, `Docker`)

## UI state model

```ts
interface ExcludedCatalogChoice {
  category: "programming_language" | "technologies";
  name: string;
}
```

## Persistence model

The list is stored in the browser as an array under a localStorage key, for example:

```ts
const STORAGE_KEY = "project-jackpot:excluded-catalog";
```

The runtime data structure is intentionally tiny because it is a user preference, not a business entity with its own lifecycle.

## Behavioral rules

- The list is global to the current browser profile and survives reload.
- Duplicate values are deduplicated by `category + name`.
- Invalid or missing values are ignored when filtering catalog options.
- Addons are never added to this list and remain eligible.
- Clearing the list restores the original, unfiltered catalog.
