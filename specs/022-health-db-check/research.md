# Research: HU-22 Verificar conexión a base de datos en el endpoint de salud

**Branch**: `022-health-db-check` | **Date**: 2026-08-25

## D-01 — Verificación mediante SELECT 1 con timeout

- **Decision**: la verificación de conectividad usa `SELECT 1` ejecutado contra el engine de SQLAlchemy existente, con un timeout de 5 segundos via `execution_options(timeout=5)`.
- **Rationale**: `SELECT 1` es la consulta más ligera posible para confirmar que la conexión TCP y el servidor PostgreSQL están operativos. No depende de tablas específicas ni de datos existentes (FR-004). El timeout de 5 segundos (FR-005) evita bloquear la plataforma de hosting.
- **Alternatives considered**:
  - *`SELECT pg_ping()`*: más semántico pero requiere extensión pg; `SELECT 1` es universal.
  - *Conexión dedicada*: más overhead; se reutiliza el engine existente (Assumption).
  - *Cache del resultado*: introduce complejidad innecesaria; el health check se invoca con poca frecuencia.

## D-02 — Inyección del engine via Depends

- **Decision**: se crea una función `get_engine()` que retorna el engine de SQLAlchemy, y se inyecta en los endpoints de health via `Depends(get_engine)`.
- **Rationale**: sigue el patrón existente de `get_settings()` en el mismo archivo. El router no instancia el engine directamente; lo recibe por dependencia (Constitución II).
- **Alternatives considered**:
  - *Importar `engine` directamente*: viola la separación de capas y dificulta el testing.
  - *Pasarlo como parámetro de path*: no aplica; es un singleton de la app.

## D-03 — Health siempre devuelve 200 (tras aclaración)

- **Decision**: `/api/health` siempre devuelve `200` con `{"status": "healthy", "database": {"connected": true/false, "configured": true/false}}`.
- **Rationale**: la plataforma de hosting (Railway) usa `/api/health` como liveness probe. Un `503` causaría reinicios innecesarios. El estado de la DB se comunica en el cuerpo de la respuesta, que es suficiente para que el responsable detecte el problema (Clarity Session 2026-08-25, Option B).
- **Alternatives considered**:
  - *503 cuando DB caída*: causa reinicios en Railway; rompe compatibilidad con CI.
  - *200 siempre, sin campo database*: no resuelve el problema del usuario.

## D-04 — Distinción "no configurado" vs "caído"

- **Decision**: si `DATABASE_URL` no está definida y las variables de DB individuales no están configuradas, se reporta `"configured": false, "connected": false`. Si están configuradas pero la conexión falla, se reporta `"configured": true, "connected": false`.
- **Rationale**: FR-007 exige no generar falsas alertas en entornos de desarrollo sin Postgres. La distinción permite al responsable saber si el problema es configuración o conectividad.
- **Alternatives considered**:
  - *Un solo campo `connected`*: no permite distinguir configuración de fallo.
  - *Campo `status` con valores enum*: más complejo; un booleano `configured` + `connected` es suficiente.
