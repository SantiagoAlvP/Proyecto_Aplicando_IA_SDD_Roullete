# Feature Specification: Estadísticas de lenguajes y tecnologías más propuestas

**Feature Branch**: `009-estadisticas-lenguajes-tecnologias`

**Created**: 2026-08-28

**Status**: Draft

**Input**: User description: "Como desarrollador, quiero ver las estadísticas de qué lenguajes y tecnologías han salido más, para saber qué está proponiendo el sistema."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar el ranking de lenguajes y tecnologías más repetidos (Priority: P1)

Un desarrollador quiere entender qué combinaciones aparecen con más frecuencia en el sistema para valorar tendencias, detectar preferencias del usuario o decidir qué tecnologías conviene reforzar en próximos proyectos. Consulta un resumen claro y ordenado con las tecnologías y lenguajes que más veces han salido.

**Why this priority**: es la necesidad principal de la funcionalidad. Sin una vista de tendencias, la aplicación no aporta información útil sobre lo que propone de forma recurrente.

**Independent Test**: generar varios proyectos con combinaciones repetidas, abrir la vista de estadísticas y verificar que el sistema muestra un ranking ordenado por frecuencia real.

**Acceptance Scenarios**:

1. **Given** un conjunto de proyectos generados con varias combinaciones repetidas, **When** el usuario abre la vista de estadísticas, **Then** el sistema muestra el ranking de lenguajes y tecnologías más frecuentes con su cantidad de apariciones.
2. **Given** una combinación que aparece muchas veces, **When** la vista de estadísticas se actualiza, **Then** esa combinación aparece en una posición más alta que las menos frecuentes.
3. **Given** proyectos generados en distintos momentos, **When** el usuario revisa la estadística, **Then** la información refleja el historial completo disponible en la aplicación y no solo la última generación.
4. **Given** un historial vacío o sin resultados, **When** el usuario consulta las estadísticas, **Then** el sistema muestra un estado vacío o sin datos de forma clara, sin error técnico.

---

### User Story 2 - Comparar tendencias entre tecnologías y lenguajes (Priority: P2)

El desarrollador quiere saber no solo qué ha salido más, sino qué proporción representa cada opción dentro del conjunto generado. Esto le permite comparar más fácilmente si el sistema está proponiendo un stack más orientado a frontend, backend, data o devops.

**Why this priority**: ayuda a interpretar la salida del sistema, pero no bloquea la utilidad básica del ranking si aún no se ofrece comparación proporcional.

**Independent Test**: generar un historial con varias categorías y verificar que la vista muestra estadísticas relativas y absolutas de cada lenguaje y tecnología.

**Acceptance Scenarios**:

1. **Given** varios proyectos generados con categorías distintas, **When** el usuario revisa la estadística, **Then** puede ver tanto la frecuencia absoluta como la proporción relativa de cada lenguaje y tecnología.
2. **Given** una tecnología que aparece en pocos proyectos, **When** se representa en la vista, **Then** su presencia queda claramente visible aunque no ocupe una posición alta en el ranking global.
3. **Given** varios resultados de la misma categoría, **When** se compara la distribución, **Then** la aplicación distingue entre frecuencia y peso relativo sin mezclar conceptos.

---

### User Story 3 - Revisar la evolución de las propuestas (Priority: P3)

El desarrollador quiere ver si la mezcla de tecnologías que propone el sistema cambia con el tiempo, por ejemplo si se está favoreciendo más frontend, backend, IA, o infraestructura en funcion de las ideas generadas recientemente.

**Why this priority**: aporta contexto de tendencia, pero el valor mínimo se entrega con el ranking global y los conteos por categoría.

**Independent Test**: generar varios grupos de proyectos en distintos momentos y verificar que la vista permite distinguir las tendencias actuales de las históricas.

**Acceptance Scenarios**:

1. **Given** un historial con proyectos generados en diferentes momentos, **When** el usuario consulta la tendencia, **Then** el sistema permite identificar qué lenguajes y tecnologías dominan en cada periodo o en el conjunto total disponible.
2. **Given** un proyecto nuevo generado después de varias ideas previas, **When** se actualiza la vista, **Then** el resultado refleja el crecimiento o cambio de frecuencia sin requerir una recarga manual del histórico completo.

---

### Edge Cases

- Se genera un historial con proyectos que no tienen datos de tecnología o lenguaje completos → la estadística ignora esos valores o los representa como no aplicables sin romper la vista.
- Se consulta la estadística cuando todavía no hay proyectos generados → la aplicación muestra un estado vacío y no falla.
- Hay tecnologías con nombres muy similares o variantes de la misma categoría → la vista evita duplicar conceptos si representan la misma elección, o los presenta de forma claramente diferenciada según el sistema de clasificación.
- El historial crece con el tiempo → la estadística se recalcula correctamente sin perder los resultados previos ni duplicarlos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE calcular y mostrar qué lenguajes y tecnologías han aparecido con más frecuencia en el historial de proyectos generados.
- **FR-002**: El sistema DEBE ordenar los resultados por frecuencia o relevancia para que el usuario pueda identificar rápidamente las opciones más propuestas.
- **FR-003**: El sistema DEBE incluir tanto lenguajes como tecnologías dentro del mismo análisis, sin ocultar ninguna categoría relevante.
- **FR-004**: El sistema DEBE mostrar la cantidad de apariciones de cada lenguaje o tecnología junto con la clasificación general.
- **FR-005**: El sistema DEBE exponer una representación clara del total y la proporción relativa de cada valor dentro del conjunto analizado.
- **FR-006**: El sistema DEBE manejar correctamente un historial vacío o incompleto, devolviendo una vista sin errores y con un estado vacío o equivalente.
- **FR-007**: El sistema DEBE actualizar la estadística cuando se agrega nuevo contenido al historial de proyectos generados.
- **FR-008**: La vista de estadísticas DEBE ser comprensible para un desarrollador sin requerir conocimientos técnicos internos del sistema de generación.
- **FR-009**: El sistema DEBE distinguir claramente entre resultados globales y resultados de tendencia o subconjuntos cuando existan en la misma vista.

### Key Entities *(include if feature involves data)*

- **Proyecto generado**: registro que incluye al menos un lenguaje y una o varias tecnologías asociadas a la propuesta generada.
- **Lenguaje**: valor representativo del stack principal del proyecto, con recuento acumulado a lo largo del historial.
- **Tecnología**: herramienta, framework, librería, infraestructura o componente que aparece en proyectos generados y puede contarse por frecuencia.
- **Estadística**: resumen calculado a partir del historial actual, con frecuencia absoluta, orden y proporción para cada valor observado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Un usuario puede consultar el ranking de lenguajes y tecnologías más frecuentes en menos de 2 segundos desde que abre la vista de estadísticas.
- **SC-002**: La vista refleja con precisión la frecuencia real de las opciones presentes en el historial, con un margen de error de 0% en la cuenta de elementos analizados.
- **SC-003**: El 100% de los proyectos generados incluidos en el historial contribuyen a la estadística sin duplicados ni omisiones en la cuenta.
- **SC-004**: La información resultante permite comparar claramente qué opciones predominan en el sistema y cuáles aparecen de forma marginal.
- **SC-005**: La vista sigue siendo útil con un historial amplio, manteniendo una lectura clara incluso cuando hay más de 100 proyectos analizados.

## Assumptions

- La estadística se calcula sobre el historial de proyectos generados actualmente disponible en la aplicación, sin segmentación por usuario ni sesión.
- La vista está pensada para informar al desarrollador sobre tendencias del sistema, no para una gestión avanzada de datos o exportación en esta iteración.
- Los proyectos pueden contener varios valores de tecnología y más de un lenguaje asociado, por lo que el análisis debe contar cada valor según la estructura del proyecto.
- Si una categoría no tiene datos, la interfaz muestra un estado vacío o una leyenda neutra sin bloquear la navegación.
