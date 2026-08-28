# Contract: Estadísticas de proyectos generados

## Endpoint

GET /api/v1/ensemble_project/statistics

## Purpose

Devuelve el ranking de lenguajes y tecnologías más frecuentes en el historial de ideas generadas por la aplicación.

## Request

- Query params:
  - `limit`: entero opcional, por defecto 10, rango 1-20

## Response

```json
{
  "total_projects": 42,
  "generated_at": "2026-08-28T10:15:00Z",
  "items": [
    {
      "category": "programming_language",
      "label": "Python",
      "count": 18,
      "share": 0.43,
      "rank": 1
    },
    {
      "category": "technology",
      "label": "FastAPI",
      "count": 12,
      "share": 0.29,
      "rank": 2
    }
  ]
}
```

## Error handling

- Si no hay datos, la API responde con `200 OK` y un array vacío o un objeto con cero elementos, nunca con error de usuario.
- Si el parámetro `limit` está fuera de rango, responde con `422` por validación del FastAPI.

## Observations

- El servicio debe devolver un resumen ordenado por frecuencia.
- La respuesta es solo de lectura y no modifica el historial ni el estado de los proyectos.
