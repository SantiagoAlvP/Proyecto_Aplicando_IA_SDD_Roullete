# Tasks: Verificar conexión a base de datos en el endpoint de salud (HU-22)

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md) · [data-model.md](./data-model.md) · [contracts/health-db-check-api.md](./contracts/health-db-check-api.md) · [research.md](./research.md)
**Branch**: `022-health-db-check`

**Tests**: obligatorios — la constitución (Principio III) exige ciclo Rojo→Verde por historia.

## Formato: `- [ ] [ID] [P?] [Story?] Descripción con ruta`

- **[P]**: paralelizable (archivos disjuntos, sin dependencia pendiente)
- **[Story]**: historia dueña de la tarea (US1/US2 según spec.md)

---

## Phase 1: Setup

- [x] T001 Verificar la línea base en verde antes de tocar código: `uv run pytest -q`, `uv run ruff check`, `uv run ruff format --check`, `uv run ty check`

---

## Phase 2: Foundational (bloquea todas las historias)

**⚠️ CRITICAL**: ninguna historia empieza hasta completar esta fase.

- [x] T002 Añadir función `check_db_connectivity(engine)` a `core/database/database.py`: ejecuta `SELECT 1` con timeout de 5s; devuelve `True` si OK, `False` si falla; captura excepciones sin exponerlas

**Checkpoint**: la función existe y puede ser importada; el comportamiento existente no cambia porque nadie la llama todavía.

---

## Phase 3: User Story 1 — Detectar base de datos caída en el health check (Priority: P1) 🎯 MVP

**Goal**: `/api/health` incluye `database.connected` y `database.configured` en la respuesta, verificando conectividad real a la base de datos.

**Independent Test**: simular DB no accesible y comprobar que `/api/health` devuelve `200` con `database.connected: false`.

### Tests for User Story 1

- [x] T003 `[US1]` Tests Rojo: DB conectada → `connected: true, configured: true`; DB caída → `connected: false, configured: true`; DB no configurada → `connected: false, configured: false`; health siempre `200` → `tests/test_health_db_check.py`

### Implementation for User Story 1

- [x] T004 `[US1]` Añadir dependencia `get_engine()` y modificar endpoint `health()` en `core/health/api/health.py`: llamar a `check_db_connectivity(engine)`, devolver `{"status": "healthy", "database": {"connected": ..., "configured": ...}}`; hacer pasar T003

**Checkpoint**: `/api/health` reporta el estado real de la DB; health siempre `200`.

---

## Phase 4: User Story 2 — Diagnóstico detallado de la base de datos (Priority: P2)

**Goal**: `/api/health/diagnostics` incluye `database.connected` y `database.configured` además del `using_platform_url` existente.

**Independent Test**: consultar `/api/health/diagnostics` con DB funcionando y caída, y verificar que `database.connected` refleja el estado.

### Tests for User Story 2

- [x] T005 `[P]` `[US2]` Tests Rojo: diagnostics con DB conectada → `connected: true`; con DB caída → `connected: false`; `using_platform_url` sigue presente → `tests/test_health_db_check.py`

### Implementation for User Story 2

- [x] T006 `[US2]` Añadir `connected` y `configured` al diccionario `database` del endpoint `diagnostics()` en `core/health/api/health.py`; hacer pasar T005

**Checkpoint**: las dos historias funcionan de forma independiente.

---

## Phase 5: Polish & Cross-Cutting

- [x] T007 Ejecutar la validación completa del quickstart y las puertas de calidad: `uv run pytest -q && uv run ruff check && uv run ruff format --check && uv run ty check` y `cd frontend && npm run build`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Fase 1 ──▶ Fase 2 (Foundational) ──┬──▶ Fase 3 (US1, MVP)
                                    └──▶ Fase 4 (US2)   ← independiente de US1
                                               │
                                     Fase 5 tras US1–US2
```

- **Setup (Fase 1)**: inmediato.
- **Foundational (Fase 2)**: bloquea US1 y US2 (ambas necesitan `check_db_connectivity`).
- **US1 y US2**: independientes entre sí; paralelizables.
- **Polish**: al cierre de ambas historias.

### Within Each Story

Tests Rojo primero → implementación → checkpoint.

### Parallel Opportunities

- T003 y T005 pueden escribirse en paralelo (tests del mismo archivo, pero cubren endpoints distintos).
- T004 y T006 tocan el mismo archivo (`health.py`) pero endpoints distintos; pueden ejecutarse en paralelo si se coordina la edición.

---

## Implementation Strategy

- **MVP First**: Fases 1–3 → demo: `/api/health` reporta `database.connected` real. Validar US1 sola antes de continuar.
- **Incremental**: + US2 añade el mismo campo al diagnóstico.
- **Un ticket = un commit** con mensaje `HU-22: descripción en imperativo`.

## Notes

- Los tests marcados Rojo deben fallar antes de implementarse y pasar después (Principio III).
- No se toca el frontend; la respuesta del health check se amplía con un campo nuevo.
- No hay migración DB; la verificación es una consulta `SELECT 1` sobre el engine existente.
- Health check siempre devuelve `200` (decisión D-03, Clarification Session 2026-08-25).
