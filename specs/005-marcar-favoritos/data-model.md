# Data Model: Marcar proyectos generados como favoritos

## Entidades

### `Project` (existente, `core/database/models.py`, tabla `projects`)

Se modifica agregando un único campo. Sin cambios en sus relaciones ni en el resto de columnas.

| Campo | Tipo | Restricciones | Notas |
|---|---|---|---|
| `is_favorite` | `bool` | `NOT NULL`, `default=False`, `server_default="false"` | Nuevo. `true` mientras el usuario lo mantenga marcado como favorito. |
| `level` | `Optional[int]` | Sin restricción de rango a nivel de columna (ya validado en el DTO de entrada al generarse) | Nuevo. Antes no se persistía en ningún lado; requerido para que `/history` y `/favorites` puedan devolver el nivel (FR-009). `NULL` en filas generadas antes de esta migración. |

Reglas de negocio (derivadas de FR-001 a FR-006 de la spec):

- Un `Project` sin favorito marcado tiene `is_favorite = False` (estado por defecto tras generarse).
- Marcar (`is_favorite = True`) sobre un proyecto ya marcado es un no-op exitoso (idempotente, FR-005).
- Desmarcar (`is_favorite = False`) sobre un proyecto no marcado es un no-op exitoso (idempotente, FR-006).
- No existen estados intermedios: solo `True`/`False` (ver Assumptions de la spec).

### Sin entidades nuevas

No se introduce una tabla `Favorite`/`project_favorites`: ver `research.md`, Decisión
"dónde vive el estado de favorito". El "Favorito" descrito en la spec (`Key Entities`) se
implementa como un atributo de `Project`, no como una fila independiente.

## DTOs afectados (`core/ensemble_project/api/ensemble_project_models.py`)

### `ProjectResponse` (modificado)

Respuesta de `generate_project_by_value`, `generate_project_by_level` y
`generate_project_totally_random`.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | `int` | **Nuevo.** Identificador persistido, requerido para poder marcarlo como favorito sin una consulta adicional (ver D-02 en `plan.md`). |
| `favorite` | `bool` | **Nuevo.** Refleja `Project.is_favorite`. Siempre `false` justo tras generarse. |
| `programming_language` | `str` | Sin cambios. |
| `technologies` | `str` | Sin cambios. |
| `addons` | `str` | Sin cambios. |
| `extras` | `list[Extras]` | Sin cambios. |
| `level` | `int` | Sin cambios. |
| `description` | `str` | Sin cambios. |

### `HistoryEntry` (modificado)

Respuesta de `GET /history` y del nuevo `GET /favorites`.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | `int` | Sin cambios. |
| `favorite` | `bool` | **Nuevo.** Refleja `Project.is_favorite`. En `/favorites` siempre es `true`; en `/history` puede ser `true` o `false`. |
| `level` | `int \| None` | **Nuevo.** Refleja `Project.level`. `None` en proyectos generados antes de esta migración (edge case: modo degradado/legado, ver Edge Cases de la spec). |
| `extras` | `list[Extras]` | **Nuevo.** Construido a partir de la relación ORM `Project.extras` (FR-009). Lista vacía si el proyecto no tiene extras. |
| `programming_language` | `str` | Sin cambios. |
| `technologies` | `str` | Sin cambios. |
| `addons` | `str` | Sin cambios. |
| `description` | `str` | Sin cambios. |

## Transiciones de estado

```text
[recién generado] --marcar favorito--> [favorito]
[favorito]        --desmarcar-------->  [no favorito]
[no favorito]     --marcar favorito--> [favorito]
[favorito]        --marcar de nuevo--> [favorito]      (idempotente, FR-005)
[no favorito]     --desmarcar de nuevo--> [no favorito] (idempotente, FR-006)
```

Un `project_id` que no existe en ninguna transición devuelve un error de dominio
(`LookupError` en el servicio -> `404` en el router) y no crea ni modifica ninguna fila (FR-008).
