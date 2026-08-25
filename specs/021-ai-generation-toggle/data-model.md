# Data Model: HU-21 Desactivar generación por IA mediante variable de entorno

**Branch**: `021-ai-generation-toggle` | **Date**: 2026-08-25

## Entidad modificada: `AppSettings` (configuración en runtime)

Campos existentes sin cambios: todos los campos actuales de `AppSettings`.

### Campo nuevo

| Campo | Tipo | Default | Reglas |
|---|---|---|---|
| `AI_GENERATION_ENABLED` | `bool` | `True` | Leído de variable de entorno. Cualquier valor que no sea `true`/`1`/`on` (case-insensitive) se interpreta como `False`. Ausencia de la variable equivale a `True`. |

### Property nueva

| Property | Tipo | Descripción |
|---|---|---|
| `ai_generation_enabled` | `bool` | Derivado de `AI_GENERATION_ENABLED`. Retorna `True` solo si el valor parseado es truthy. Se evalúa en cada petición (no se cachea). |

### Transiciones de estado

El toggle no tiene ciclo de vida propio. Su valor se determina en cada petición
a partir de la variable de entorno. No se persiste en base de datos.

## DTOs modificados

### `diagnostics` response (endpoint `/api/health/diagnostics`)

Campo nuevo dentro del objeto `ai`:

| Campo | Tipo | Descripción |
|---|---|---|
| `ai_generation_enabled` | `bool` | `True` si la generación por IA está activa; `False` si el toggle la desactiva. |

### Sin cambios en otros DTOs

`ProjectResponse`, `HistoryEntry`, `SharedProjectResponse` no se modifican.
La descripción de respaldo tiene la misma forma que la generada por IA.

## Reglas de validación

- El parsing de `AI_GENERATION_ENABLED` lo maneja pydantic-settings automáticamente.
- No hay restricciones de formato adicionales; el campo es binario.
- No se requiere validación en el borde HTTP porque el toggle es interno del servidor.

## Relaciones

Sin cambios. No hay tablas nuevas ni columnas nuevas.
