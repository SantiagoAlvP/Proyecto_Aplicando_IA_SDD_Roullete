# Feature Specification: Regenerar la descripción de un proyecto existente

**Feature Branch**: `008-regenerar-descripcion`

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "Como desarrollador, quiero regenerar solo la descripción de un proyecto existente, para obtener una redacción distinta sin cambiar la combinación."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Regenerar la descripción de una idea guardada (Priority: P1)

Un desarrollador revisa una idea que ya generó y quiere una redacción alternativa que le
ayude a entenderla mejor. Solicita regenerar la descripción del proyecto y recibe el mismo
lenguaje, tecnología, addon, nivel y restricciones, con una nueva descripción.

**Why this priority**: permite mejorar la utilidad de una idea sin perder una combinación
que el desarrollador ya eligió o quiere conservar.

**Independent Test**: generar o disponer de un proyecto guardado, solicitar la regeneración
por su identificador y verificar que se actualiza la descripción del mismo proyecto mientras
todos los campos de la combinación permanecen iguales.

**Acceptance Scenarios**:

1. **Given** un proyecto existente con una combinación y una descripción, **When** se solicita
   regenerar su descripción usando su identificador, **Then** se devuelve `200` con el mismo
  identificador, la misma combinación completa y una descripción no vacía y distinta de la
  anterior.
2. **Given** un proyecto existente, **When** se solicita regenerar su descripción, **Then**
   no cambian el lenguaje, la tecnología, el addon, el nivel, las restricciones ni las
   relaciones de catálogo del proyecto.
3. **Given** un proyecto existente, **When** la regeneración termina correctamente, **Then**
   se actualiza la descripción del proyecto existente y no se crea un segundo proyecto en el
   historial.
4. **Given** un proyecto existente, **When** se solicita una regeneración, **Then** el modelo
   de IA recibe la combinación actual como contexto y no recibe instrucciones para volver a
   sortearla o modificarla.

---

## Edge Cases

- **El identificador no corresponde a ningún proyecto** → se devuelve `404`, no se llama al
  proveedor de IA y no se persiste ningún cambio.
- **El identificador no es un entero positivo** → se devuelve `422` antes de consumir cuota
  del modelo de IA.
- **El proveedor de IA no responde o agotó su cuota** → se guarda y devuelve una descripción
  determinística de respaldo, se registra el incidente y la petición no produce un `5xx`.
- **La IA devuelve una descripción vacía o inválida** → se conserva la descripción anterior,
  no se modifica ninguna parte de la combinación y se informa el resultado sin exponer detalles
  internos.
- **La nueva descripción supera el límite permitido** → se trunca antes de persistir, sin
  truncar ni alterar otros campos del proyecto.
- **Dos regeneraciones del mismo proyecto llegan simultáneamente** → ambas peticiones solo
  pueden modificar la descripción; la última escritura prevalece y nunca se duplican el
  proyecto ni sus relaciones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir solicitar una nueva descripción para un proyecto
  previamente persistido mediante su identificador.
- **FR-002**: El sistema DEBE devolver el proyecto actualizado con su identificador,
  combinación completa, nivel, restricciones y descripción.
- **FR-003**: El sistema DEBE conservar sin cambios el lenguaje de programación, la tecnología,
  el addon, el nivel, las restricciones y las relaciones de catálogo del proyecto objetivo.
- **FR-004**: El sistema DEBE actualizar la descripción del proyecto existente en lugar de crear
  un nuevo proyecto o nuevas relaciones.
- **FR-005**: El sistema DEBE usar la combinación persistida del proyecto como contexto para
  redactar la nueva descripción.
- **FR-006**: La nueva descripción DEBE ser texto plano, no vacío, de 2 a 4 frases, menor de
  400 caracteres cuando el proveedor responda correctamente y diferente de la descripción
  anterior.
- **FR-007**: Si el proveedor de IA no está disponible, el sistema DEBE persistir y devolver
  una descripción determinística de respaldo, además de registrar el incidente.
- **FR-008**: Si el proveedor devuelve una descripción vacía, inválida o idéntica a la anterior,
  el sistema DEBE conservar la descripción anterior y no modificar el proyecto.
- **FR-009**: El sistema DEBE devolver `404` cuando el proyecto solicitado no exista.
- **FR-010**: El sistema DEBE rechazar con `422` identificadores que no sean enteros positivos
  antes de llamar al proveedor de IA.
- **FR-011**: La operación DEBE respetar el límite de tasa aplicable a las operaciones que
  consumen el proveedor de IA.

### Key Entities

- **Proyecto**: idea persistida identificada de forma única. Contiene la combinación, el nivel,
  las restricciones y la descripción que puede regenerarse.
- **Descripción**: texto generado para explicar qué se construirá y qué se aprenderá; es el
  único atributo que esta operación puede cambiar.
- **Combinación**: conjunto inmutable durante la operación formado por lenguaje, tecnología,
  addon, nivel y restricciones, junto con sus relaciones de catálogo.

## Success Criteria *(mandatory)*

- **SC-001**: En el 100% de las regeneraciones exitosas, el identificador y todos los campos
  de la combinación coinciden con los del proyecto antes de la operación.
- **SC-002**: En el 100% de las regeneraciones exitosas, la respuesta contiene una descripción
  no vacía y distinta de la anterior; el proyecto conserva su lugar como una única entrada del
  historial.
- **SC-003**: El 100% de los identificadores inexistentes produce `404` sin llamadas al modelo
  de IA ni cambios en la base de datos.
- **SC-004**: Ninguna caída o respuesta inválida del proveedor de IA produce un error `5xx`
  visible para el usuario.
- **SC-005**: El 95% de las regeneraciones completadas con un proveedor disponible termina en
  menos de 10 segundos.

## Assumptions

- El historial global existente sigue siendo la forma de localizar un proyecto y sus
  identificadores son suficientes para esta iteración.
- No se requiere autenticación ni autorización por usuario en esta iteración.
- La regeneración reemplaza la descripción anterior; no se conserva un historial de versiones
  de descripciones.
- El límite persistido para una descripción continúa siendo de 500 caracteres, aunque la
  descripción generada normalmente debe ser menor de 400.