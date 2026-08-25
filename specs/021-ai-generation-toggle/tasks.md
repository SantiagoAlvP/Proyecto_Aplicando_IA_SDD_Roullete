# Tasks: Desactivar generación por IA mediante variable de entorno (HU-21)

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md) · [data-model.md](./data-model.md) · [contracts/ai-toggle-api.md](./contracts/ai-toggle-api.md) · [research.md](./research.md)
**Branch**: `021-ai-generation-toggle`

**Tests**: obligatorios — la constitución (Principio III) exige ciclo Rojo→Verde por historia.

## Formato: `- [ ] [ID] [P?] [Story?] Descripción con ruta`

- **[P]**: paralelizable (archivos disjuntos, sin dependencia pendiente)
- **[Story]**: historia dueña de la tarea (US1/US2/US3 según spec.md)

---

## Phase 1: Setup

- [X] T001 Verificar la línea base en verde antes de tocar código: `uv run pytest -q`, `uv run ruff check`, `uv run ruff format --check`, `uv run ty check`

---

## Phase 2: Foundational (bloquea todas las historias)

**⚠️ CRITICAL**: ninguna historia empieza hasta completar esta fase.

- [X] T002 Añadir campo `AI_GENERATION_ENABLED: bool = True` y property `ai_generation_enabled` a `AppSettings` → `core/settings/default.py`

**Checkpoint**: el setting existe y pydantic-settings parsea la env var correctamente; el comportamiento existente no cambia porque el default es `True`.

---

## Phase 3: User Story 1 — Activar el modo degradado (Priority: P1) 🎯 MVP

**Goal**: con `AI_GENERATION_ENABLED=false`, toda generación devuelve descripción de respaldo del stub sin llamar al proveedor de IA; el proyecto se persiste igual.

**Independent Test**: establecer `AI_GENERATION_ENABLED=false`, generar un proyecto y comprobar que la descripción viene del stub (texto template) y el gateway no fue contactado.

### Tests for User Story 1

- [X] T003 `[US1]` Tests Rojo: con toggle desactivado, `generate_description` devuelve descripción de respaldo y `choose_valid_project` acepta el primer candidato sin llamar al gateway → `tests/test_ai_toggle.py`

### Implementation for User Story 1

- [X] T004 `[US1]` Añadir check de `settings.ai_generation_enabled` en `AIProjectAdvisor`: cuando `False`, usar `self._fallback` (stub) en `generate_description` y `choose_valid_project`; hacer pasar T003 → `core/ensemble_project/ai_project_advisor.py`

**Checkpoint**: con `AI_GENERATION_ENABLED=false`, generar un proyecto produce descripción de respaldo, el gateway no se contacta, y el proyecto se persiste con todos sus campos.

---

## Phase 4: User Story 2 — Reactivar la generación por IA (Priority: P2)

**Goal**: con `AI_GENERATION_ENABLED=true` (o ausente), la generación usa el proveedor de IA configurado como hasta ahora.

**Independent Test**: generar un proyecto sin el toggle (default) y comprobar que el gateway es contactado (o que se usa el stub si no hay provider, que es el comportamiento existente).

### Tests for User Story 2

- [X] T005 `[P]` `[US2]` Tests Rojo: con toggle activado (default), `generate_description` llama al gateway real y `choose_valid_project` usa el gateway real → `tests/test_ai_toggle.py`

### Implementation for User Story 2

- [X] T006 `[US2]` Verificar que el camino default (`ai_generation_enabled=True`) mantiene el comportamiento existente: el gateway real se usa sin cambios → `core/ensemble_project/ai_project_advisor.py`

**Checkpoint**: con el default (sin env var o con `true`), la generación funciona como antes de HU-21.

---

## Phase 5: User Story 3 — Mensaje claro al usuario y diagnóstico (Priority: P2)

**Goal**: el endpoint `/api/health/diagnostics` indica si la IA está activada o desactivada; la descripción de respaldo es legible y de largo adecuado.

**Independent Test**: consultar `/api/health/diagnostics` con toggle activado y desactivado, y verificar que el campo `ai_generation_enabled` refleja el estado.

### Tests for User Story 3

- [X] T007 `[P]` `[US3]` Tests Rojo: diagnóstico devuelve `ai_generation_enabled: true` con default y `ai_generation_enabled: false` con toggle desactivado → `tests/test_ai_toggle.py`

### Implementation for User Story 3

- [X] T008 `[US3]` Añadir `"ai_generation_enabled": settings.ai_generation_enabled` al diccionario `ai` del endpoint de diagnóstico → `core/health/api/health.py`

**Checkpoint**: las tres historias funcionan de forma independiente.

---

## Phase 6: Polish & Cross-Cutting

- [X] T009 Ejecutar la validación completa del quickstart y las puertas de calidad: `uv run pytest -q && uv run ruff check && uv run ruff format --check && uv run ty check` y `cd frontend && npm run build`

---

## Dependencies & Execution Order

### Phase Dependencies

```
Fase 1 ──▶ Fase 2 (Foundational) ──┬──▶ Fase 3 (US1, MVP)
                                    ├──▶ Fase 4 (US2)   ← independiente de US1
                                    └──▶ Fase 5 (US3)   ← independiente de US1/US2
                                               │
                                     Fase 6 tras US1–US3
```

- **Setup (Fase 1)**: inmediato.
- **Foundational (Fase 2)**: bloquea US1, US2 y US3 (todas necesitan el setting).
- **US1, US2 y US3**: independientes entre sí; paralelizables.
- **Polish**: al cierre de todas las historias.

### Within Each Story

Tests Rojo primero → implementación → checkpoint.

### Parallel Opportunities

- T003 y T005 pueden escribirse en paralelo (tests del mismo archivo, pero cubren estados distintos).
- T007 es independiente de T003/T005.
- T004, T006 y T008 tocan archivos distintos y pueden ejecutarse en paralelo.

---

## Implementation Strategy

- **MVP First**: Fases 1–3 → demo: con `AI_GENERATION_ENABLED=false`, la generación produce descripciones de respaldo sin gastar cuota. Validar US1 sola antes de continuar.
- **Incremental**: + US2 confirma que el default no rompe nada; + US3 añade observabilidad al diagnóstico.
- **Un ticket = un commit** con mensaje `HU-21: descripción en imperativo`.

## Notes

- Los tests marcados Rojo deben fallar antes de implementarse y pasar después (Principio III).
- No se toca el frontend; la descripción de respaldo tiene la misma forma que la generada por IA.
- No hay migración DB; el toggle es una variable de entorno.
