# Tasks: Compartir proyectos mediante enlace público (HU-20)

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md) · [data-model.md](./data-model.md) · [contracts/shared-project-api.md](./contracts/shared-project-api.md) · [research.md](./research.md)
**Branch**: `020-compartir-enlace-publico`

**Tests**: obligatorios — la constitución (Principio III) exige ciclo Rojo→Verde por historia; cada endpoint nuevo trae test de contrato, camino feliz y error.

## Formato: `- [ ] [ID] [P?] [Story?] Descripción con ruta`

- **[P]**: paralelizable (archivos disjuntos, sin dependencia pendiente)
- **[Story]**: historia dueña de la tarea (US1/US2/US3 según spec.md)

---

## Phase 1: Setup

- [X] T001 Verificar la línea base en verde antes de tocar código: `uv run pytest -q`, `uv run ruff check`, `uv run ruff format --check`, `uv run ty check`

---

## Phase 2: Foundational (bloquea todas las historias)

**⚠️ CRITICAL**: ninguna historia empieza hasta completar esta fase.

- [X] T002 Escribir tests Rojo de esquema: proyecto nuevo persiste `share_token` único, `level` y `created_at`; `get_by_share_token` lo recupera → `tests/test_database/test_crud.py`
- [X] T003 Añadir columnas `share_token` (única, indexada), `level` (anulable) y `created_at` al modelo `Project` → `core/database/models.py`
- [X] T004 Crear migración Alembic que añade las tres columnas y hace backfill de `share_token` con `secrets.token_urlsafe(12)` para filas previas (FR-007); niveles legados quedan `NULL` → `alembic/versions/`
- [X] T005 Extender `ProjectCRUD.create` para generar token y persistir nivel, y añadir `get_by_share_token`; hacer pasar los tests de T002 → `core/database/crud.py`

**Checkpoint**: `docker compose up api postgres` aplica la migración al arrancar; todo proyecto, antiguo o nuevo, tiene token.

---

## Phase 3: User Story 1 — Abrir un enlace compartido y ver el proyecto (Priority: P1) 🎯 MVP

**Goal**: `{origin}/proyecto/{token}` muestra combinación, nivel, extras y descripción en solo lectura, sin sesión ni acciones previas, con CTA hacia la máquina.

**Independent Test**: tomar el token de cualquier proyecto existente, abrir su enlace y comprobar el contenido completo sin interactuar.

### Tests for User Story 1

- [X] T006 `[P]` `[US1]` Tests Rojo del contrato: `GET shared/{token}` devuelve 200 con forma completa, 404 con mensaje neutro para token inexistente, 422 para token fuera de cotas, y nunca filtra detalles internos → `tests/test_fastapi_endpoints/test_shared_project.py`

### Implementation for User Story 1

- [X] T007 `[US1]` Definir DTO `SharedProjectResponse` (share_token, combinación, extras, level anulable, description con relleno legible) → `core/ensemble_project/api/ensemble_project_models.py`
- [X] T008 `[US1]` Añadir `get_by_share_token` al repositorio: carga proyecto + catálogos + extras y lo mapea a DTO (patrón `_name_of` para legados) → `core/ensemble_project/ensemble_project_repository.py`
- [X] T009 `[US1]` Implementar `get_shared_project(token)` en el servicio con excepción de dominio para "no encontrado" → `core/ensemble_project/ensemble_project_service.py`
- [X] T010 `[US1]` Exponer `GET /ensemble_project/shared/{share_token}` con path param acotado (`min_length=10, max_length=64`, patrón `^[A-Za-z0-9_-]+$`) y traducción del error de dominio a 404 neutro; hacer pasar T006 → `core/ensemble_project/api/ensemble_project_router.py`
- [X] T011 `[P]` `[US1]` Definir tipo `SharedProject` espejo y cliente `api.sharedProject(token)` → `frontend/src/types.ts`, `frontend/src/api.ts`
- [X] T012 `[US1]` Crear la vista pública de solo lectura: combinación completa, nivel (texto neutral si es `null`), extras, descripción con contenedor con scroll y CTA "crea el tuyo" hacia `/` (FR-002, FR-003, FR-009) → `frontend/src/components/SharedProject.tsx`
- [X] T013 `[US1]` Detectar `pathname` `/proyecto/{token}` en el arranque y renderizar la vista pública sin añadir librería de routing (D-03) → `frontend/src/App.tsx`

**Checkpoint**: un enlace válido funciona de punta a punta sin haber tocado ResultCard ni History.

---

## Phase 4: User Story 2 — Obtener y copiar el enlace desde la interfaz (Priority: P2)

**Goal**: "Compartir" sobre el resultado recién generado y sobre cada entrada del historial entrega el enlace copiado, con fallback visible si el portapapeles está bloqueado.

**Independent Test**: generar un proyecto (o usar el historial), pulsar compartir, pegar el enlace y comprobar que abre ese mismo proyecto.

### Tests for User Story 2

- [X] T014 `[P]` `[US2]` Tests Rojo: cada entrada de `GET /history` y cada respuesta `POST /generate_*` incluye `share_token` (y `level`) → `tests/test_fastapi_endpoints/test_history.py`

### Implementation for User Story 2

- [X] T015 `[US2]` Ampliar `HistoryEntry` y `ProjectResponse` con `share_token` (+`level` anulable) y poblarlos desde el repositorio (`list_recent`, `save_project`); hacer pasar T014 → `core/ensemble_project/api/ensemble_project_models.py`, `core/ensemble_project/ensemble_project_repository.py`
- [X] T016 `[P]` `[US2]` Componente `ShareButton`: construye `{origin}/proyecto/{token}`, copia con `navigator.clipboard`, segundo intento vía `textarea` + `execCommand`, confirmación visual breve; nunca muestra error crudo (FR-005, D-06) → `frontend/src/components/ShareButton.tsx`
- [X] T017 `[US2]` Integrar `ShareButton` en la tarjeta de resultado y en cada entrada del historial (FR-004) → `frontend/src/components/ResultCard.tsx`, `frontend/src/components/History.tsx`
- [X] T018 `[US2]` Estilos del botón y de la confirmación, coherentes con el tema actual → `frontend/src/styles.css`

**Checkpoint**: emitir un enlace toma dos interacciones o menos (SC-002).

---

## Phase 5: User Story 3 — Enlaces rotos con salida digna (Priority: P3)

**Goal**: cualquier enlace roto, manipulado o mal formado muestra una página amigable "Proyecto no disponible" con salida hacia la máquina, jamás texto técnico.

**Independent Test**: abrir enlaces con token inexistente y mal formado; ambos muestran la página amigable.

### Implementation for User Story 3

- [X] T019 `[US3]` Estado "no disponible" dentro de la vista pública: cubre 404 del API, fallo de red y token con formato inválido detectado en cliente (sin llamar al API), siempre con CTA hacia `/` (FR-008) → `frontend/src/components/SharedProject.tsx`
- [X] T020 `[US3]` Recorrer los escenarios negativos del quickstart (§3) y verificar que ninguna respuesta filtra stack trace, rutas ni nombres de tablas → `specs/020-compartir-enlace-publico/quickstart.md`

**Checkpoint**: las tres historias funcionan de forma independiente.

---

## Phase 6: Polish & Cross-Cutting

- [X] T021 `[P]` Revisión responsive a 360 px de la vista pública y del botón compartir (edge case móvil, SC/FR-010) → `frontend/src/styles.css`
- [X] T022 Ejecutar la validación completa del quickstart y las puertas de calidad: `uv run pytest -q && uv run ruff check && uv run ruff format --check && uv run ty check` y `cd frontend && npm run build`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Fase 1 ──▶ Fase 2 (Foundational) ──┬──▶ Fase 3 (US1, MVP)
                                   ├──▶ Fase 4 (US2)   ← independiente de US1
                                   └──▶ (tras US1) Fase 5 (US3)
                                              │
                                    Fase 6 tras US1–US3
```

- **Setup (Fase 1)**: inmediato.
- **Foundational (Fase 2)**: bloquea US1 y US2 (ambas necesitan tokens persistentes).
- **US1 y US2**: independientes entre sí; paralelizables por dos integrantes.
- **US3**: depende de US1 (extiende su vista).
- **Polish**: al cierre de todas las historias.

### Within Each Story

Tests Rojo primero → DTO/modelos → repositorio → servicio → endpoint → frontend.

### Parallel Opportunities

- T002 puede escribirse en paralelo con T001 (solo lectura).
- Dentro de Fase 3: backend (T007–T010) y frontend (T011–T013) son cadenas disjuntas; dos integrantes.
- T016 (ShareButton) es paralelo a todo el backend de US2.
- T021 puede hacerse mientras se ejecuta la validación manual de US3.

---

## Implementation Strategy

- **MVP First**: Fases 1–3 → demo: enlace compartido ya enseña proyectos (valor central HU-20). Validar US1 sola antes de continuar.
- **Incremental**: + US2 cierra el lado emisor; + US3 endurece la percepción ante errores.
- **Un ticket = un commit** con mensaje `HU-20: descripción en imperativo`.

## Notes

- Los tests marcados Rojo deben fallar antes de implementarse y pasar después (Principio III).
- Nada de secretos ni `allow_origins=["*"]`; el 404 público usa mensaje neutro con correlación en log.
