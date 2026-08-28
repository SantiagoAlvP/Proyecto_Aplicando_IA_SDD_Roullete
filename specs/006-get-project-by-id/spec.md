# Obtener proyecto por identificador (get-project-by-id)

Resumen

Como desarrollador, quiero obtener un proyecto específico por su identificador, para poder enlazarlo directamente desde otras aplicaciones o interfaces.

User Story

- Actor: Desarrollador que consume la API (p. ej. frontend o servicio interno).
- Historia: Como desarrollador, quiero obtener los datos de un proyecto concreto mediante su identificador único para poder enlazarlo y mostrar su información sin necesidad de búsquedas adicionales.

Objetivo

Permitir referencias directas a proyectos mediante un identificador estable y obtener todos los datos necesarios para mostrar una vista de detalle o generar enlaces compartibles.

Contexto y alcance

- Esta funcionalidad permite recuperar un único recurso "Proyecto" (read-only) por su identificador.
- No incluye creación, edición ni eliminación de proyectos.
- Se espera que el identificador sea único y estable (UUID o id numérico); el formato exacto se asumirá salvo que se indique lo contrario en las aclaraciones.

## Clarifications

### Session 2026-08-28

- Q: ¿El endpoint debe ser público o requerir autenticación/roles para acceder a proyectos no públicos? → A: B — Híbrido: proyectos públicos accesibles sin autenticación; proyectos privados requieren autenticación y autorización. Esta política permite acceso simple a contenido público y protege datos privados (401 para no autenticado, 403 para sin permiso).


User Scenarios & Testes de aceptación

Escenario A — Proyecto encontrado (flujo feliz)
- Dado que existe un proyecto con identificador válido
- Cuando el cliente solicita el recurso por su identificador
- Entonces la API responde con estado 200 y el body contiene los campos mínimos: id, nombre, descripción, slug (si aplica), propietario (id y nombre), fecha de creación y metadatos relevantes.

Escenario B — Proyecto no encontrado
- Dado que no existe un proyecto con el identificador proporcionado
- Cuando el cliente solicita el recurso
- Entonces la API responde con estado 404 Not Found.

Escenario C — Identificador inválido
- Dado un identificador con formato inválido
- Cuando el cliente hace la petición
- Entonces la API responde con estado 400 Bad Request con un mensaje de error claro.

Escenario D — Acceso denegado (si aplica)
- Dado que el proyecto existe pero el cliente no tiene permisos para verlo
- Cuando el cliente solicita el recurso
- Entonces la API responde con 401 o 403 según la situación y no devuelve campos sensibles.

Requisitos funcionales (testables)

1. RF-01 — Recuperación por identificador
   - Dado un identificador válido de un proyecto existente, una llamada al endpoint devuelve 200 y el cuerpo contiene los campos esperados (id, nombre, descripción, propietario, fechas, tags/metadatos).

2. RF-02 — Manejo de no encontrado
   - Dado un identificador cuyo proyecto no existe, el endpoint devuelve 404.

3. RF-03 — Validación de formato
   - Si el identificador tiene un formato inválido, el endpoint devuelve 400 con un mensaje que indica el problema.

4. RF-04 — Control de acceso
   - Si el proyecto tiene is_public == False, el endpoint requiere autenticación; solo usuarios autorizados (propietario o con permiso 'ver_proyecto' en un modelo de roles) pueden ver el recurso. Responder 401 para clientes no autenticados y 403 para clientes autenticados pero sin permiso. No exponer campos sensibles a usuarios no autorizados.

5. RF-05 — Consistencia de identificadores
   - El identificador usado debe ser el único atributo canónico para enlazar al recurso; la API debe aceptar dicho identificador como única llave para recuperar el proyecto.

Entidades clave

- Proyecto
  - id (string/UUID o entero)
  - nombre (string)
  - descripción (string)
  - slug (string, opcional)
  - owner_id (string)
  - owner_name (string)
  - created_at (timestamp)
  - updated_at (timestamp)
  - is_public (bool)
  - tags (array[string])
  - metadata (object)

Criterios de éxito (medibles y verificables)

- CS-01: Dado un identificador válido de un proyecto existente, la suite de pruebas de aceptación específica para este feature pasa (escenarios A–D).
- CS-02: El 100% de las peticiones con identificadores válidos devuelven el recurso correcto (o 404 si no existe) en entornos de prueba controlados.
- CS-03: No se exponen campos sensibles en respuestas entregadas a clientes sin permisos (cuando apliquen), verificado mediante pruebas de autorización.

Suposiciones

- Los proyectos tienen un identificador único ya establecido en la base de datos.
- El consumidor espera recibir un JSON con campos básicos para renderizar una vista de detalle.
- Política de autorización: proyectos marcados con is_public=true son accesibles sin autenticación; proyectos con is_public=false requieren autenticación y autorización (propietario o permiso 'ver_proyecto').

Dependencias

- Servicio/tabla de proyectos existente (catálogo).
- Mecanismo de autorización del sistema (si aplica).
- Versionado/contratos de la API (para documentar la nueva ruta si se añade).

Fuera de alcance

- Paginación, búsquedas o listados de proyectos.
- Modificación del estado del proyecto (crear/editar/eliminar).
- Generación de vistas o frontend: solo se entrega el recurso.

Seguridad y privacidad

- La respuesta debe ocultar cualquier dato sensible (p. ej. claves internas) si el consumidor no está autorizado.
- Registrar accesos a proyectos protegidos para auditoría (si ya existe esa práctica en el sistema).

Notas y siguientes pasos

- Política de autorización confirmada en la sección Clarifications (2026-08-28): híbrido público/privado con 401/403 según corresponda.
- Con la spec sin huecos, proceder a `/speckit-plan` para definir tareas, y luego `/speckit-tasks` para convertirlas en tickets ejecutables.

---

Especificación generada automáticamente como punto de partida. Actualizar según las respuestas a las aclaraciones y retroalimentación de stakeholders.
