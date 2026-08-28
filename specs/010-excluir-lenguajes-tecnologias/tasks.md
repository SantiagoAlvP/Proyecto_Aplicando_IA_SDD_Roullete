# Tasks: Excluir lenguajes y tecnologías antes de girar

**Input**: Design documents from `/specs/010-excluir-lenguajes-tecnologias/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [quickstart.md](./quickstart.md), [contracts/generation-exclusions.md](./contracts/generation-exclusions.md)

**Tests**: Se incluyen pruebas porque la especificación exige validación independiente de cada historia y la constitución del proyecto exige el ciclo Red -> Green -> Refactor.

**Organization**: Las tareas están agrupadas por historia de usuario y ordenadas por dependencia para permitir entregas incrementales.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparar los tipos y la superficie de trabajo sin alterar todavía el comportamiento de generación.

- [X] T001 [P] Añadir los tipos `ExcludedCatalogChoice` y `ExcludedCatalog` para distinguir lenguajes/tecnologías excluibles de addons en `frontend/src/types.ts`
- [X] T002 [P] Documentar la clave estable de `localStorage`, el formato persistido y la compatibilidad hacia atrás en `frontend/src/App.tsx`
- [X] T003 [P] Añadir el campo opcional `excluded` con cota explícita de longitud y número de elementos a `GenerateProjectByValueRequest` y `Level` en `core/ensemble_project/api/ensemble_project_models.py`

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Crear el filtro común que usará tanto la generación por valores como la generación por nivel, incluidos los extras.

- [X] T004 Implementar la normalización case-insensitive de nombres excluidos, eliminando vacíos, duplicados, addons y valores desconocidos en `core/ensemble_project/ensemble_project_service.py`
- [X] T005 Implementar la selección de valores elegibles para lenguajes y tecnologías, manteniendo addons sin filtrar, en `core/ensemble_project/ensemble_project_service.py`
- [X] T006 Actualizar `ProjectGeneratorService.generate_by_value()` y `_build_best_project()` para aplicar exclusiones a valores principales y extras en `core/ensemble_project/ensemble_project_service.py`
- [X] T007 [P] Añadir los parámetros `excluded` a `generateByValue()` y `generateByLevel()` en `frontend/src/api.ts`, preservando payloads que no los envíen
- [X] T008 [P] Añadir pruebas unitarias del filtro para exclusiones vacías, duplicadas, desconocidas, de addons y aplicadas a extras en `tests/test_ensemble_project/test_exclusions.py`

## Phase 3: User Story 1 - Excluir tecnologías antes de generar (Priority: P1)

**Goal**: El usuario puede bloquear una o varias tecnologías y ninguna aparece en los rodillos, la propuesta ni sus extras.

**Independent Test**: Marcar dos tecnologías, girar y comprobar que ninguna aparece en los tres valores principales ni en los extras; repetir sin exclusiones y comprobar que el flujo base permanece operativo.

### Tests for User Story 1

- [X] T009 [P] [US1] Añadir pruebas de contrato para `excluded` en `tests/test_fastapi_endpoints/test_generate_project_by_value.py`
- [X] T010 [P] [US1] Verificar que una tecnología excluida no se persiste en el proyecto generado ni en sus extras en `tests/test_fastapi_endpoints/test_generate_project_by_value.py`

### Implementation for User Story 1

- [X] T011 [US1] Filtrar las opciones de tecnología mostradas en los selectores de reels, manteniendo visibles los controles de alternancia, en `frontend/src/App.tsx` y `frontend/src/components/SlotMachine.tsx`
- [X] T012 [US1] Enviar la lista combinada de exclusiones al endpoint correcto durante `spin()` sin modificar los locks existentes en `frontend/src/App.tsx`
- [X] T013 [US1] Deshabilitar el botón de giro cuando no exista ninguna tecnología elegible y mostrar un estado accionable en `frontend/src/components/SlotMachine.tsx`

## Phase 4: User Story 2 - Excluir lenguajes de forma persistente (Priority: P1)

**Goal**: El usuario puede bloquear uno o varios lenguajes, conservar la decisión entre recargas y evitar que aparezcan también en extras.

**Independent Test**: Bloquear un lenguaje, recargar la página, generar varias propuestas y comprobar que el lenguaje no aparece en ningún resultado ni extra.

### Tests for User Story 2

- [X] T014 [P] [US2] Añadir pruebas de generación por nivel con lenguajes excluidos y verificar candidatos principales y extras en `tests/test_fastapi_endpoints/test_generate_project_by_level.py`
- [ ] T015 [P] [US2] Añadir una prueba de integración de persistencia, recarga y recuperación del estado de exclusiones en `frontend/src/App.tsx`

### Implementation for User Story 2

- [X] T016 [US2] Cargar las exclusiones válidas desde `localStorage`, guardar cambios de forma deduplicada y descartar datos malformados en `frontend/src/App.tsx`
- [X] T017 [US2] Aplicar el filtro de lenguajes a cada candidato de la generación por nivel y a cada extra en `core/ensemble_project/ensemble_project_service.py`
- [X] T018 [US2] Mantener el estado de los selectores coherente cuando se excluye el valor actualmente seleccionado en `frontend/src/App.tsx` y `frontend/src/components/Reel.tsx`

## Phase 5: User Story 3 - Ajustar y limpiar exclusiones (Priority: P2)

**Goal**: El usuario puede retirar una exclusión individual o borrar todas para recuperar el catálogo normal.

**Independent Test**: Excluir un valor, retirarlo y comprobar que vuelve a aparecer como elegible; después usar “Limpiar” y comprobar que las tres categorías recuperan su catálogo original.

### Tests for User Story 3

- [ ] T019 [P] [US3] Verificar que retirar una exclusión vuelve a habilitar el valor para futuras generaciones en `tests/test_fastapi_endpoints/test_generate_project_by_value.py`
- [ ] T020 [P] [US3] Verificar que limpiar todas las exclusiones elimina el estado persistido y restaura la interacción de la máquina en `frontend/src/App.tsx`

### Implementation for User Story 3

- [X] T021 [US3] Implementar los controles de activar/desactivar exclusiones por nombre y categoría en `frontend/src/components/SlotMachine.tsx`
- [X] T022 [US3] Implementar la acción “Limpiar” para vaciar el estado, actualizar `localStorage` y restaurar las opciones completas en `frontend/src/App.tsx`
- [X] T023 [US3] Cubrir la respuesta controlada cuando un cliente directo excluye toda una categoría, sin devolver un resultado prohibido, en `core/ensemble_project/api/ensemble_project_router.py` y `core/ensemble_project/ensemble_project_service.py`

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T024 [P] Revisar textos, etiquetas accesibles, estados disabled y navegación por teclado de los controles de exclusión en `frontend/src/components/SlotMachine.tsx` y `frontend/src/components/Reel.tsx`
- [X] T025 [P] Actualizar el contrato y la guía de validación con los códigos de error y el caso de categoría vacía en `specs/010-excluir-lenguajes-tecnologias/contracts/generation-exclusions.md` y `specs/010-excluir-lenguajes-tecnologias/quickstart.md`
- [X] T026 Ejecutar `uv run pytest -q`, `uv run ruff check`, `uv run ruff format --check`, `uv run ty check` y `npm run build` desde `frontend/` y registrar el resultado en `specs/010-excluir-lenguajes-tecnologias/quickstart.md`

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; define the shared request and state shapes.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP for technology exclusion.
- **User Story 2 (Phase 4)**: Depends on Foundational and extends the same filter to persistent language exclusions.
- **User Story 3 (Phase 5)**: Depends on the UI controls from US1/US2 and validates removal/reset behavior.
- **Polish (Phase 6)**: Depends on all desired stories being complete.

### User Story Dependencies

- **US1**: Independent after Foundational; delivers technology exclusions and the first complete spin path.
- **US2**: Independent at the service level after Foundational; reuses the same exclusion payload and persistence state.
- **US3**: Depends on the toggle controls delivered by US1/US2, but does not require new persistence or database schema.

### Parallel Opportunities

- T001, T002 and T003 can run in parallel during Setup.
- T007 and T008 can run in parallel with the foundational service work once the request shape is fixed.
- T009/T010 can run in parallel with T011/T012 because they target the backend contract and frontend flow separately.
- T014/T015 can run in parallel with T016/T017.
- T019/T020 can run in parallel with T021/T022.
- T024 and T025 can run in parallel after the stories are stable.

## Parallel Example: User Story 1

```text
Task: "Add contract tests for excluded technologies in tests/test_fastapi_endpoints/test_generate_project_by_value.py"
Task: "Filter technology options in frontend/src/App.tsx and frontend/src/components/SlotMachine.tsx"
Task: "Send excluded values through frontend/src/api.ts"
```

## Implementation Strategy

### MVP First (US1 + shared foundation)

1. Complete Phase 1 and Phase 2.
2. Complete US1 for technology exclusions, including main values, extras and the no-exclusions regression.
3. Validate the focused backend tests and `npm run build`.

### Incremental Delivery

1. Add persistent language exclusions in US2.
2. Add individual removal and “Limpiar” in US3.
3. Run the full quality gate and quickstart validation.

### Format Validation

Every task uses the required `- [ ] Txxx [P?] [USn?] description with an exact file path` format. Setup, foundational and polish tasks omit story labels; user-story tasks include exactly one `[USn]` label.
