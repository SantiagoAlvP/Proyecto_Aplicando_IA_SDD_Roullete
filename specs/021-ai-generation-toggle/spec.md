# Feature Specification: Desactivar generación por IA mediante variable de entorno

**Feature Branch**: `021-ai-generation-toggle`

**Created**: 2026-08-25

**Status**: En especificación

**Input**: "Como responsable del servicio, quiero poder desactivar la generación por IA con una variable de entorno, para proteger la cuota gratuita si detecto abuso."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Activar el modo degradado (Priority: P1)

El responsable del servicio detecta uso abusivo de la API de IA y necesita cortar el gasto
inmediatamente sin desplegar código nuevo ni reiniciar el servicio. Define una variable de
entorno y el sistema deja de llamar al proveedor de IA en las siguientes peticiones.

**Why this priority**: es la protección financiera mínima. Sin ella, el servicio depende
del comportamiento honorable de los visitantes para no agotar la cuota gratuita.

**Independent Test**: establecer la variable de entorno, reiniciar el servicio y comprobar
que un intento de generación devuelve una descripción determinística de respaldo sin
contactar al proveedor de IA.

**Acceptance Scenarios**:

1. **Given** la variable de entorno configurada para desactivar la IA, **When** un usuario solicita generar un proyecto, **Then** el sistema devuelve una descripción de respaldo generada localmente, sin llamar al proveedor externo, y el código de estado es `201`.
2. **Given** la variable de entorno configurada para desactivar la IA, **When** se consulta el historial, **Then** el endpoint funciona normalmente (la lectura no depende de la IA).
3. **Given** la variable de entorno configurada para desactivar la IA, **When** se consulta un enlace compartido, **Then** el endpoint funciona normalmente.

---

### User Story 2 — Reactivar la generación por IA (Priority: P2)

El responsable del servicio elimina o cambia la variable de entorno y el sistema vuelve a
usar la IA para generar descripciones en las siguientes peticiones.

**Why this priority**: sin reactivación, la protección contra abuso se convierte en una
interrupción permanente del servicio.

**Independent Test**: establecer la variable de entorno para activar la IA, reiniciar
el servicio y comprobar que la generación devuelve descripciones generadas por IA.

**Acceptance Scenarios**:

1. **Given** la variable de entorno configurada para activar la IA, **When** un usuario solicita generar un proyecto, **Then** el sistema llama al proveedor de IA y devuelve una descripción generada por el modelo.
2. **Given** la variable de entorno configurada para activar la IA, **When** se consulta el endpoint de salud, **Then** el sistema responde `200`.

---

### User Story 3 — Mensaje claro al usuario (Priority: P2)

El desarrollador que usa la máquina tragamonedas ve que el servicio funciona pero con
descripciones genéricas, y entiende que el servicio está en modo degradado sin ver
errores técnicos ni stack traces.

**Why this priority**: la experiencia del usuario no debe romperse cuando se activa
la protección; la descripción de respaldo es una degradación aceptable.

**Independent Test**: activar el modo degradado y comprobar que la descripción
devuelta no es una cadena vacía ni un error, sino texto legible.

**Acceptance Scenarios**:

1. **Given** el modo degradado activo, **When** se genera un proyecto, **Then** la descripción tiene entre 2 y 4 frases, menos de 400 caracteres, y es legible para el usuario.
2. **Given** el modo degradado activo, **When** se genera un proyecto, **Then** el frontend muestra la combinación completa, el nivel, los extras y la descripción de respaldo sin errores visibles.

---

### Edge Cases

- **La variable de entorno tiene un valor no reconocido** → el sistema trata cualquier valor que no sea `true`, `1` o `on` (case-insensitive) como desactivación de la IA, por seguridad (fail-closed).
- **La variable de entorno no está definida** → la IA queda activada por defecto (comportamiento actual sin cambios).
- **El proveedor de IA está caído mientras la IA está activada** → el sistema ya maneja esto con la descripción de respaldo determinística existente (FR-009 de la spec 001); el toggle no cambia ese comportamiento.
- **Múltiples generaciones concurrentes con la IA desactivada** → cada una recibe su propia descripción de respaldo; no hay estado compartido que contaminar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE leer una variable de entorno al momento de cada petición de generación, no solo al arrancar, para que un cambio en la configuración surta efecto tras reinicio sin rebuild.
- **FR-002**: El sistema DEBE tratar como "IA desactivada" cualquier valor de la variable que no sea `true`, `1` o `on` (case-insensitive), o la ausencia de la variable. Esto es fail-closed: ante la duda, no se gasta cuota.
- **FR-003**: Cuando la IA está desactivada, el sistema DEBE devolver una descripción de respaldo determinística local (sin salir de la máquina) en lugar de intentar contactar al proveedor.
- **FR-004**: Cuando la IA está desactivada, el sistema DEBE persistir el proyecto igual que con IA activa, incluyendo nivel, extras, share_token y created_at.
- **FR-005**: El endpoint `/api/health` DEBE seguir respondiendo `200` independientemente del estado del toggle, para que CI y el hosting no marquen el despliegue como fallido.
- **FR-006**: El endpoint `/api/health/diagnostics` DEBE indicar si la IA está activada o desactivada, para que el responsable pueda verificar el estado sin revisar el log.
- **FR-007**: El toggle NO DEBE afectar los endpoints de lectura (`/history`, `/shared/{token}`, `/catalog/*`), que no consumen IA.

### Key Entities

- **Variable de entorno `AI_GENERATION_ENABLED`**: la única fuente de verdad sobre si la generación por IA está activa. No se persiste en base de datos.
- **Descripción de respaldo**: texto determinístico generado localmente, ya existente en el sistema como fallback del proveedor de IA; ahora se usa también por decisión explícita del operador.

## Success Criteria *(mandatory)*

- **SC-001**: El operador puede desactivar la generación por IA modificando una variable de entorno y reiniciando el servicio, sin tocar código ni configuración de base de datos.
- **SC-002**: Tras desactivar la IA, el 100% de las peticiones de generación devuelven una descripción no vacía y ningún error visible para el usuario.
- **SC-003**: El endpoint de salud (`/api/health`) sigue respondiendo `200` tanto con la IA activada como desactivada.
- **SC-004**: El endpoint de diagnóstico (`/api/health/diagnostics`) refleja el estado del toggle en tiempo real.
- **SC-005**: Los endpoints de lectura (historial, enlace compartido, catálogo) no se ven afectados por el toggle.

## Assumptions

- La variable de entorno se llama `AI_GENERATION_ENABLED` por defecto; esto se documenta pero no se cambiará en esta iteración.
- El valor por defecto (variable ausente) mantiene la IA activada, para no romper el comportamiento existente.
- La descripción de respaldo determinística ya existe en el código como fallback del gateway; esta feature la reutiliza sin crear nueva lógica.
- El toggle es global: no hay control por usuario o por endpoint, solo un interruptor general del servicio.
- No se requiere persistir el estado del toggle ni registrar cuándo se cambió; es una operación táctica, no de auditoría.
