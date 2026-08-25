# Feature Specification: Verificar conexión a base de datos en el endpoint de salud

**Feature Branch**: `022-health-db-check`

**Created**: 2026-08-25

**Status**: En especificación

**Input**: "Como responsable del servicio, quiero que el endpoint de salud verifique también la conexión a la base de datos, para detectar una base caída antes de que falle una petición de usuario."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Detectar base de datos caída en el health check (Priority: P1)

El responsable del servicio despliega una nueva versión y la plataforma de hosting
confirma que `/api/health` responde `200`. Sin embargo, la base de datos subyacente
está caída y cada petición de usuario que intenta leer o escribir falla con error 500.
El responsable necesitaba saber que la base estaba caída **antes** de que los usuarios
reportaran errores.

**Why this priority**: sin verificación de la base de datos, el health check reporta
"saludable" cuando el servicio está funcionalmente degradado. Esta es la protección
mínima para detectar una falla común.

**Independent Test**: simular una base de datos no accesible y comprobar que el
endpoint de salud indica que la base de datos no está conectada.

**Acceptance Scenarios**:

1. **Given** la base de datos está caída o no accesible, **When** se consulta `/api/health`, **Then** el endpoint responde `200` con `{"status": "healthy", "database": {"connected": false}}`, preservando la compatibilidad con la plataforma de hosting.
2. **Given** la base de datos está funcionando correctamente, **When** se consulta `/api/health`, **Then** el endpoint responde `200` con `{"status": "healthy"}` y la sección de base de datos indica que está conectada.
3. **Given** la base de datos está caída, **When** se consulta `/api/health/diagnostics`, **Then** la sección `database` incluye un campo que indica que la conexión falló, sin exponer detalles técnicos como rutas del servidor o mensajes de error de SQL.

---

### User Story 2 — Diagnóstico detallado de la base de datos (Priority: P2)

El responsable del servicio quiere verificar el estado de la base de datos sin causar
una alerta en la plataforma de hosting. Consulta `/api/health/diagnostics` y ve si la
base está conectada, si se está usando una URL de plataforma, y si la conexión es
estable.

**Why this priority**: el diagnóstico detallado permite investigar problemas sin
afectar el despliegue ni las alertas de CI.

**Independent Test**: consultar `/api/health/diagnostics` con la base de datos
funcionando y caída, y verificar que el campo `database.connected` refleja el estado
correcto.

**Acceptance Scenarios**:

1. **Given** la base de datos está funcionando, **When** se consulta `/api/health/diagnostics`, **Then** la sección `database` incluye `"connected": true`.
2. **Given** la base de datos está caída, **When** se consulta `/api/health/diagnostics`, **Then** la sección `database` incluye `"connected": false`.
3. **Given** la base de datos está funcionando, **When** se consulta `/api/health/diagnostics`, **Then** la sección `database` sigue incluyendo `"using_platform_url"` (comportamiento existente sin cambios).

---

### Edge Cases

- **La base de datos tarda mucho en responder** → el health check debe tener un timeout corto (no más de 5 segundos) para no bloquear la plataforma de hosting. Si el timeout se alcanza, se reporta como "no conectada".
- **La base de datos está configurada pero el servidor no está arrancado** → se reporta como "no conectada".
- **No hay configuración de base de datos** (DATABASE_URL no definida y variables de entorno de DB no configuradas) → se reporta como "no configurada" (distinguir de "caída").
- **La verificación de la base de datos falla pero el servicio sigue funcionando** → el health check reporta el fallo de la base; el servicio puede seguir respondiendo peticiones que no requieren base de datos.
- **Múltiples consultas concurrentes al health check con la base caída** → cada una realiza su propia verificación; no hay estado compartido que contaminar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El endpoint `/api/health` DEBE verificar la conectividad a la base de datos antes de reportar `{"status": "healthy"}`.
- **FR-002**: Si la verificación de la base de datos falla, el endpoint `/api/health` DEBE devolver `200` con `{"status": "healthy", "database": {"connected": false}}` para preservar la compatibilidad con la plataforma de hosting y CI.
- **FR-003**: El endpoint `/api/health/diagnostics` DEBE incluir un campo `database.connected` que indique `true` si la conexión a la base de datos es exitosa, `false` si falló.
- **FR-004**: La verificación de conectividad DEBE usar una consulta ligera (por ejemplo, `SELECT 1`) que no dependa de tablas específicas ni de datos existentes.
- **FR-005**: La verificación DEBE tener un timeout máximo de 5 segundos para no bloquear la plataforma de hosting ni CI.
- **FR-006**: Los errores de la base de datos NO DEBEN exponer al cliente mensajes de error de SQL, rutas del sistema ni stack traces. El detalle técnico va al log; al cliente va un mensaje neutro.
- **FR-007**: Si no hay configuración de base de datos (ni `DATABASE_URL` ni variables de entorno de DB), el health check DEBE reportar "no configurado" en lugar de "caído", para no generar falsas alertas en entornos de desarrollo sin Postgres.

### Key Entities

- **Estado de conectividad de la base de datos**: un valor booleano que indica si la base de datos responde a una consulta ligera. No se persiste; se evalúa en cada petición al health check.

## Success Criteria *(mandatory)*

- **SC-001**: El responsable del servicio puede detectar una base de datos caída consultando `/api/health` antes de que los usuarios reporten errores.
- **SC-002**: La verificación de la base de datos no añade más de 5 segundos de latencia al health check.
- **SC-003**: El endpoint `/api/health/diagnostics` muestra el estado de conectividad de la base de datos en tiempo real.
- **SC-004**: En un entorno sin base de datos configurada (desarrollo local), el health check no genera falsas alertas.
- **SC-005**: Los errores de conexión a la base de datos no se exponen al cliente; solo se registran en el log.

## Clarifications

### Session 2026-08-25

- Q: When the database is down, should `/api/health` return `503` (causing Railway to restart) or `200` with a degraded status field? → A: Return `200` with `"healthy": false` (Option B) to preserve backward compatibility with CI/CD and hosting platforms.

## Assumptions

- La consulta de verificación será `SELECT 1` (o equivalente), que es la forma más ligera de confirmar conectividad sin depender de tablas específicas.
- El timeout de 5 segundos es razonable para un health check; en producción la conexión a Postgres debería ser mucho más rápida.
- Se reutiliza la conexión existente del engine de SQLAlchemy/SQLModel; no se crea una conexión dedicada para el health check.
- El health check de la base de datos es global: no verifica tablas específicas ni datos, solo conectividad.
- La plataforma de hosting (Railway) usa el endpoint `/api/health` como liveness probe; el endpoint siempre devuelve `200` para no causar reinicios innecesarios. El estado de la base de datos se indica en el cuerpo de la respuesta.
