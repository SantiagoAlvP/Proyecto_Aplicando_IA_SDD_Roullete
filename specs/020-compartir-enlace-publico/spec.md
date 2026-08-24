# Feature Specification: Compartir proyectos mediante enlace público

**Feature Branch**: `020-compartir-enlace-publico`

**Historia de Usuario**: HU-20

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "20 Como visitante, quiero compartir un proyecto generado mediante un enlace público, para enseñárselo a alguien sin que tenga que girar los rodillos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Abrir un enlace compartido y ver el proyecto (Priority: P1)

Una persona recibe un enlace (por chat, correo o mensaje) de un proyecto generado en
Project Jackpot. Al abrirlo ve, sin pulsar nada más, la combinación completa del
proyecto (lenguaje, tecnología y addon), su nivel de dificultad y su descripción.
No necesita girar los rodillos ni conocer cómo funciona la máquina.

**Why this priority**: es el valor central de la historia: enseñar un resultado concreto
sin que la otra persona tenga que usar la aplicación. Sin esta vista pública no hay nada
que compartir.

**Independent Test**: con el identificador de cualquier proyecto ya generado, abrir su
enlace público y comprobar que se muestra la combinación, el nivel y la descripción
sin realizar ninguna acción.

**Acceptance Scenarios**:

1. **Given** un proyecto generado y persistido, **When** se abre su enlace público, **Then** se muestra la combinación completa (lenguaje, tecnología, addon), el nivel y la descripción, sin necesidad de girar rodillos ni iniciar sesión.
2. **Given** el enlace abierto por una persona que nunca usó la aplicación, **When** observa la página, **Then** entiende qué es el proyecto sin instrucciones adicionales.
3. **Given** un proyecto generado antes de que existiera esta funcionalidad, **When** se abre su enlace, **Then** la vista funciona igual que para los proyectos nuevos.
4. **Given** la vista pública abierta, **When** se observa, **Then** incluye una invitación clara para crear el propio proyecto que lleva a la máquina tragamonedas.

---

### User Story 2 - Obtener y copiar el enlace desde la interfaz (Priority: P2)

Tras generar un proyecto —o desde una entrada del historial— la persona quiere pasarlo
a alguien. Pulsa "compartir", el sistema le entrega el enlace público listo para pegar,
y confirma que quedó copiado.

**Why this priority**: es el lado emisor del recorrido. La vista pública (Historia 1)
es inútil si obtener el enlace requiere copiar identificadores a mano.

**Independent Test**: generar un proyecto (o tomar uno del historial), pulsar compartir y verificar que se obtiene un enlace que, al abrirse, muestra ese mismo proyecto.

**Acceptance Scenarios**:

1. **Given** un proyecto recién generado visible en pantalla, **When** se pulsa "compartir", **Then** se ofrece el enlace público de ese proyecto y queda copiado al portapapeles con una confirmación visual.
2. **Given** una entrada del historial, **When** se pulsa "compartir" sobre ella, **Then** se obtiene el enlace público de ese proyecto concreto.
3. **Given** un navegador que bloquea el acceso al portapapeles, **When** se pulsa "compartir", **Then** se muestra el enlace completo de forma legible para copiarlo manualmente, sin error aparente para el usuario.

---

### User Story 3 - Enlaces rotos con salida digna (Priority: P3)

Alguien recibe un enlace incompleto, manipulado o de un proyecto que ya no existe.
En lugar de un error técnico o una pantalla en blanco, ve un mensaje comprensible y
una salida clara hacia la aplicación.

**Why this priority**: no bloquea el recorrido feliz, pero define cómo se percibe la
aplicación cuando algo falla; un error crudo rompería la confianza en los enlaces.

**Independent Test**: abrir un enlace con un identificador inexistente o mal formado y comprobar que aparece un mensaje amigable con un camino hacia la aplicación.

**Acceptance Scenarios**:

1. **Given** un enlace cuyo identificador no corresponde a ningún proyecto, **When** se abre, **Then** se muestra un mensaje comprensible de "proyecto no disponible" sin ningún detalle técnico interno.
2. **Given** un enlace mal formado, **When** se abre, **Then** se muestra la misma página amigable y ninguna traza, ruta de sistema ni dato interno.
3. **Given** la página de "proyecto no disponible", **When** se observa, **Then** existe una acción clara para ir a la máquina y generar el propio proyecto.

---

### Edge Cases

- **Proyecto antiguo sin descripción** (generado en modo degradado antes de esta funcionalidad) → la vista muestra un texto de relleno legible, nunca un hueco vacío ni texto técnico.
- **Descripción muy larga** → el contenedor hace scroll en lugar de romper el diseño.
- **Apertura desde móvil (por ejemplo, un mensaje de WhatsApp)** → la vista es usable desde 360 px de ancho, igual que el resto de la interfaz.
- **El enlace se comparte varias veces o se reabre días después** → sigue funcionando igual; los enlaces no expiran mientras el proyecto exista.
- **El identificador lleva mayúsculas, barras finales u otros caracteres añadidos al copiar/pegar** → el sistema lo interpreta de forma tolerante o muestra la página amigable, nunca un error técnico.
- **Muchas personas abren el mismo enlace a la vez** → la vista es de solo lectura y todas ven el mismo contenido sin afectar al proyecto original.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE exponer una vista pública de detalle por cada proyecto generado, accesible mediante un enlace directo, sin autenticación ni registro.
- **FR-002**: La vista DEBE mostrar la combinación completa del proyecto (lenguaje, tecnología y addon), su nivel de dificultad y su descripción.
- **FR-003**: La vista DEBE ser de solo lectura: ver el contenido no puede exigir girar rodillos, regenerar nada ni realizar ninguna otra acción previa.
- **FR-004**: La interfaz DEBE ofrecer una acción de "compartir" tanto sobre el proyecto recién generado como sobre cada entrada del historial, que entregue el enlace público correspondiente.
- **FR-005**: Al compartir, el sistema DEBE intentar copiar el enlace al portapapeles y confirmarlo visualmente; si el navegador lo impide, DEBE mostrar el enlace completo para copia manual.
- **FR-006**: Los enlaces DEBEN ser estables y permanentes: no expiran, no requieren sesión y siguen funcionando mientras el proyecto exista.
- **FR-007**: La mecánica de compartir DEBE aplicar también a todos los proyectos generados con anterioridad a esta funcionalidad (alcance retroactivo).
- **FR-008**: Un enlace a un proyecto inexistente o mal formado DEBE mostrar una página de "proyecto no disponible" comprensible, sin exponer detalles técnicos internos, con una acción clara hacia la aplicación.
- **FR-009**: La vista pública DEBE incluir una invitación a crear el propio proyecto, que dirija a la máquina tragamonedas.
- **FR-010**: La vista pública DEBE ser usable en pantallas desde 360 px de ancho, al igual que el resto de la interfaz.

### Key Entities *(include if feature involves data)*

- **Proyecto compartido**: un proyecto ya generado y persistido, identificado de forma única. Lo visible son su combinación (lenguaje, tecnología, addon), su nivel de dificultad, su descripción y su fecha de creación. No se duplica al compartir: el enlace apunta siempre al mismo proyecto.
- **Enlace público**: la dirección que contiene el identificador del proyecto y resuelve a su vista de solo lectura. Es la única pieza que circula entre personas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una persona que recibe el enlace ve el proyecto completo en su primera apertura en menos de 5 segundos, sin realizar ninguna acción adicional.
- **SC-002**: Compartir un proyecto recién generado toma dos interacciones o menos y menos de 10 segundos desde que aparece el resultado.
- **SC-003**: El 100 % de los proyectos del historial tiene un enlace público funcional (alcance retroactivo verificado).
- **SC-004**: Ningún enlace roto o manipulado muestra información técnica interna; el 100 % de los casos muestra la página amigable con salida hacia la aplicación.
- **SC-005**: Quien recibe un enlace entiende el proyecto compartido sin necesitar explicaciones de quien lo envió (comprensión autónoma verificable en pruebas con usuarios).

## Assumptions

- No existen cuentas de usuario: cualquier persona con el enlace puede ver el proyecto. No hay privacidad por proyecto en esta iteración (el historial ya es global).
- El enlace corresponde a un único proyecto; las colecciones y favoritos quedan fuera de esta historia.
- Los enlaces no expiran y no se pueden revocar individualmente en esta iteración.
- La vista está en español, coherente con el resto de la interfaz.
- El contenido mostrado es exactamente el mismo que el del historial: compartir no altera ni enriquece el proyecto.
