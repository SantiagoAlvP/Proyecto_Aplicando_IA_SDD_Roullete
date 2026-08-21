# Feature Specification: Endurecimiento de seguridad de la API

**Feature Branch**: `003-endurecimiento-seguridad`

**Created**: 2026-08-21

**Status**: Implementado

**Input**: User description: "La API es pública, gratuita y llama a un LLM con cuota limitada. Cualquiera puede agotarla con un bucle de curl. Además necesitamos que no filtre información interna y que CI detecte secretos y dependencias vulnerables."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resistir el abuso de la cuota de IA (Priority: P1)

Un script automatizado bombardea el endpoint de generación. El sistema debe cortar el exceso
antes de que consuma la cuota gratuita del proveedor de IA, sin afectar a los usuarios legítimos.

**Why this priority**: es el riesgo con mayor impacto real. Si la cuota se agota, la aplicación
deja de funcionar para todos, incluida la demostración.

**Independent Test**: enviar N+1 peticiones en un minuto desde el mismo origen y verificar que
la última recibe `429`.

**Acceptance Scenarios**:

1. **Given** el límite configurado en N peticiones por minuto, **When** se envía la petición N+1 desde el mismo cliente, **Then** se devuelve `429` con la cabecera `Retry-After`.
2. **Given** que un cliente fue limitado, **When** transcurre la ventana de tiempo, **Then** vuelve a ser atendido normalmente.
3. **Given** dos clientes distintos, **When** uno alcanza su límite, **Then** el otro no se ve afectado.
4. **Given** el endpoint de salud, **When** se consulta repetidamente, **Then** nunca se limita (lo usa la plataforma de hosting como verificación de vida).

---

### User Story 2 - No filtrar información interna (Priority: P1)

Ante un fallo, el usuario debe recibir un mensaje neutro y el equipo debe poder rastrear el
incidente. Un stack trace en la respuesta es un mapa del sistema regalado a un atacante.

**Why this priority**: la fuga de información habilita todos los demás ataques. Coste de
implementación bajo, impacto alto.

**Independent Test**: forzar una excepción no controlada y verificar la forma de la respuesta.

**Acceptance Scenarios**:

1. **Given** una excepción no controlada, **When** se devuelve la respuesta, **Then** contiene un mensaje genérico y un `request_id`, y no contiene trazas, rutas del sistema, SQL ni nombres de tablas.
2. **Given** ese mismo fallo, **When** se revisa el log del servidor, **Then** aparece el detalle técnico completo asociado al mismo `request_id`.
3. **Given** un error de validación, **When** se devuelve, **Then** indica qué campo es inválido sin revelar la estructura interna del modelo de datos.

---

### User Story 3 - Endurecer el navegador y los orígenes (Priority: P2)

Las respuestas deben instruir al navegador para que no infiera tipos MIME, no permita
enmarcado y no cargue recursos arbitrarios. Los orígenes permitidos deben ser una lista blanca.

**Why this priority**: mitiga XSS, clickjacking y sniffing de contenido con configuración,
sin cambiar la lógica de negocio.

**Independent Test**: inspeccionar las cabeceras de cualquier respuesta.

**Acceptance Scenarios**:

1. **Given** cualquier respuesta, **When** se inspeccionan sus cabeceras, **Then** incluye `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy` y `Content-Security-Policy`.
2. **Given** el entorno de producción, **When** se inspecciona la respuesta, **Then** incluye además `Strict-Transport-Security`.
3. **Given** un origen fuera de la lista blanca, **When** hace una petición desde el navegador, **Then** CORS la rechaza.
4. **Given** la configuración de producción, **When** se revisa, **Then** `allow_origins` nunca es `*`.

---

### User Story 4 - Rechazar entradas desproporcionadas (Priority: P2)

Un payload con diez mil extras o una cadena de un megabyte no debe llegar nunca al modelo de IA.

**Why this priority**: es la puerta de entrada barata a un ataque de agotamiento de recursos.

**Independent Test**: enviar un payload sobredimensionado y verificar el rechazo temprano.

**Acceptance Scenarios**:

1. **Given** un payload con más extras de los permitidos, **When** se envía, **Then** se devuelve `422` sin invocar al modelo de IA.
2. **Given** un nombre de tecnología más largo que el máximo permitido, **When** se envía, **Then** se devuelve `422`.
3. **Given** un cuerpo de petición que excede el tamaño máximo, **When** se envía, **Then** se rechaza antes de deserializarlo.

---

### User Story 5 - Impedir que entren secretos y dependencias vulnerables (Priority: P2)

Ningún commit debe introducir una API key ni una dependencia con vulnerabilidad conocida de severidad alta.

**Why this priority**: previene el error humano más común y más caro del proyecto.

**Independent Test**: ejecutar el pipeline de CI sobre una rama que contenga una clave de prueba y verificar que falla.

**Acceptance Scenarios**:

1. **Given** un commit con una cadena que parece una API key, **When** corre CI, **Then** el pipeline falla y el merge queda bloqueado.
2. **Given** una dependencia con vulnerabilidad de severidad alta, **When** corre la auditoría, **Then** el pipeline falla.
3. **Given** el repositorio en su estado actual, **When** se ejecutan ambos análisis, **Then** no se reporta ningún hallazgo.

---

### Edge Cases

- **El servicio corre detrás de un proxy** → el limitador identifica al cliente por `X-Forwarded-For` cuando la plataforma lo provee, y por IP directa en caso contrario.
- **Reinicio del proceso** → el contador en memoria se pierde y todos los clientes empiezan de cero. Es aceptable: sin Redis en capa gratuita, el limitador es una defensa de mejor esfuerzo, no una garantía contractual.
- **Peticiones legítimas simultáneas desde una misma red universitaria (NAT)** → el límite por minuto se dimensiona con holgura para no castigar este caso.
- **Preflight de CORS** (`OPTIONS`) → no cuenta contra el límite.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE limitar la tasa de peticiones por cliente en los endpoints que invocan al modelo de IA.
- **FR-002**: El sistema DEBE responder `429` con `Retry-After` al superar el límite.
- **FR-003**: El endpoint de salud DEBE quedar exento del límite.
- **FR-004**: El sistema DEBE incluir cabeceras de seguridad en todas las respuestas, y HSTS únicamente en producción.
- **FR-005**: El sistema DEBE resolver los orígenes permitidos desde configuración, con lista blanca explícita y prohibición de `*` en producción.
- **FR-006**: El sistema DEBE devolver errores genéricos con un `request_id` correlacionable, y registrar el detalle solo en el log del servidor.
- **FR-007**: El sistema DEBE acotar explícitamente toda entrada externa: longitud de cadenas, número de extras, rango del nivel y tamaño del cuerpo.
- **FR-008**: El sistema DEBE leer todo secreto desde variables de entorno y NO DEBE contener secretos versionados.
- **FR-009**: El pipeline de CI DEBE ejecutar un escaneo de secretos y una auditoría de dependencias, y fallar ante hallazgos de severidad alta.
- **FR-010**: El sistema DEBE registrar cada petición con su `request_id`, método, ruta, código de estado y duración, sin registrar el contenido del cuerpo.

### Key Entities

- **Cliente limitado**: identificado por su dirección de origen. Tiene una cuenta de peticiones dentro de una ventana temporal.
- **Identificador de correlación (`request_id`)**: identificador único por petición que enlaza la respuesta del cliente con el registro del servidor.
- **Política de seguridad**: conjunto de cabeceras y orígenes permitidos, resuelto según el entorno.

## Success Criteria *(mandatory)*

- **SC-001**: Un bucle automatizado no consigue más de N generaciones por minuto.
- **SC-002**: Ninguna respuesta de error contiene trazas, rutas del sistema, SQL ni nombres de tablas.
- **SC-003**: El 100% de las respuestas incluye las cuatro cabeceras de seguridad obligatorias.
- **SC-004**: El escaneo de secretos y la auditoría de dependencias corren en cada push y no reportan hallazgos.
- **SC-005**: Todo incidente en producción puede rastrearse desde el `request_id` que vio el usuario hasta la traza completa en el log.

## Assumptions

- No hay autenticación en esta iteración, por lo que el limitador identifica clientes por dirección de red.
- Sin Redis en la capa gratuita, el estado del limitador es por proceso. Se documenta como limitación conocida en `docs/security.md`.
