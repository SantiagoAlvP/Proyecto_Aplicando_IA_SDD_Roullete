# Feature Specification: Generador de ideas de proyectos asistido por IA

**Feature Branch**: `001-generador-de-proyectos`

**Created**: 2026-08-21

**Status**: Implementado

**Input**: User description: "Quiero una máquina tragamonedas que combine lenguajes, tecnologías y addons para proponerle a un desarrollador una idea de proyecto con la que aprender, con una descripción escrita por IA y persistida en base de datos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Girar y obtener una idea sin pensar (Priority: P1)

Un desarrollador quiere practicar pero no sabe qué construir. Pide una idea completamente
aleatoria y el sistema le entrega una combinación coherente de lenguaje, tecnología, addon,
nivel y restricciones extra, acompañada de una descripción que explica qué construirá y qué aprenderá.

**Why this priority**: es el corazón del producto. Sin esto no hay aplicación. Es el único
recorrido que, por sí solo, ya entrega valor completo al usuario.

**Independent Test**: se prueba llamando a un único endpoint sin cuerpo y verificando que
la respuesta contiene los cinco campos del proyecto más la descripción.

**Acceptance Scenarios**:

1. **Given** el catálogo poblado, **When** se solicita un proyecto totalmente aleatorio, **Then** se devuelve `201` con `programming_language`, `technologies`, `addons`, `level` (1-5), `extras` y `description`.
2. **Given** el catálogo vacío, **When** se solicita un proyecto, **Then** se devuelve `422` con un mensaje explicativo y no se persiste nada.
3. **Given** dos solicitudes consecutivas, **When** se comparan, **Then** las combinaciones son independientes entre sí.

---

### User Story 2 - Ajustar el reto al nivel propio (Priority: P2)

El desarrollador conoce su nivel y quiere un proyecto proporcional: ni trivial ni imposible.
Indica un nivel de 1 a 5 y el sistema ajusta la cantidad de restricciones adicionales.

**Why this priority**: convierte un generador de ruido en una herramienta de aprendizaje.
Es la diferencia entre "una idea" y "una idea útil para mí".

**Independent Test**: enviar `{"level": N}` y verificar que el proyecto devuelto tiene nivel N
y exactamente `N*2` restricciones extra.

**Acceptance Scenarios**:

1. **Given** `level = 3`, **When** se genera el proyecto, **Then** el proyecto tiene `level = 3` y 6 extras.
2. **Given** `level = 0`, `6` o un valor no numérico, **When** se envía, **Then** se devuelve `422` sin llamar al modelo de IA.

---

### User Story 3 - Dirigir el aprendizaje hacia una tecnología concreta (Priority: P2)

El desarrollador quiere practicar Rust específicamente, pero le da igual el resto.
Fija uno o más rodillos y deja que el sistema complete los demás.

**Why this priority**: es el caso de uso de retorno. Un usuario que ya conoce el producto
vuelve para dirigir su práctica, no para recibir azar puro.

**Independent Test**: enviar un payload con un solo campo fijado y verificar que ese campo
se respeta y los demás se completan.

**Acceptance Scenarios**:

1. **Given** `programming_language = "Rust"` y el resto vacío, **When** se genera, **Then** el resultado usa Rust y completa lo demás aleatoriamente.
2. **Given** un valor inexistente en el catálogo, **When** se genera, **Then** el valor se incorpora al catálogo para usos futuros.
3. **Given** una combinación técnicamente inviable, **When** la IA la evalúa, **Then** se devuelve `422` con la razón y no se persiste.

---

### User Story 4 - Ver qué opciones existen (Priority: P3)

Antes de fijar un rodillo, el usuario necesita saber qué valores están disponibles.

**Why this priority**: habilitador de la Historia 3 y de la interfaz gráfica, pero sin valor
independiente para el usuario final.

**Independent Test**: consultar los tres endpoints de catálogo y verificar listas no vacías.

**Acceptance Scenarios**:

1. **Given** el catálogo sembrado, **When** se consulta cada lista, **Then** se devuelve `200` con entradas que tienen `id` y `name`.
2. **Given** una tabla vacía, **When** se pide un valor aleatorio, **Then** se devuelve `null`, no un error `500`.

---

### User Story 5 - Recordar lo generado (Priority: P3)

El dueño del producto necesita que cada idea quede almacenada con sus relaciones para
poder analizarla después y construir funcionalidades encima.

**Why this priority**: no lo percibe el usuario final hoy, pero sin él no existen el historial
ni ninguna analítica futura.

**Independent Test**: generar un proyecto y verificar en base de datos las filas y claves foráneas creadas.

**Acceptance Scenarios**:

1. **Given** un proyecto generado, **When** finaliza la petición, **Then** existe una fila en `projects` con claves foráneas válidas.
2. **Given** un proyecto con N extras, **When** se persiste, **Then** existen N filas relacionadas en `project_extras`.
3. **Given** un valor de catálogo ya existente, **When** se guarda otro proyecto que lo usa, **Then** se reutiliza la fila y no se duplica.

---

### Edge Cases

- **El proveedor de IA no responde o agotó su cuota** → el sistema devuelve una descripción determinística de respaldo y registra el incidente. La petición **no** falla.
- **La IA devuelve un índice fuera de rango** al elegir el mejor candidato → se valida el rango y se cae al primer candidato en lugar de propagar un `IndexError`.
- **La descripción excede el límite de la columna** (500 caracteres) → se trunca antes de persistir.
- **Un valor del catálogo llega con el literal `"string"`** (valor por defecto de Swagger) → se trata como vacío y se sustituye por un valor aleatorio.
- **Todos los candidatos son inviables** → `422` con la razón, sin persistir.
- **Peticiones concurrentes que crean el mismo valor de catálogo** → la restricción `unique` sobre `name` evita duplicados.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE generar una idea de proyecto compuesta por un lenguaje de programación, una tecnología, un addon, un nivel de dificultad de 1 a 5 y un conjunto de restricciones extra.
- **FR-002**: El sistema DEBE ofrecer tres modos de generación: totalmente aleatorio, por nivel de dificultad, y por valores fijados por el usuario.
- **FR-003**: El sistema DEBE derivar la cantidad de restricciones extra del nivel elegido, con la regla `extras = nivel * 2`.
- **FR-004**: El sistema DEBE evaluar la viabilidad técnica de cada combinación antes de proponerla, y rechazar únicamente las genuinamente imposibles de construir (no las meramente inusuales o difíciles).
- **FR-005**: El sistema DEBE producir una descripción en texto plano de 2 a 4 frases y menos de 400 caracteres que explique qué se construirá y qué se aprenderá.
- **FR-006**: El sistema DEBE exponer el catálogo completo y una selección aleatoria para cada una de las tres dimensiones.
- **FR-007**: El sistema DEBE persistir cada proyecto aceptado junto con sus relaciones, reutilizando los valores de catálogo existentes.
- **FR-008**: El sistema DEBE incorporar al catálogo cualquier valor nuevo enviado por el usuario.
- **FR-009**: El sistema DEBE seguir respondiendo con una descripción de respaldo cuando el proveedor de IA no esté disponible.
- **FR-010**: El sistema DEBE permitir cambiar de proveedor de IA por configuración, sin modificar servicios ni routers.
- **FR-011**: El sistema DEBE rechazar con `422` toda entrada que no cumpla las restricciones declaradas, antes de consumir cuota del modelo de IA.

### Key Entities

- **Proyecto**: la idea generada. Referencia un lenguaje, una tecnología y un addon, y guarda su descripción.
- **Lenguaje de programación / Tecnología / Addon**: entradas de catálogo con nombre único. Son las tres dimensiones que giran en los rodillos.
- **Extra del proyecto**: restricción adicional asociada a un proyecto. Puede aportar un lenguaje, una tecnología, un addon, o una combinación de ellos.
- **Nivel**: entero de 1 a 5 que representa la dificultad y determina cuántos extras se aplican.

## Success Criteria *(mandatory)*

- **SC-001**: Un usuario obtiene una idea de proyecto completa en menos de 10 segundos desde que la solicita, en el 95% de las peticiones.
- **SC-002**: El 100% de las ideas devueltas incluyen los cinco campos obligatorios más una descripción no vacía.
- **SC-003**: Ninguna caída del proveedor de IA produce un error `5xx` visible para el usuario.
- **SC-004**: El catálogo arranca con al menos 100 valores sembrados sin intervención manual.
- **SC-005**: Cambiar de proveedor de IA requiere modificar exactamente una variable de entorno y cero líneas de código.

## Assumptions

- El usuario no necesita cuenta ni autenticación para generar ideas en esta iteración.
- La calidad literaria de la descripción es secundaria frente a la disponibilidad del servicio.
- El catálogo semilla (`data/data.yaml`) es representativo y no requiere curación editorial en esta iteración.
