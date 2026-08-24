# Data Model: HU-20 Compartir proyectos mediante enlace público

**Branch**: `020-compartir-enlace-publico` | **Date**: 2026-08-23

## Entidad modificada: `Project` (tabla `projects`)

Campos existentes sin cambios: `id`, `description`, `programming_language_id`,
`project_tech_id`, `project_addon_id` y relaciones.

### Columnas nuevas

| Campo | Tipo | Reglas |
|---|---|---|
| `share_token` | `str` | Único, indexado, no nulo. Generado con `secrets.token_urlsafe(12)` (~16 chars `[A-Za-z0-9_-]`). Se asigna al crear el proyecto y por backfill en la migración para filas previas (FR-007). Nunca se regenera: es la identidad pública permanente (FR-006). |
| `level` | `int \| None` | Anulable; para filas nuevas `1..5`. Las filas legadas quedan `NULL` porque el nivel nunca se persistió. La vista muestra texto neutral cuando es `None`. |
| `created_at` | `datetime` | No nulo con valor por defecto en el modelo (`datetime.now(timezone.utc)`); el backfill de filas legadas usa la fecha de la migración (supuesto documentado: no había registro previo). |

### Transiciones de estado

Ninguna nueva: el proyecto sigue siendo inmutable tras crearse y solo lectura vía enlace.
El token no tiene ciclo de vida propio (no expira, no se revoca en esta iteración).

## DTOs (contratos espejo en `frontend/src/types.ts`)

### `SharedProjectResponse` (nuevo — vista pública)

| Campo | Tipo | Notas |
|---|---|---|
| `share_token` | `str` | Eco del token solicitado |
| `programming_language` | `str` | Nombre legible; `"Unknown"` si faltara la fila de catálogo (patrón `_name_of`) |
| `technologies` | `str` | Ídem |
| `addons` | `str` | Ídem |
| `extras` | `list[Extras]` | Extras persistidos del proyecto |
| `level` | `int \| None` | `null` en filas legadas |
| `description` | `str` | Texto de relleno legible si la fila legada no tenía descripción |

### `HistoryEntry` (ampliado)

Añade `share_token: str` y `level: int | None`. Sirve a la Historia 2 (botón compartir
por entrada) sin exponer el ID secuencial interno como identidad pública.

### `ProjectResponse` (ampliado)

Añade `share_token: str`. La respuesta de generación lleva desde el primer momento el
token que la UI usa para ofrecer "Compartir" sobre el resultado recién creado.

## Consultas nuevas

- `ProjectCRUD.get_by_share_token(session, token) -> Project | None`
  (búsqueda exacta por índice único).
- `save_project` persiste `level` junto al resto del proyecto.

## Reglas de validación en el borde HTTP

- Path param `share_token`: `min_length=10`, `max_length=64`, `pattern=^[A-Za-z0-9_-]+$`.
  Todo lo que no cumpla ni llega a la base de datos (Principio IV).

## Relaciones

Sin cambios: los extras siguen colgando de `projects.id`; el token no crea tabla nueva
(YAGNI — una columna alcanza para resolver "enlace → proyecto").
