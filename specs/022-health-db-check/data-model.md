# Data Model: HU-22 Verificar conexión a base de datos en el endpoint de salud

**Branch**: `022-health-db-check` | **Date**: 2026-08-25

## Entidad modificada: Respuesta de `/api/health`

### Campo nuevo en la raíz

| Campo | Tipo | Descripción |
|---|---|---|
| `database` | `object` | Sección con estado de conectividad de la base de datos. |

### Sub-campos de `database`

| Campo | Tipo | Descripción |
|---|---|---|
| `connected` | `bool` | `true` si `SELECT 1` se ejecuta exitosamente; `false` si la conexión falla o la DB no está configurada. |
| `configured` | `bool` | `true` si hay configuración de base de datos (DATABASE_URL o variables individuales); `false` si no hay configuración. |

### Ejemplo de respuesta con DB conectada

```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "configured": true
  }
}
```

### Ejemplo de respuesta con DB caída

```json
{
  "status": "healthy",
  "database": {
    "connected": false,
    "configured": true
  }
}
```

### Ejemplo de respuesta sin DB configurada

```json
{
  "status": "healthy",
  "database": {
    "connected": false,
    "configured": false
  }
}
```

## DTOs modificados

### `diagnostics` response (endpoint `/api/health/diagnostics`)

Campo nuevo dentro del objeto `database`:

| Campo | Tipo | Descripción |
|---|---|---|
| `connected` | `bool` | `true` si la conexión a la base de datos es exitosa; `false` si falló. |
| `configured` | `bool` | `true` si hay configuración de base de datos; `false` si no. |

### Sin cambios en otros DTOs

`ProjectResponse`, `HistoryEntry`, `SharedProjectResponse`, `ai` section del diagnóstico no se modifican.

## Reglas de validación

- La verificación se ejecuta en cada petición al health check; no se cachea.
- El timeout de 5 segundos se aplica a la consulta `SELECT 1`.
- Si el engine no tiene una URL de base de datos configurada, se reporta "no configurado" sin intentar la conexión.

## Relaciones

Sin cambios. No hay tablas nuevas ni columnas nuevas.
