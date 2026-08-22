# Feature Specification: Marcar proyectos generados como favoritos

**Feature Branch**: `005-marcar-favoritos`

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "Como desarrollador que usa la aplicación, quiero marcar un proyecto generado como favorito, para poder recuperarlo después sin volver a girar los rodillos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Marcar un proyecto como favorito (Priority: P1)

Un desarrollador gira los rodillos, recibe una idea de proyecto que le gusta y quiere
asegurarse de no perderla entre los muchos giros que hará después. Marca ese proyecto
como favorito con una sola acción, sin necesidad de copiar la descripción a otro lado.

**Why this priority**: es el comportamiento central de la funcionalidad. Sin la capacidad
de marcar, no existe nada que recuperar después.

**Independent Test**: generar un proyecto, marcarlo como favorito y verificar que su
estado de favorito queda registrado y persiste aunque se recargue la página.

**Acceptance Scenarios**:

1. **Given** un proyecto recién generado, **When** el usuario lo marca como favorito, **Then** el proyecto queda identificado como favorito de forma persistente.
2. **Given** un proyecto que ya aparece en el historial, **When** el usuario lo marca como favorito, **Then** el marcado tiene el mismo efecto que si se marcara justo al generarlo.
3. **Given** un proyecto ya marcado como favorito, **When** el usuario intenta marcarlo de nuevo, **Then** el sistema no crea un duplicado y el proyecto sigue apareciendo una sola vez entre los favoritos.
4. **Given** un identificador de proyecto que no existe, **When** el usuario intenta marcarlo como favorito, **Then** el sistema devuelve un error explícito y no registra ningún favorito.

---

### User Story 2 - Recuperar los proyectos favoritos (Priority: P1)

Días después de haber girado, el desarrollador quiere retomar una idea que le gustó sin
tener que volver a girar los rodillos con la esperanza de que vuelva a salir la misma
combinación. Consulta su lista de favoritos y ahí está, con toda su descripción.

**Why this priority**: es la razón de ser de la funcionalidad — "recuperarlo después sin
volver a girar" solo tiene valor si existe un lugar donde recuperarlo. Marcar sin poder
consultar no resuelve el problema del usuario.

**Independent Test**: marcar dos proyectos como favoritos, generar un tercero sin marcarlo,
consultar la lista de favoritos y verificar que aparecen exactamente los dos marcados, con
su combinación y descripción completas.

**Acceptance Scenarios**:

1. **Given** varios proyectos marcados como favoritos, **When** el usuario consulta su lista de favoritos, **Then** ve todos los proyectos marcados con su lenguaje, tecnología, addon, nivel, extras y descripción, sin necesidad de volver a girar.
2. **Given** ningún proyecto marcado como favorito, **When** el usuario consulta la lista, **Then** el sistema muestra una lista vacía en lugar de un error.
3. **Given** proyectos favoritos marcados en distintos momentos, **When** se consulta la lista, **Then** se muestran ordenados del más reciente al más antiguo.

---

### User Story 3 - Quitar un proyecto de favoritos (Priority: P2)

El desarrollador marcó un proyecto como favorito pero, tras revisarlo con calma, decide
que no le interesa seguir practicando esa combinación. Lo desmarca para que deje de
ocupar espacio en su lista de favoritos.

**Why this priority**: mantiene la lista de favoritos útil en el tiempo. No bloquea el
valor principal (marcar y recuperar), pero evita que la lista se vuelva ruido acumulado.

**Independent Test**: marcar un proyecto como favorito, desmarcarlo, y verificar que ya no
aparece en la lista de favoritos aunque el proyecto siga existiendo en el historial general.

**Acceptance Scenarios**:

1. **Given** un proyecto marcado como favorito, **When** el usuario lo desmarca, **Then** deja de aparecer en la lista de favoritos pero sigue existiendo en el historial general de proyectos generados.
2. **Given** un proyecto que no está marcado como favorito, **When** el usuario intenta desmarcarlo, **Then** el sistema no produce error y el resultado final es el mismo (el proyecto no es favorito).

---

### Edge Cases

- **Se marca un proyecto generado en modo degradado** (sin descripción de IA) → el proyecto se puede marcar igual como favorito y se muestra con un texto de relleno en lugar de `null`.
- **Se solicita la lista de favoritos con el catálogo o historial vacíos** → se devuelve una lista vacía, no un error.
- **Dos marcados o desmarcados casi simultáneos sobre el mismo proyecto** → el estado final refleja la última acción procesada, sin duplicar ni dejar estados inconsistentes.
- **Se elimina o depura un proyecto del historial general** → deja de estar disponible también como favorito, ya que no puede recuperarse un proyecto que ya no existe.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir marcar como favorito cualquier proyecto previamente generado, identificándolo de forma unívoca.
- **FR-002**: El sistema DEBE permitir desmarcar un proyecto que estaba marcado como favorito.
- **FR-003**: El estado de favorito de un proyecto DEBE persistir entre sesiones (recargar la página, cerrar y volver a abrir la aplicación) sin depender de que el usuario vuelva a girar.
- **FR-004**: El sistema DEBE exponer una forma de consultar únicamente los proyectos marcados como favoritos, ordenados del más reciente al más antiguo.
- **FR-005**: Marcar como favorito un proyecto que ya es favorito DEBE ser una operación idempotente: no debe crear duplicados ni errores.
- **FR-006**: Desmarcar un proyecto que no es favorito DEBE ser una operación idempotente: no debe producir error.
- **FR-007**: El sistema DEBE indicar de forma visible, tanto en el resultado recién generado como en el historial general, si un proyecto está marcado como favorito.
- **FR-008**: Intentar marcar o desmarcar un proyecto con un identificador inexistente DEBE devolver un error explícito y no alterar ningún estado de favoritos.
- **FR-009**: La lista de favoritos DEBE incluir, para cada proyecto, la misma información que se muestra al generarlo (lenguaje, tecnología, addon, nivel, extras y descripción).

### Key Entities

- **Favorito**: marca sobre un proyecto ya generado que indica la intención del usuario de conservarlo para recuperarlo después. Se asocia a un único proyecto generado; su posición en la lista de favoritos sigue el orden de generación del proyecto (no el momento en que se marcó o desmarcó como favorito).
- **Proyecto generado** *(entidad existente, ver `001-generador-de-proyectos`)*: ahora incorpora un estado de favorito que puede activarse o desactivarse sin afectar el resto de sus datos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede marcar un proyecto como favorito en una sola acción, en menos de 2 segundos desde que lo tiene visible en pantalla.
- **SC-002**: Un usuario puede recuperar la descripción completa de cualquier proyecto marcado como favorito sin generar ningún proyecto nuevo.
- **SC-003**: El estado de favorito se mantiene correcto el 100% de las veces tras recargar la aplicación o volver a abrirla en otra sesión.
- **SC-004**: La lista de favoritos sigue siendo consultable y usable con al menos 100 proyectos marcados.

## Assumptions

- No existe todavía un sistema de cuentas de usuario (ver `002-interfaz-tragamonedas`, donde el historial es global). Por lo tanto, los favoritos son globales para la aplicación, igual que el historial, y no están segmentados por usuario.
- No hay un límite máximo de proyectos que se puedan marcar como favoritos en esta iteración.
- Un proyecto solo puede tener dos estados posibles respecto a favoritos: marcado o no marcado (no hay categorías ni etiquetas adicionales).
- La eliminación de proyectos del historial general está fuera del alcance de esta funcionalidad; si en el futuro se agrega, su efecto sobre los favoritos queda documentado como edge case pero no se implementa aquí.
