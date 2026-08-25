# Contracts: HU-22 Verificar conexión a base de datos en el endpoint de salud

**Branch**: `022-health-db-check` | **Base**: `/api/v1`

## Endpoint modificado

### `GET /health`

El endpoint ahora incluye una sección `database` en la respuesta.

**Respuesta con DB conectada**:

```json
{
  "status": "healthy",
  "database": {
    "connected": true,
    "configured": true
  }
}
```

**Respuesta con DB caída**:

```json
{
  "status": "healthy",
  "database": {
    "connected": false,
    "configured": true
  }
}
```

**Respuesta sin DB configurada**:

```json
{
  "status": "healthy",
  "database": {
    "connected": false,
    "configured": false
  }
}
```

**Nota**: el código de estado es siempre `200`. El estado de la DB se indica en el cuerpo.

### `GET /health/diagnostics`

El campo `database` ahora incluye `connected` y `configured`.

**Respuesta con DB conectada**:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "ai": { "..." },
  "database": {
    "using_platform_url": true,
    "connected": true,
    "configured": true
  },
  "security": { "..." }
}
```

**Respuesta con DB caída**:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "ai": { "..." },
  "database": {
    "using_platform_url": true,
    "connected": false,
    "configured": true
  },
  "security": { "..." }
}
```

## Sin nuevos endpoints

No se crean endpoints nuevos. La verificación de DB se añade a los endpoints existentes.

## Contrato de comportamiento

| Escenario | `connected` | `configured` | HTTP Status |
|---|---|---|---|
| DB accesible | `true` | `true` | 200 |
| DB caída o timeout | `false` | `true` | 200 |
| DB no configurada | `false` | `false` | 200 |
