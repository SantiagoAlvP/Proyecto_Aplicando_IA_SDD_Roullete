# Implementation Plan: Marcar proyectos generados como favoritos

**Branch**: `005-marcar-favoritos` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-marcar-favoritos/spec.md`

## Summary

Se añade un estado booleano `is_favorite` a los proyectos ya persistidos (tabla `projects`),
más tres operaciones sobre ese estado: marcar, desmarcar y listar solo los favoritos. No se
introduce ninguna tabla nueva ni ningún concepto de usuario: los favoritos son globales,
igual que el historial existente (spec `002-interfaz-tragamonedas`).

El backend reutiliza el dominio `ensemble_project` ya establecido
(`router -> service -> repository -> model`) y extiende sus DTOs existentes (`ProjectResponse`,
`HistoryEntry`) con `id` y `favorite` en lugar de crear un dominio nuevo. El frontend añade un
botón de marcar/desmarcar sobre el resultado recién girado y sobre cada fila del historial, y
una pestaña de "Favoritos" que reutiliza el mismo componente de lista.

## Technical Context

**Language/Version**: Python 3.13 (backend); TypeScript 5.9 / React 19 (frontend)

**Primary Dependencies**: FastAPI, SQLModel, Pydantic v2, Alembic (backend, ya presentes); React, Vite (frontend, ya presentes). Ninguna dependencia nueva.

**Storage**: PostgreSQL 17, mismo esquema existente + dos columnas nuevas en `projects` (`is_favorite`, `level`)

**Testing**: pytest con dobles de prueba para el repositorio (sin Postgres real); `npm run build` como verificación de compilación del frontend

**Target Platform**: mismo contenedor Linux (Docker) desplegado en Railway; sin cambios de infraestructura

**Project Type**: web (API + frontend ya desacoplados, mismo origen)

**Performance Goals**: marcar/desmarcar/listar favoritos responde en < 200 ms (operación CRUD simple, sin LLM de por medio)

**Constraints**: costo adicional USD 0.00 (ninguna dependencia ni servicio nuevo); no debe alterar el comportamiento de generación ni de historial ya existentes

**Scale/Scope**: 3 historias de usuario, 3 endpoints nuevos, 2 columnas nuevas, ~2 componentes de frontend modificados + 1 nuevo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento en este plan |
|---|---|
| I. SDD | Spec, plan y `tasks.md` preceden al código. Rama `005-marcar-favoritos`. |
| II. Capas y SOLID | El estado de favorito se maneja en `EnsembleProjectRepository` (acceso a datos) y `ProjectGeneratorService` (regla: idempotencia, error si no existe). El router solo traduce HTTP <-> DTO y `LookupError` -> `404`. Ningún router toca SQL. |
| III. Test-First | Cada endpoint nuevo lleva test de contrato, camino feliz e idempotencia/error. El repositorio se prueba con dobles (sin Postgres); el servicio se prueba sin la base de datos real. |
| IV. Seguridad | El `project_id` de la ruta se valida como entero positivo por FastAPI; un id inexistente devuelve `404` sin exponer detalle de SQL. `limit` de `/favorites` acotado igual que `/history` (`ge=1, le=50`). Sin secretos ni dependencias nuevas. |
| V. Free-tier | Cero dependencias nuevas, cero servicios externos. La operación no consume tokens de IA. |
| VI. Despliegue | Una migración Alembic (`is_favorite`, `default=false`, `server_default='false'` para filas existentes) aplicada automáticamente al arrancar. |
| VII. YAGNI | Sin tabla de auditoría, sin conteo de favoritos, sin límite máximo de favoritos: la spec no lo pide. El frontend reutiliza el componente de lista existente en lugar de duplicar marcado. |

**Resultado**: PASS — sin desviaciones que registrar.

## Project Structure

### Documentation (this feature)

```text
specs/005-marcar-favoritos/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
core/database/
├── models.py                          # + Project.is_favorite: bool, Project.level: Optional[int]
└── crud.py                            # + ProjectCRUD.create(level=...), .set_favorite(), .get_favorites()

core/ensemble_project/
├── api/
│   ├── ensemble_project_router.py     # + PUT/DELETE /{project_id}/favorite, GET /favorites
│   └── ensemble_project_models.py     # + ProjectResponse.id/.favorite ; HistoryEntry.favorite/.level/.extras
├── ensemble_project_service.py        # + mark_favorite(), unmark_favorite(), get_favorites()
└── ensemble_project_repository.py     # + set_favorite(), list_favorites(); list_recent()/save_project()
                                        #   now populate level and extras from the database

alembic/versions/
└── <rev>_add_favorite_and_level_to_projects.py

frontend/src/
├── types.ts                           # + Project.id/.favorite, HistoryEntry.favorite
├── api.ts                             # + markFavorite(), unmarkFavorite(), favorites()
├── App.tsx                            # + estado y handlers de favorito, pestaña Historial/Favoritos
└── components/
    ├── ResultCard.tsx                 # + botón de marcar/desmarcar sobre el proyecto recién girado
    └── History.tsx                    # + botón de marcar/desmarcar por fila + soporte de modo "favoritos"
```

**Structure Decision**: se extiende el dominio `ensemble_project` ya existente en vez de crear
un dominio `favorites` nuevo, porque un favorito no es una entidad independiente: es un atributo
del ciclo de vida de un proyecto ya generado, y vive en la misma tabla y el mismo repositorio que
ya lo persisten. En el frontend, `History.tsx` se generaliza para servir tanto al historial
completo como a la lista de favoritos (misma forma de datos, filtro distinto), evitando duplicar
un componente de lista casi idéntico (Principio VII).

## Decisiones de diseño

**D-01 — Columna booleana en `projects`, no tabla `favorites` separada.** Un favorito no tiene
atributos propios más allá de "está marcado" y "cuándo" (y la fecha ya la aporta la clave de
ordenamiento existente, `id`). Una tabla adicional exigiría un `JOIN` en cada consulta de
historial solo para pintar una estrella.
*Alternativa descartada*: tabla `project_favorites(project_id, created_at)`. Correcta si algún
día un favorito necesitara historial propio (quién y cuándo lo marcó/desmarcó), pero hoy es
complejidad sin problema que resuelva (Principio VII).

**D-02 — `ProjectResponse` gana `id`.** Hoy el DTO de respuesta de generación no expone el `id`
persistido, así que el frontend no tiene forma de marcar como favorito el proyecto que acaba de
girar sin antes consultar el historial. Añadir `id` es un cambio aditivo y no rompe a ningún
consumidor existente.

**D-03 — Marcar y desmarcar son idempotentes por diseño de método HTTP.** `PUT .../favorite`
para marcar y `DELETE .../favorite` para desmarcar: ambos verbos son naturalmente idempotentes,
así que FR-005 y FR-006 (repetir la operación no falla ni duplica) se cumplen sin lógica
adicional en el servicio más que "si ya está en ese estado, no hacer nada y devolver éxito".

**D-04 — Un único endpoint de listado con filtro, siguiendo el patrón de `/history`.**
`GET /ensemble_project/favorites?limit=` reutiliza la misma forma de respuesta
(`list[HistoryEntry]`) y el mismo acotamiento de `limit` que el historial (spec `002`), en
lugar de inventar un contrato nuevo.

**D-05 — `HistoryEntry` gana `level` y `extras`, no solo `favorite`.** FR-009 exige que la
lista de favoritos muestre la misma información que al generarse, incluyendo nivel y extras.
Como esos dos campos también faltaban en `/history` (nunca se persistió `level` y `extras`
nunca se leía de vuelta desde `project_extras`), se corrige el DTO compartido para ambos
endpoints en lugar de crear un DTO paralelo solo para favoritos.
*Alternativa descartada*: un `FavoriteEntry` separado que sí incluya `level`/`extras`, dejando
`/history` como está. Se descartó porque `/history` tiene exactamente el mismo requisito
implícito (mostrar la información completa de un proyecto ya generado) y dejarlo incompleto
sería una inconsistencia nueva, no una que se resuelve.

**D-06 — `level` se persiste en `projects`; `extras` se lee de `project_extras`.** El nivel
nunca se guardó en la tabla `projects` (solo se usaba en memoria para calcular
`extras_count = nivel * 2` antes de descartarse); sin una columna, no hay forma de devolverlo
en una consulta de historial o favoritos hecha después de que la petición original terminó.
Los extras, en cambio, ya están persistidos en `project_extras` desde `001`; solo faltaba la
consulta que los recupera y los traduce a `Extras` en el repositorio.
*Alternativa descartada*: recalcular `extras_count` a partir de `len(project_extras)` para
inferir un "nivel aproximado". Se descartó por inventar un valor que no es el nivel que el
usuario realmente pidió (Constitution, Principio IV: no se aproximan datos que se pueden
persistir con exactitud).

## Complexity Tracking

*Sin violaciones que registrar: no se introduce ninguna capa, patrón o dependencia adicional.*
