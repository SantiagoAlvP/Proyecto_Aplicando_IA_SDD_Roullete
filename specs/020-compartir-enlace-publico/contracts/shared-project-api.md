# Contracts: API de proyecto compartido

**Branch**: `020-compartir-enlace-publico` | **Base**: `/api/v1`

## Endpoint nuevo

### `GET /ensemble_project/shared/{share_token}`

Vista pública de solo lectura de un proyecto (FR-001–FR-003). Sin autenticación.

**Path param**

| Nombre | Restricción |
|---|---|
| `share_token` | `min_length=10`, `max_length=64`, patrón `^[A-Za-z0-9_-]+$` |

**Respuestas**

| Status | Cuerpo | Cuándo |
|---|---|---|
| `200` | `SharedProjectResponse` | Token existente |
| `404` | `{"detail": "Proyecto no disponible."}` | Token bien formado pero inexistente. Mensaje neutro, sin detalles internos (FR-008, Principio IV) |
| `422` | Error de validación FastAPI | Parámetro que viola las cotas |

**Ejemplo 200**

```json
{
  "share_token": "kX9m2LpQ_vR4wBn7",
  "programming_language": "Python",
  "technologies": "FastAPI",
  "addons": "PostgreSQL",
  "extras": [
    {"programming_language": "SQL", "technologies": null, "addons": "Docker"}
  ],
  "level": 3,
  "description": "Construye una API REST con autenticación JWT y migraciones versionadas."
}
```

Filas legadas: `level: null` y descripción con texto de relleno legible si estaba vacía.

## Esquemas modificados

### `HistoryEntry` — `GET /ensemble_project/history`

Campos nuevos: `"share_token": str`, `"level": int | null`.

```json
{
  "id": 42,
  "share_token": "kX9m2LpQ_vR4wBn7",
  "programming_language": "Python",
  "technologies": "FastAPI",
  "addons": "PostgreSQL",
  "description": "...",
  "level": 3
}
```

### `ProjectResponse` — `POST /generate_project_*`

Campo nuevo: `"share_token": str`. Mismo valor queda persistido; el enlace público del
resultado recién generado es `{origin}/proyecto/{share_token}`.

## Contrato de UI (SPA)

| Ruta | Comportamiento |
|---|---|
| `/proyecto/{token}` | Vista pública de solo lectura: combinación, nivel, extras, descripción y CTA hacia la máquina (FR-009). Token con formato inválido → página amigable sin llamar a la API |
| `/` | Máquina tragamonedas + historial, cada uno con acción "Compartir" (FR-004) |
| cualquier otra | Shell SPA actual (sin cambios) |

Errores de red o `404` en la vista pública → misma página amigable "Proyecto no
disponible" con salida hacia `/` (Historia 3).
