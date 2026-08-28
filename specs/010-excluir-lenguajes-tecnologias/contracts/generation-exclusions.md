# Contrato: generación con exclusiones

## Endpoint

Los endpoints existentes de generación aceptan una lista opcional de nombres excluidos:

- `POST /api/v1/ensemble_project/generate_project_by_value`
- `POST /api/v1/ensemble_project/generate_project_by_level`

No se crea un endpoint de preferencias: la preferencia vive en el navegador y se envía en cada solicitud de generación.

## Request shape

### `generate_project_by_value`

```json
{
  "programming_language": "",
  "technologies": "",
  "addons": "",
  "extras": [],
  "excluded": ["Rust", "Docker"],
  "level": { "level": 3 }
}
```

### `generate_project_by_level`

```json
{
  "level": 3,
  "excluded": ["Rust", "Docker"]
}
```

`excluded` is optional for backward compatibility and defaults to an empty list. Values are names from the programming-language or technology catalogs. Addon names are ignored for exclusion purposes.

## Behavior

- Valid excluded names are matched case-insensitively after trimming whitespace.
- Duplicate, blank, unknown, or addon entries are ignored.
- Valid exclusions apply to the main result and to every generated extra.
- Addons remain eligible in the main result and extras.
- If any required language or technology catalog has no eligible value, the request must not produce a forbidden result. The UI disables the spin action before sending the request; the service returns a controlled validation error if a direct client bypasses the UI.
- With an omitted or empty `excluded` list, generation preserves the existing behavior.

## Response compatibility

The response shape remains the existing `ProjectResponse`. No exclusion preference is persisted in the database and no new response field is required.
