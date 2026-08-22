# Contract: API de favoritos

Todas las rutas cuelgan del prefijo existente `/api/v1/ensemble_project` (ver
`core/routers.py`). No se crea un router nuevo: se agregan operaciones al router
`ensemble_project` ya existente.

## `PUT /api/v1/ensemble_project/{project_id}/favorite`

Marca un proyecto como favorito. Idempotente (FR-005).

**Path params**

| Nombre | Tipo | Restricción |
|---|---|---|
| `project_id` | entero | `> 0` |

**Respuesta 200 OK** — `HistoryEntry` con `favorite: true`

```json
{
  "id": 42,
  "programming_language": "Rust",
  "technologies": "gRPC",
  "addons": "CLI interactiva",
  "level": 3,
  "extras": [{"programming_language": null, "technologies": "Tokio", "addons": null}],
  "description": "...",
  "favorite": true
}
```

**Respuesta 404 Not Found** — `project_id` inexistente (FR-008)

```json
{ "detail": "Project 42 not found." }
```

**Acceptance mapping**: US1 (spec), escenarios 1, 2, 3 y 4.

---

## `DELETE /api/v1/ensemble_project/{project_id}/favorite`

Desmarca un proyecto como favorito. Idempotente (FR-006).

**Path params**: igual que arriba.

**Respuesta 200 OK** — `HistoryEntry` con `favorite: false`

**Respuesta 404 Not Found** — `project_id` inexistente, mismo formato que arriba.

**Acceptance mapping**: US3 (spec), escenarios 1 y 2.

---

## `GET /api/v1/ensemble_project/favorites`

Lista los proyectos actualmente marcados como favoritos, más recientes primero.

**Query params**

| Nombre | Tipo | Restricción | Default |
|---|---|---|---|
| `limit` | entero | `ge=1, le=50` | `10` |

**Respuesta 200 OK** — `list[HistoryEntry]`, todos con `favorite: true`

```json
[
  {
    "id": 42,
    "programming_language": "Rust",
    "technologies": "gRPC",
    "addons": "CLI interactiva",
    "level": 3,
    "extras": [{"programming_language": null, "technologies": "Tokio", "addons": null}],
    "description": "...",
    "favorite": true
  }
]
```

Lista vacía (`[]`) cuando no hay favoritos — nunca un error (FR-004, Edge Cases de la spec).

**Respuesta 422 Unprocessable Entity** — `limit` fuera de rango, mismo formato que `/history`.

**Acceptance mapping**: US2 (spec), escenarios 1, 2 y 3.

---

## Cambios en endpoints existentes (no nuevos, pero con contrato modificado)

### `POST /generate_project_by_value` · `/generate_project_by_level` · `/generate_project_totally_random`

`ProjectResponse` gana dos campos: `id` (int) y `favorite` (bool, siempre `false` en la
respuesta de una generación nueva). Ningún campo existente cambia de tipo ni de nombre.

### `GET /history`

`HistoryEntry` gana tres campos: `favorite` (bool, estado real de cada proyecto), `level`
(`int | None`, `None` en proyectos generados antes de esta migración) y `extras`
(`list[Extras]`, leído de `project_extras`). Antes de esta funcionalidad, `/history` nunca
había expuesto nivel ni extras.
