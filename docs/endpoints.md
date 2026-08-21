# Endpoints

Base pública: `https://TU-DOMINIO.up.railway.app`
Documentación interactiva: `/api/docs` (Swagger) · `/api/redocs` (ReDoc)

Todas las respuestas incluyen `X-Request-ID` y las cabeceras de seguridad
descritas en `docs/security.md`.

## Salud

| Método | Ruta | Descripción | Notas |
|---|---|---|---|
| GET | `/api/health` | Verificación de vida | Exento del límite de tasa; no consulta la base de datos |

## Catálogo

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/catalog/programming-languages` | Lista completa de lenguajes |
| GET | `/api/v1/catalog/programming-languages/random` | Un lenguaje al azar |
| GET | `/api/v1/catalog/technologies` | Lista completa de tecnologías |
| GET | `/api/v1/catalog/technologies/random` | Una tecnología al azar |
| GET | `/api/v1/catalog/addons` | Lista completa de addons |
| GET | `/api/v1/catalog/addons/random` | Un addon al azar |

Los endpoints `/random` devuelven `null` (no un `500`) cuando la tabla está vacía.

## Generación de proyectos

| Método | Ruta | Descripción | Cuerpo |
|---|---|---|---|
| POST | `/api/v1/ensemble_project/generate_project_totally_random` | Proyecto completamente aleatorio | — |
| POST | `/api/v1/ensemble_project/generate_project_by_level` | Proyecto por dificultad | `{"level": 1..5}` |
| POST | `/api/v1/ensemble_project/generate_project_by_value` | Proyecto con valores fijados | ver abajo |
| GET | `/api/v1/ensemble_project/history?limit=10` | Últimos proyectos generados | `limit` entre 1 y 50 |

Cuerpo de `generate_project_by_value` — un campo vacío significa "al azar":

```json
{
  "programming_language": "Rust",
  "technologies": "",
  "addons": "",
  "extras": [],
  "level": { "level": 3 }
}
```

## Códigos de estado

| Código | Cuándo |
|---|---|
| `200` | Consulta correcta |
| `201` | Proyecto generado y persistido |
| `413` | Cuerpo de la petición mayor a `MAX_BODY_BYTES` (64 KiB por defecto) |
| `422` | Entrada inválida, o combinación técnicamente inviable según la IA |
| `429` | Límite de tasa superado. Incluye `Retry-After` |
| `500` | Error interno. Devuelve un `request_id`, nunca un stack trace |

## Formato de error

```json
{
  "detail": "Invalid request.",
  "errors": [{ "field": "level", "message": "Input should be less than or equal to 5" }],
  "request_id": "32b807635994"
}
```

El `request_id` es el que hay que citar para rastrear el incidente en los logs.
