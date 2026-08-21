# Feature Specification: Interfaz web tipo máquina tragamonedas

**Feature Branch**: `002-interfaz-tragamonedas`

**Created**: 2026-08-21

**Status**: Implementado

**Input**: User description: "La API funciona pero solo se puede usar desde Swagger. Quiero una interfaz visual de máquina tragamonedas donde los rodillos giren, se pueda fijar valores, y se vea el historial de lo generado."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Girar los rodillos (Priority: P1)

Un visitante abre la página, ve tres rodillos y un botón. Presiona girar, los rodillos se
animan, y al detenerse aparece la idea de proyecto con su descripción.

**Why this priority**: sin esto la aplicación no tiene interfaz. Es el recorrido que
convierte una API en un producto.

**Independent Test**: abrir la raíz del sitio, presionar girar y verificar que aparece un
proyecto con descripción.

**Acceptance Scenarios**:

1. **Given** la página cargada, **When** se observa, **Then** hay tres rodillos (lenguaje, tecnología, addon), un selector de nivel 1-5 y un botón de girar.
2. **Given** la página cargada, **When** se presiona girar, **Then** los rodillos se animan, se muestra un estado de carga y al terminar aparecen el resultado y su descripción.
3. **Given** que el backend devuelve un error, **When** se presiona girar, **Then** se muestra un mensaje de error legible y el botón vuelve a estar disponible.
4. **Given** una pantalla de 360 px de ancho, **When** se abre la aplicación, **Then** todos los controles siguen siendo usables.

---

### User Story 2 - Fijar rodillos antes de girar (Priority: P2)

El usuario quiere practicar Rust. Bloquea el rodillo de lenguaje en "Rust" y gira:
solo cambian los rodillos libres.

**Why this priority**: es la traducción visual de la Historia 3 de la spec 001. Sin ella,
esa capacidad del backend queda inaccesible desde la interfaz.

**Independent Test**: bloquear un rodillo, girar varias veces y comprobar que ese valor no cambia.

**Acceptance Scenarios**:

1. **Given** un rodillo bloqueado con un valor, **When** se gira, **Then** ese valor se conserva y los demás cambian.
2. **Given** los tres rodillos bloqueados, **When** se gira, **Then** solo cambian el nivel y los extras.
3. **Given** un rodillo bloqueado, **When** se desbloquea, **Then** vuelve a participar en el azar.

---

### User Story 3 - Consultar el historial (Priority: P3)

El usuario generó algo que le gustó hace tres giros. Quiere recuperarlo sin volver a girar.

**Why this priority**: mejora la retención pero no bloquea el uso básico.

**Independent Test**: generar tres proyectos, consultar el historial y verificar que aparecen en orden inverso.

**Acceptance Scenarios**:

1. **Given** varios proyectos generados, **When** se consulta el historial, **Then** se devuelven los más recientes primero.
2. **Given** un `limit` mayor a 50, **When** se consulta, **Then** se devuelve `422`.
3. **Given** ningún proyecto generado, **When** se consulta, **Then** se devuelve `200` con una lista vacía.
4. **Given** la interfaz abierta, **When** termina un giro, **Then** el panel de historial se actualiza automáticamente.

---

### Edge Cases

- **El catálogo tarda en cargar** → los rodillos muestran valores de relleno y se deshabilita el botón hasta que llegue el catálogo.
- **El usuario presiona girar dos veces seguidas** → la segunda pulsación se ignora mientras haya una petición en curso.
- **La descripción es muy larga** → el contenedor hace scroll en lugar de romper el diseño.
- **JavaScript deshabilitado** → se muestra un mensaje indicando que la aplicación requiere JavaScript.
- **El historial contiene proyectos sin descripción** (generados en modo degradado antiguo) → se muestra un texto de relleno, no `null`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE servir una interfaz web en la raíz del dominio público.
- **FR-002**: La interfaz DEBE presentar tres rodillos correspondientes a lenguaje, tecnología y addon, más un selector de nivel de 1 a 5.
- **FR-003**: La interfaz DEBE permitir bloquear individualmente cada rodillo para que conserve su valor entre giros.
- **FR-004**: La interfaz DEBE mostrar estados explícitos de carga y de error, sin dejar nunca la pantalla en blanco.
- **FR-005**: El sistema DEBE exponer un endpoint de historial que devuelva los proyectos generados más recientes, con un límite acotado.
- **FR-006**: El historial DEBE actualizarse automáticamente tras cada generación exitosa.
- **FR-007**: La interfaz DEBE ser usable en pantallas desde 360 px de ancho.
- **FR-008**: El frontend compilado DEBE servirse desde el mismo origen que la API, para evitar peticiones entre orígenes distintos.

### Key Entities

- **Rodillo (reel)**: una de las tres dimensiones visibles. Tiene un valor actual, un estado de bloqueo y un estado de animación.
- **Giro (spin)**: una solicitud de generación. Tiene estado `inactivo`, `girando`, `completado` o `error`.
- **Entrada de historial**: proyecto previamente generado, con su combinación, nivel y descripción.

## Success Criteria *(mandatory)*

- **SC-001**: Un visitante nuevo genera su primera idea sin leer instrucciones, en menos de 15 segundos desde que carga la página.
- **SC-002**: La interfaz nunca queda en un estado sin salida: todo error ofrece reintentar.
- **SC-003**: El paquete del frontend pesa menos de 300 KB comprimido.
- **SC-004**: La interfaz funciona en el último Chrome, Firefox y Safari, y en móvil.

## Assumptions

- No se requiere internacionalización en esta iteración; la interfaz está en español.
- El historial es global, no por usuario, porque todavía no existen cuentas.
