# Feature Specification: Despliegue continuo en la nube

**Feature Branch**: `004-despliegue-continuo`

**Created**: 2026-08-21

**Status**: Implementado

**Input**: User description: "La aplicación solo corre en local con docker compose y Ollama. Necesitamos que esté publicada en Internet, en capa gratuita, y que cada merge a main la actualice sola, porque en la demostración construimos historias en vivo y hay que mostrarlas desplegadas en minutos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publicar sin intervención manual (Priority: P1)

Un integrante fusiona su historia a `main`. Sin que nadie toque un servidor, la nueva versión
queda publicada y accesible en la URL pública.

**Why this priority**: es el requisito que hace posible la demostración en vivo. Sin esto,
"mostrar la aplicación desplegada en 5 a 10 minutos por spec" es inviable.

**Independent Test**: hacer un cambio visible, fusionarlo, y verificar que aparece en la URL pública sin acción manual.

**Acceptance Scenarios**:

1. **Given** un push a `main` que pasa CI, **When** termina el pipeline, **Then** la plataforma construye y publica la nueva versión automáticamente.
2. **Given** un push a `main` que **falla** CI, **When** termina el pipeline, **Then** el despliegue no ocurre y la versión anterior sigue en línea.
3. **Given** un despliegue completado, **When** se consulta la URL pública, **Then** responde en menos de 10 minutos desde el merge.

---

### User Story 2 - Arrancar con la base de datos lista (Priority: P1)

Al desplegar, el esquema y el catálogo semilla deben quedar listos solos. Nadie debe conectarse
a la base de datos de producción a ejecutar SQL a mano.

**Why this priority**: si una historia en vivo añade una columna, el despliegue debe aplicarla
sin intervención o la demostración se detiene.

**Independent Test**: desplegar sobre una base de datos vacía y verificar que la aplicación responde correctamente sin pasos manuales.

**Acceptance Scenarios**:

1. **Given** una base de datos vacía, **When** arranca el contenedor, **Then** se aplican las migraciones de Alembic y se siembra el catálogo.
2. **Given** una base de datos ya migrada, **When** arranca de nuevo, **Then** la siembra no duplica valores (es idempotente).
3. **Given** una migración que falla, **When** arranca el contenedor, **Then** el arranque se detiene con un error explícito en lugar de servir con un esquema inconsistente.

---

### User Story 3 - Saber si está viva (Priority: P2)

La plataforma y el equipo necesitan una señal inequívoca de que la aplicación está operativa.

**Why this priority**: sin verificación de salud, un despliegue roto pasa desapercibido hasta que alguien lo abre a mano.

**Independent Test**: consultar el endpoint de salud en la URL pública.

**Acceptance Scenarios**:

1. **Given** la aplicación desplegada, **When** se consulta `/api/health`, **Then** devuelve `200 {"status": "healthy"}`.
2. **Given** un despliegue cuya salud no responde, **When** la plataforma lo verifica, **Then** lo marca como fallido y conserva la versión anterior.

---

### User Story 4 - Un solo dominio para todo (Priority: P2)

El frontend, la API y la documentación interactiva deben servirse desde la misma URL pública.

**Why this priority**: elimina la configuración de CORS entre orígenes y simplifica lo que hay que mostrar y recordar durante la presentación.

**Independent Test**: abrir la raíz, `/api/docs` y un endpoint de la API en el mismo dominio.

**Acceptance Scenarios**:

1. **Given** la URL pública, **When** se abre la raíz, **Then** se sirve el frontend compilado.
2. **Given** la URL pública, **When** se abre `/api/docs`, **Then** se sirve la documentación interactiva.
3. **Given** el frontend en producción, **When** llama a la API, **Then** usa rutas relativas y no requiere CORS entre orígenes.

---

### Edge Cases

- **El proveedor de IA no está configurado en producción** → la aplicación arranca igualmente en modo degradado y lo advierte en el log. Un despliegue no debe fallar por falta de una clave opcional.
- **La plataforma provee la URL de la base de datos en un formato distinto al esperado** → la configuración acepta tanto una URL completa (`DATABASE_URL`) como los componentes por separado.
- **La plataforma asigna el puerto por variable de entorno** → la aplicación escucha en `PORT` y no en un puerto fijo.
- **Arranques en frío** → el endpoint de salud responde sin tocar la base de datos, para no encadenar latencias.
- **Dos despliegues simultáneos** → el segundo espera al primero; las migraciones no se ejecutan en paralelo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE publicarse automáticamente en cada merge a `main`, sin intervención manual.
- **FR-002**: El despliegue NO DEBE ocurrir si CI falla (test rojo, lint sucio, tipos con errores, secreto detectado o vulnerabilidad de severidad alta).
- **FR-003**: El sistema DEBE aplicar las migraciones de base de datos y sembrar el catálogo automáticamente al arrancar.
- **FR-004**: La siembra DEBE ser idempotente.
- **FR-005**: El sistema DEBE exponer un endpoint de salud que no dependa de servicios externos.
- **FR-006**: El sistema DEBE escuchar en el puerto indicado por la variable de entorno de la plataforma.
- **FR-007**: El sistema DEBE aceptar la configuración de base de datos como URL completa o como componentes separados.
- **FR-008**: El sistema DEBE arrancar correctamente aunque no haya proveedor de IA configurado, registrando la advertencia.
- **FR-009**: Un mismo artefacto de contenedor DEBE servir para local, CI y producción; solo cambian las variables de entorno.
- **FR-010**: El frontend, la API y la documentación DEBEN servirse desde el mismo origen.
- **FR-011**: El costo mensual de la infraestructura DEBE ser USD 0.00 en la configuración documentada.

### Key Entities

- **Artefacto de despliegue**: imagen de contenedor que incluye el backend y el frontend compilado.
- **Entorno**: conjunto de variables que diferencian local, CI y producción sin cambiar el código.
- **Verificación de salud**: señal binaria que la plataforma consulta para aceptar o rechazar un despliegue.

## Success Criteria *(mandatory)*

- **SC-001**: Desde el merge hasta la versión publicada transcurren menos de 10 minutos.
- **SC-002**: Cero pasos manuales entre el merge y la publicación.
- **SC-003**: El costo mensual de infraestructura es USD 0.00.
- **SC-004**: Una historia de usuario construida en vivo puede quedar publicada dentro de la ventana de la demostración.
- **SC-005**: Ningún despliegue con CI en rojo llega a producción.

## Assumptions

- La capa gratuita de la plataforma alcanza para el volumen de una demostración académica.
- Una sola réplica es suficiente; no se requiere alta disponibilidad.
- El dominio proporcionado por la plataforma es aceptable; no se requiere dominio propio.
