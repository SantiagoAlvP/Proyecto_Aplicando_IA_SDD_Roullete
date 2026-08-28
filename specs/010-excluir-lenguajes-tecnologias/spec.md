# Feature Specification: Excluir lenguajes y tecnologías antes de girar

**Feature Branch**: `010-excluir-lenguajes-tecnologias`

**Created**: 2026-08-28

**Status**: Draft

**Input**: User description: "Como desarrollador, quiero excluir uno o más lenguajes antes de girar, para que nunca me salgan tecnologías que no pienso aprender."

## Clarifications

### Session 2026-08-28

- Q: ¿Dónde debe persistirse la configuración de exclusiones para que siga activa entre sesiones? → A: Persistencia local en el navegador mediante `localStorage`.
- Q: ¿También debe poder excluirse el tercer tipo de resultado del catálogo, los addons, o solo los lenguajes y las tecnologías? → A: Solo lenguajes y tecnologías; los addons siguen disponibles.
- Q: ¿Qué debe ocurrir si el usuario excluye todas las opciones disponibles de una categoría, por ejemplo todos los lenguajes? → A: El botón de giro se deshabilita hasta que retire al menos una exclusión.
- Q: ¿Las exclusiones de lenguajes y tecnologías deben aplicarse también a los extras de cada proyecto generado? → A: Sí, deben aplicarse a los rodillos principales y a todos los extras.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Excluir tecnologías no deseadas antes de generar una propuesta (Priority: P1)

Un desarrollador quiere afinar el generador para que no proponga tecnologías que no quiere aprender ni mantener. Antes de girar, selecciona una o varias opciones en una lista de exclusiones y, durante la generación, esas tecnologías desaparecen de las posibilidades.

**Why this priority**: es el comportamiento central de la funcionalidad. Sin esta exclusión, el usuario sigue recibiendo propuestas que no pueden formar parte de su aprendizaje o de su backlog.

**Independent Test**: seleccionar varias tecnologías para excluir, generar un proyecto y comprobar que ninguna de esas opciones aparece en la propuesta ni en los resultados de la tirada.

**Acceptance Scenarios**:

1. **Given** un usuario con varias tecnologías marcadas como excluidas, **When** genera una nueva propuesta, **Then** el sistema no incluye ninguna de esas tecnologías en el resultado final.
2. **Given** un usuario no ha marcado ninguna exclusión, **When** gira los rodillos, **Then** el sistema mantiene el comportamiento habitual sin cambios relevantes.
3. **Given** un usuario intenta excluir una tecnología que ya no existe en el catálogo, **When** guarda la configuración, **Then** el sistema ignora la entrada no válida y no rompe la pantalla ni la generación.
4. **Given** una exclusión ya guardada, **When** el usuario vuelve a la pantalla principal, **Then** la configuración sigue aplicada la próxima vez que genere un proyecto.

---

### User Story 2 - Excluir uno o varios lenguajes enteros de forma persistente (Priority: P1)

El desarrollador quiere bloquear lenguajes completos que no desea ver jamás en el sistema, por ejemplo por afinidad, aprendizaje o estrategia profesional. La exclusión se conserva entre sesiones para evitar que vuelva a salir por error.

**Why this priority**: muchas decisiones de aprendizaje o evolución profesional se toman a nivel de lenguaje, no solo de tecnología puntual. Si se ignora esta capa, la decisión del usuario sigue siendo incompleta.

**Independent Test**: marcar un lenguaje como excluido, generar varias propuestas y verificar que ninguna de ellas usa ese lenguaje.

**Acceptance Scenarios**:

1. **Given** un lenguaje marcado como excluido, **When** el usuario genera una propuesta, **Then** ese lenguaje no aparece en ninguna de las opciones de la tirada.
2. **Given** varios lenguajes excluidos, **When** la generación se ejecuta, **Then** todos quedan fuera del conjunto de posibilidades disponibles.
3. **Given** la exclusión se ha aplicado en una sesión, **When** el usuario vuelve a abrir la aplicación, **Then** la configuración sigue activa sin necesidad de volver a seleccionarla.

---

### User Story 3 - Ajustar y limpiar la lista de exclusiones (Priority: P2)

El desarrollador puede cambiar de opinión con el tiempo y quitar una exclusión que ya no le importa. También puede relajar varios filtros de una vez para volver a la mezcla por defecto.

**Why this priority**: permite mantener la lista de exclusiones útil sin encerrar al usuario en una configuración obsoleta o demasiado restrictiva.

**Independent Test**: añadir una exclusión, eliminarla y generar una propuesta nueva para comprobar que la tecnología vuelve a formar parte del catálogo disponible.

**Acceptance Scenarios**:

1. **Given** una tecnología o lenguaje previamente excluido, **When** el usuario lo elimina de la lista de exclusiones, **Then** vuelve a ser elegible en nuevas generaciones.
2. **Given** un usuario desea reiniciar su configuración, **When** borra todas las exclusiones, **Then** el sistema recupera el comportamiento estándar del generador.

---

### Edge Cases

- El usuario intenta excluir un valor que no existe en el catálogo actual → el sistema lo ignora sin romper la interfaz ni la generación.
- La configuración de exclusiones queda vacía → el generador funciona con el comportamiento por defecto.
- Se excluyen varias opciones a la vez → el sistema aplica todas las restricciones simultáneamente y nunca genera una combinación que incumpla alguna de ellas.
- Los addons no están sujetos a exclusión y siguen formando parte de las posibilidades normales del generador.
- Las exclusiones se aplican también a los lenguajes y tecnologías presentes en los extras; solo los addons de los extras quedan sin filtrar.
- Si todas las opciones elegibles de una categoría están excluidas, el botón de giro permanece deshabilitado y la interfaz indica que debe retirarse al menos una exclusión.
- La lista de catálogo cambia (por ejemplo, se agregan nuevas tecnologías) → las exclusiones solo afectan a los valores que el usuario haya marcado; si una nueva tecnología no está en la lista, no se bloquea automáticamente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir que el usuario excluya uno o varios lenguajes antes de generar una propuesta.
- **FR-002**: El sistema DEBE permitir que el usuario excluya una o varias tecnologías antes de generar una propuesta; los addons no forman parte de esta configuración.
- **FR-003**: El sistema DEBE impedir que cualquier lenguaje o tecnología excluida pueda aparecer en una propuesta recién generada, tanto en los tres rodillos principales como en todos sus extras.
- **FR-004**: La configuración de exclusiones DEBE persistir entre sesiones en el navegador mediante `localStorage`, sin requerir autenticación ni almacenamiento adicional en el backend.
- **FR-005**: El sistema DEBE permitir al usuario revisar y eliminar las exclusiones almacenadas sin perder el resto de la configuración.
- **FR-006**: El sistema DEBE aplicar todas las exclusiones simultáneamente, evitando que una sola entrada no válida o vacía rompa el resto del filtro.
- **FR-007**: Cuando no hay exclusiones activas, el sistema DEBE conservar el comportamiento normal del generador sin cambios en la experiencia base.
- **FR-008**: El sistema DEBE ignorar entradas de exclusión que no correspondan a valores válidos del catálogo actual en lugar de fallar o bloquear la generación.
- **FR-009**: La lista de exclusiones DEBE ser comprensible para el usuario y fácil de activar o desactivar antes de cada generación.
- **FR-010**: Si una categoría no conserva ninguna opción elegible, el sistema DEBE deshabilitar el giro hasta que el usuario retire al menos una exclusión de esa categoría.

### Key Entities

- **Configuración de exclusiones**: conjunto de lenguajes y tecnologías, pero no addons, que el usuario ha decidido no permitir en futuras generaciones.
- **Lenguaje excluido**: valor del catálogo de lenguajes que queda fuera de las posibilidades del generador.
- **Tecnología excluida**: valor del catálogo de tecnologías que queda fuera de las posibilidades del generador; los addons permanecen disponibles.
- **Proyecto generado**: propuesta final que debe respetar la configuración vigente de exclusiones al momento de la generación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El usuario puede marcar y guardar exclusiones en menos de 2 segundos desde que lo decide en la interfaz.
- **SC-002**: El 100% de las propuestas generadas respetan todas las exclusiones activas en ese momento.
- **SC-003**: La configuración persistida continúa aplicándose tras recargar la aplicación o abrirla de nuevo en otra sesión.
- **SC-004**: El usuario puede volver al comportamiento normal en menos de 1 acción de limpieza, eliminando todas las exclusiones activas.

## Assumptions

- Las exclusiones se aplican a nivel global para la aplicación, sin segmentación por usuario ni sesión en esta iteración.
- La funcionalidad se limita a filtrar valores del catálogo ya existente; no crea un sistema de preferencias avanzadas ni reglas complejas de prioridad.
- Los valores excluidos se guardan de forma persistente en el `localStorage` del navegador y se reutilizan la próxima vez que el usuario genere un proyecto en ese navegador.
- Si el catálogo cambia en futuras iteraciones, la configuración de exclusiones no se elimina automáticamente si el valor ya no existe, pero tampoco bloquea la generación.
