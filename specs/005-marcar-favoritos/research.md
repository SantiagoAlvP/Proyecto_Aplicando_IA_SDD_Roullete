# Phase 0 Research: Marcar proyectos generados como favoritos

No quedaron `NEEDS CLARIFICATION` en el Technical Context: la funcionalidad reutiliza
el stack, el dominio y las convenciones ya fijadas en `001-generador-de-proyectos` y
`002-interfaz-tragamonedas`. Este documento registra las decisiones evaluadas antes de
escribir el modelo de datos y los contratos.

## Decisión: dónde vive el estado de favorito

- **Decision**: columna `is_favorite: bool` (default `false`) en la tabla `projects` existente.
- **Rationale**: un favorito es un atributo del ciclo de vida de un proyecto ya generado, no una
  entidad con relaciones propias. Vivir en la misma fila evita un `JOIN` en cada lectura de
  historial solo para saber si mostrar la estrella marcada.
- **Alternatives considered**: tabla `project_favorites(project_id, marked_at)` — se descartó
  por añadir una migración, una relación y un `JOIN` para resolver un problema que hoy es un
  booleano (Principio VII, Constitution).

## Decisión: forma de las operaciones de marcar/desmarcar

- **Decision**: `PUT /ensemble_project/{project_id}/favorite` para marcar,
  `DELETE /ensemble_project/{project_id}/favorite` para desmarcar.
- **Rationale**: ambos verbos HTTP son idempotentes por definición, que es exactamente el
  requisito de FR-005/FR-006 (repetir la operación no debe fallar ni duplicar). Evita tener que
  codificar la idempotencia como lógica de negocio adicional.
- **Alternatives considered**: un único `POST /favorite:toggle` — más corto, pero obliga al
  cliente a conocer el estado actual para predecir el resultado, y no es naturalmente idempotente
  ante un doble clic o un reintento de red.

## Decisión: cómo se listan los favoritos

- **Decision**: `GET /ensemble_project/favorites?limit=` devuelve `list[HistoryEntry]`, el mismo
  DTO que ya usa `/history`, con `favorite` siempre en `true`.
- **Rationale**: reutilizar la forma de respuesta evita que el frontend mantenga dos tipos casi
  idénticos y permite reutilizar el mismo componente de lista (`History.tsx`) para ambas vistas.
- **Alternatives considered**: un DTO `FavoriteEntry` propio — duplicaría campos sin aportar
  información adicional.

## Decisión: exposición del `id` en la respuesta de generación

- **Decision**: `ProjectResponse` (la respuesta de los tres endpoints `generate_project_*`) gana
  un campo `id` con el identificador ya persistido.
- **Rationale**: sin el `id`, el frontend no puede marcar como favorito el proyecto recién
  girado sin antes ir a buscarlo al historial. Es un cambio aditivo: ningún consumidor existente
  depende de la ausencia de ese campo.
- **Alternatives considered**: obligar al frontend a resolver el `id` consultando `/history`
  inmediatamente después de girar — añade una petición de red y una condición de carrera si el
  usuario marca como favorito antes de que esa segunda petición responda.

## Migración de esquema

- **Decision**: una migración Alembic que agrega `is_favorite BOOLEAN NOT NULL DEFAULT false` y
  `level INTEGER NULL`, con `server_default` en `is_favorite` para que las filas ya existentes
  queden como no favoritas sin necesitar un `UPDATE` manual. `level` queda `NULL` en filas
  históricas (nunca se persistió antes) y se rellena para todo proyecto generado en adelante.
- **Rationale**: Constitution, Principio VI — las migraciones son versionadas y se aplican solas
  al arrancar; el `server_default` evita romper filas históricas.

## Decisión: cómo exponer `level` y `extras` en `/history` y `/favorites` (hallazgo de `/speckit-analyze`)

- **Decision**: `HistoryEntry` gana `level: int | None` y `extras: list[Extras]`, además de
  `favorite`. `level` se lee de la nueva columna `Project.level`; `extras` se construye a
  partir de la relación ORM `Project.extras` (ya definida desde `001`, sin consulta SQL
  adicional) traduciendo cada `ProjectExtra` a `Extras` con los nombres de catálogo
  relacionados.
- **Rationale**: FR-009 exige que la lista de favoritos muestre "la misma información que se
  muestra al generarlo (lenguaje, tecnología, addon, **nivel, extras** y descripción)". El plan
  inicial reutilizaba `HistoryEntry` sin darse cuenta de que ese DTO nunca tuvo esos dos campos
  — ni siquiera en `/history` — porque `level` nunca se persistió y `extras` nunca se leía de
  vuelta. Corregir el DTO compartido resuelve el requisito para favoritos y, de paso, para
  historial (que tenía la misma carencia sin que ninguna spec anterior la exigiera
  explícitamente).
- **Alternatives considered**: dejar `/history` como está y crear un `FavoriteEntry` con los
  campos completos solo para `/favorites` — descartado por duplicar el DTO para resolver una
  carencia que en realidad es compartida por ambos endpoints (ver D-05 en `plan.md`).
