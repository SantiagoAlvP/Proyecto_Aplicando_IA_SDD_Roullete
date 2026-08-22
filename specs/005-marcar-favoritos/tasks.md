# Tasks: Marcar proyectos generados como favoritos

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md) · [data-model.md](./data-model.md) · [contracts/favorites-api.md](./contracts/favorites-api.md) · [research.md](./research.md) · [quickstart.md](./quickstart.md)

**Branch**: `005-marcar-favoritos`

**Convención**: `[P]` = paralelizable (toca archivos disjuntos de las demás tareas `[P]` de la
misma fase). `[USn]` = historia de usuario a la que pertenece la tarea, según `spec.md`.
Cada tarea es un commit con mensaje `HU-XX: descripción`.

> **Nota de `/speckit-analyze`**: esta versión corrige dos hallazgos detectados antes de
> implementar (ver decisiones D-05/D-06 en `plan.md`): `level` no se persistía en ningún lado
> (se agrega la columna) y `extras` nunca se leía de vuelta desde `project_extras` (se agrega
> la consulta). Ambos son necesarios para que `/history` y `/favorites` cumplan FR-009.

---

## Fase 1 — Fundamentos (bloquea todas las historias)

**Propósito**: preparar el esquema y los contratos que las tres historias necesitan antes de
poder marcar, listar o desmarcar nada.

- [X] **T001** `[P]` Migración Alembic: agregar `is_favorite BOOLEAN NOT NULL DEFAULT false` (con `server_default`) y `level INTEGER NULL` a `projects` → `alembic/versions/<rev>_add_favorite_and_level_to_projects.py`
- [X] **T002** `[P]` Agregar `is_favorite: bool = Field(default=False)` y `level: Optional[int] = Field(default=None)` al modelo `Project` → `core/database/models.py`
- [X] **T003** `[P]` Agregar `id: int` y `favorite: bool` a `ProjectResponse`; agregar `favorite: bool`, `level: int | None` y `extras: list[Extras]` a `HistoryEntry` → `core/ensemble_project/api/ensemble_project_models.py`
- [X] **T004** Aceptar y persistir `level` en `ProjectCRUD.create()` (depende de T002) → `core/database/crud.py`
- [X] **T005** Actualizar `EnsembleProjectRepository`: `save_project()` pasa `project["level"]` a `ProjectCRUD.create()` y agrega `id`/`favorite=False` al dict devuelto; `list_recent()` agrega `level=project.level` y `extras` (mapeados desde la relación ORM ya cargada `project.extras`, sin consulta adicional) y `favorite=project.is_favorite` a cada `HistoryEntry`. Extraer un helper privado `_to_history_entry(project)` para no duplicar este mapeo en la Fase 3 (depende de T003, T004) → `core/ensemble_project/ensemble_project_repository.py`
- [X] **T006** `[P]` Actualizar los tests existentes que construyen `ProjectResponse`/`HistoryEntry` para reflejar los campos nuevos (`id`, `favorite`, `level`, `extras`) → `tests/test_fastapi_endpoints/test_history.py`, `tests/test_database/test_history_repository.py`

**Checkpoint**: `uv run pytest` sigue en verde con los campos nuevos presentes en las
respuestas de generación e historial, aunque todavía no exista forma de cambiar el favorito.

---

## Fase 2 — Historia 1: Marcar un proyecto como favorito (Priority: P1) 🎯 MVP

**Goal**: un usuario puede marcar como favorito un proyecto recién generado o uno del
historial, y ese estado persiste, visible en ambos lugares (FR-007).

**Independent Test**: generar un proyecto, marcarlo como favorito vía `PUT .../{id}/favorite`
y confirmar que la respuesta trae `favorite: true` y que un `GET /history` posterior también
lo refleja.

### Implementación

- [X] **T007** `[US1]` Agregar `ProjectCRUD.set_favorite(session, project_id, value)` que actualiza `is_favorite` y devuelve el `Project` actualizado, o `None` si no existe → `core/database/crud.py`
- [X] **T008** `[US1]` Agregar `EnsembleProjectRepository.set_favorite(project_id, value) -> Optional[HistoryEntry]`, reutilizando el helper `_to_history_entry()` de T005 (depende de T007) → `core/ensemble_project/ensemble_project_repository.py`
- [X] **T009** `[US1]` Agregar `ProjectGeneratorService.mark_favorite(project_id) -> HistoryEntry`, lanzando `LookupError` si el proyecto no existe (depende de T008) → `core/ensemble_project/ensemble_project_service.py`
- [X] **T010** `[US1]` Exponer `PUT /api/v1/ensemble_project/{project_id}/favorite` con `project_id: int = Path(gt=0)`, traduciendo `LookupError` a `404` (depende de T009) → `core/ensemble_project/api/ensemble_project_router.py`
- [X] **T011** `[P]` `[US1]` Tests: marcar un proyecto existente, marcar dos veces seguidas (idempotencia, FR-005), marcar un `id` inexistente o `<= 0` (`404`/`422`, FR-008) → `tests/test_fastapi_endpoints/test_favorites.py`
- [X] **T012** `[P]` `[US1]` Agregar `markFavorite(id)` a la capa de red del frontend → `frontend/src/api.ts`
- [X] **T013** `[P]` `[US1]` Agregar `id: number`, `favorite: boolean`, `level: number | null` y `extras: Extra[]` a `HistoryEntry`, y `id: number`/`favorite: boolean` a `Project` → `frontend/src/types.ts`
- [X] **T014** `[US1]` Agregar un indicador/botón de favorito sobre el resultado recién girado que refleje visualmente `project.favorite` desde el primer render, no solo tras hacer clic (FR-007) (depende de T012, T013) → `frontend/src/components/ResultCard.tsx`
- [X] **T015** `[US1]` Agregar el mismo indicador/botón de favorito por fila del historial, reflejando `entry.favorite` (FR-007) (depende de T012, T013) → `frontend/src/components/History.tsx`
- [X] **T016** `[US1]` Conectar ambos botones en `App.tsx`: al marcar, actualizar el proyecto mostrado y la entrada correspondiente del historial con la respuesta del servidor (depende de T014, T015) → `frontend/src/App.tsx`

**Checkpoint**: la Historia 1 es demostrable por API con `curl` al cierre de esta fase; la
demostración completa en la interfaz (poder *consultar* lo marcado sin volver a girar) llega
con la Fase 3.

---

## Fase 3 — Historia 2: Recuperar los proyectos favoritos (Priority: P1)

**Goal**: un usuario puede ver todos sus proyectos marcados como favoritos, con su
combinación, nivel, extras y descripción completos, sin volver a girar.

**Independent Test**: marcar dos proyectos como favoritos, generar un tercero sin marcarlo,
llamar a `GET /favorites` y confirmar que devuelve exactamente los dos marcados, con nivel y
extras incluidos, ordenados del más reciente al más antiguo.

### Implementación

- [X] **T017** `[US2]` Agregar `ProjectCRUD.get_favorites(session, limit) -> Sequence[Project]`, filtrado por `is_favorite=True` y ordenado por `id` descendente con `limit` acotado en SQL → `core/database/crud.py`
- [X] **T018** `[US2]` Agregar `EnsembleProjectRepository.list_favorites(limit) -> list[HistoryEntry]`, reutilizando el helper `_to_history_entry()` de T005 (depende de T017) → `core/ensemble_project/ensemble_project_repository.py`
- [X] **T019** `[US2]` Agregar `ProjectGeneratorService.get_favorites(limit) -> list[HistoryEntry]` (depende de T018) → `core/ensemble_project/ensemble_project_service.py`
- [X] **T020** `[US2]` Exponer `GET /api/v1/ensemble_project/favorites` con `limit` acotado (`ge=1, le=50`, por defecto 10), igual que `/history` (depende de T019) → `core/ensemble_project/api/ensemble_project_router.py`
- [X] **T021** `[P]` `[US2]` Tests: orden del más reciente al más antiguo, `level`/`extras` presentes en cada elemento (FR-009), `limit` fuera de rango (`422`), lista vacía sin favoritos (`200`, `[]`) → `tests/test_fastapi_endpoints/test_favorites.py`
- [X] **T022** `[P]` `[US2]` Agregar `favorites(limit)` a la capa de red del frontend → `frontend/src/api.ts`
- [X] **T023** `[US2]` Generalizar `History.tsx` para aceptar un título y una lista de entradas configurables, de modo que sirva tanto para el historial completo como para los favoritos (depende de T013) → `frontend/src/components/History.tsx`
- [X] **T024** `[US2]` Agregar una pestaña "Favoritos" en `App.tsx` que consulta `favorites()` y reutiliza el componente generalizado (depende de T022, T023) → `frontend/src/App.tsx`

**Checkpoint**: las Historias 1 y 2 juntas entregan el valor completo descrito en la spec
("marcar y recuperar sin volver a girar"), incluyendo nivel y extras (FR-009). **Este es el
MVP real de la spec.**

---

## Fase 4 — Historia 3: Quitar un proyecto de favoritos (Priority: P2)

**Goal**: un usuario puede desmarcar un proyecto que ya no le interesa mantener en favoritos.

**Independent Test**: marcar un proyecto como favorito, desmarcarlo vía
`DELETE .../{id}/favorite`, y confirmar que ya no aparece en `GET /favorites` aunque sigue
existiendo en `GET /history`.

### Implementación

- [X] **T025** `[US3]` Agregar `ProjectGeneratorService.unmark_favorite(project_id) -> HistoryEntry`, reutilizando `EnsembleProjectRepository.set_favorite(project_id, False)` (de T008) y lanzando `LookupError` si no existe → `core/ensemble_project/ensemble_project_service.py`
- [X] **T026** `[US3]` Exponer `DELETE /api/v1/ensemble_project/{project_id}/favorite` con `project_id: int = Path(gt=0)`, traduciendo `LookupError` a `404` (depende de T025) → `core/ensemble_project/api/ensemble_project_router.py`
- [X] **T027** `[P]` `[US3]` Tests: desmarcar un favorito existente, desmarcar dos veces seguidas (idempotencia, FR-006), desmarcar un `id` inexistente o `<= 0` (`404`/`422`), y verificar que el proyecto sigue en `/history` pero no en `/favorites` → `tests/test_fastapi_endpoints/test_favorites.py`
- [X] **T028** `[P]` `[US3]` Agregar `unmarkFavorite(id)` a la capa de red del frontend → `frontend/src/api.ts`
- [X] **T029** `[US3]` Convertir el indicador de favorito en un verdadero interruptor (marcar/desmarcar) en `ResultCard.tsx` y en las filas de `History.tsx`/Favoritos, quitando la fila de la pestaña de Favoritos en cuanto se desmarca (depende de T014, T015, T023, T028) → `frontend/src/App.tsx`, `frontend/src/components/ResultCard.tsx`, `frontend/src/components/History.tsx`

**Checkpoint**: las tres historias funcionan de forma independiente y en conjunto: marcar,
consultar y desmarcar sin volver a girar los rodillos.

---

## Fase 5 — Pulido y verificación cruzada

- [X] **T030** `[P]` Ejecutar `uv run ruff check`, `uv run ruff format --check` y `uv run ty check` sobre todos los archivos tocados
- [X] **T031** `[P]` Ejecutar `npm run build` en `frontend/` para verificar que compila sin errores de tipos con los campos nuevos
- [ ] **T032** Ejecutar `quickstart.md` de punta a punta contra el backend levantado localmente (marcar, idempotencia, listar con nivel/extras, desmarcar, errores 404/422, verificación en la interfaz)

---

## Dependencias

```
Fase 1 (Fundamentos) ──▶ Fase 2 (US1: marcar) ──▶ Fase 3 (US2: listar) ──▶ Fase 4 (US3: desmarcar) ──▶ Fase 5 (Pulido)
```

- **Fase 1** bloquea todo: sin `is_favorite`/`level` en `projects` ni los campos nuevos en los
  DTOs, ninguna historia tiene dónde apoyarse.
- **Historia 1 (US1)** es la única con dependencia dura de la Fase 1. No depende de US2 ni US3.
- **Historia 2 (US2)** es independiente de US1 a nivel de API (`GET /favorites` funciona aunque
  nunca se haya llamado a `PUT .../favorite` — devolvería una lista vacía), pero solo es
  demostrable con datos reales después de US1.
- **Historia 3 (US3)** reutiliza el `set_favorite()` construido en US1 (T008) y el `History.tsx`
  generalizado en US2 (T023); por eso se implementa al final, aunque su valor de negocio es P2.

### Oportunidades de paralelismo

- T001, T002, T003 (Fase 1) tocan archivos distintos y no dependen entre sí.
- Dentro de cada historia, la tarea de tests (`[P]`) y las tareas de frontend de red/tipos
  (`[P]`) pueden avanzar en paralelo a la implementación del backend, ya que ambas leen el
  contrato de `contracts/favorites-api.md` en lugar de depender del código del backend.

---

## Ejemplo de ejecución en paralelo: Fase 1

```bash
Task: "Migración Alembic: agregar is_favorite y level a projects"
Task: "Agregar is_favorite: bool y level: Optional[int] al modelo Project en core/database/models.py"
Task: "Agregar id/favorite a ProjectResponse y favorite/level/extras a HistoryEntry en ensemble_project_models.py"
```

---

## Estrategia de implementación

### MVP (Historias 1 y 2)

1. Completar Fase 1 (Fundamentos).
2. Completar Fase 2 (US1 — marcar). Verificable con `curl` aunque la pestaña de favoritos
   todavía no exista.
3. Completar Fase 3 (US2 — listar). En este punto el flujo "marcar y recuperar sin volver a
   girar" ya está completo end-to-end, con nivel y extras incluidos: **este es el MVP real
   de la spec**.
4. **Parar y validar** con `quickstart.md` antes de continuar.

### Entrega incremental

1. Fase 1 → base lista.
2. Fase 2 (US1) → demo por API.
3. Fase 3 (US2) → demo completa en la interfaz (MVP).
4. Fase 4 (US3) → mejora de mantenimiento de la lista, no bloquea nada anterior.
5. Fase 5 → pulido y verificación final.

---

## Notas

- No se generan tests unitarios separados por capa (repositorio/servicio) porque el patrón ya
  establecido en `002-interfaz-tragamonedas` prueba estas historias a nivel de contrato HTTP con
  dobles de prueba para la base de datos; se mantiene esa misma granularidad.
- `[P]` = archivos distintos, sin dependencias entre sí.
- `[USn]` mapea cada tarea a su historia de usuario para trazabilidad.
- Verificar que `uv run pytest` está en rojo antes de implementar cada endpoint nuevo y en
  verde después, según Constitution Principio III.
- `project_id: int = Path(gt=0)` en T010/T026 es la corrección del hallazgo `CN1` de
  `/speckit-analyze`: el plan ya afirmaba esta validación, ahora la tarea la hace explícita.
