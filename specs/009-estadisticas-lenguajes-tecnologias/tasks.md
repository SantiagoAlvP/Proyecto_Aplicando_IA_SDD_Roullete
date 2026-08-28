# Tasks: Estadísticas de lenguajes y tecnologías más propuestas

**Input**: Design documents from `/specs/009-estadisticas-lenguajes-tecnologias/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Task list includes contract and integration checks for the user stories to keep implementation test-first and independently verifiable.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the existing app architecture and align the stats feature with the current backend/frontend contracts.

- [X] T001 Review the current project generation flow in core/ensemble_project/api/ensemble_project_router.py, core/ensemble_project/ensemble_project_repository.py, and core/database/models.py to confirm the statistics source of truth
- [X] T002 [P] Define the shared statistics response shape in core/ensemble_project/api/ensemble_project_models.py and frontend/src/types.ts so backend and frontend agree on the contract
- [ ] T003 [P] Map the statistics feature into the existing app structure and confirm the UI placement in frontend/src/App.tsx and frontend/src/components/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the read-only aggregation pipeline and API boundary before story implementation.

- [ ] T004 Implement the aggregation query in core/database/crud.py to count languages, technologies, and addons across the project history
- [ ] T005 [P] Implement repository-level stats aggregation in core/ensemble_project/ensemble_project_repository.py and normalize the result into ranked entries
- [ ] T006 [P] Add the service method in core/ensemble_project/ensemble_project_service.py that exposes the aggregated statistics and preserves the current read-only behavior
- [ ] T007 [P] Register the GET /api/v1/ensemble_project/statistics endpoint in core/ensemble_project/api/ensemble_project_router.py with validation for the limit parameter
- [ ] T008 [P] Add the client call in frontend/src/api.ts for the statistics endpoint and prepare the types used by the UI

**Checkpoint**: Foundation ready - statistics data can now be requested from backend and consumed by the frontend without touching generation logic.

---

## Phase 3: User Story 1 - Consultar el ranking de lenguajes y tecnologías más repetidos (Priority: P1) 🎯 MVP

**Goal**: Expose a ranking of the most frequent languages and technologies in the generated project history.

**Independent Test**: Generate several projects with repeated combinations and verify that the statistics endpoint returns the correct ordering and counts.

### Tests for User Story 1

- [ ] T010 [P] [US1] Add contract test for GET /api/v1/ensemble_project/statistics in tests/test_fastapi_endpoints/test_statistics.py
- [ ] T011 [P] [US1] Add integration test for repeated project-generation history in tests/test_integration/test_statistics_flow.py

### Implementation for User Story 1

- [ ] T012 [US1] Aggregate counts for language/technology/addon occurrences in core/database/crud.py and core/ensemble_project/ensemble_project_repository.py
- [ ] T013 [US1] Return ranked and fully serialized statistics from core/ensemble_project/ensemble_project_service.py
- [ ] T014 [US1] Expose the endpoint response contract in core/ensemble_project/api/ensemble_project_models.py for total count, category, label, and rank
- [ ] T015 [US1] Render the ranking in the main app flow via frontend/src/App.tsx and a dedicated stats panel component in frontend/src/components/StatisticsPanel.tsx
- [ ] T016 [US1] Handle empty-history and invalid-limit states in the backend and the UI without breaking the rest of the experience

**Checkpoint**: At this point, User Story 1 should be fully functional and independently testable.

---

## Phase 4: User Story 2 - Comparar tendencias entre tecnologías y lenguajes (Priority: P2)

**Goal**: Show not only frequency but also relative share so the user can compare how dominant each option is.

**Independent Test**: Verify that the statistics view includes both absolute counts and relative percentages for the same set of categories.

### Tests for User Story 2

- [ ] T020 [P] [US2] Extend the statistics contract test to assert share and ordering in tests/test_fastapi_endpoints/test_statistics.py
- [ ] T021 [P] [US2] Add a frontend rendering test for percentage display in frontend/src/components/StatisticsPanel.tsx or a related test file

### Implementation for User Story 2

- [ ] T022 [US2] Calculate share per category and sort by count descending in core/ensemble_project/ensemble_project_repository.py and core/ensemble_project/ensemble_project_service.py
- [ ] T023 [US2] Update the frontend statistics panel to display count, share, and category labels in a clear ranked layout in frontend/src/components/StatisticsPanel.tsx
- [ ] T024 [US2] Add empty-state and category comparison behavior for low-volume or uneven distributions in frontend/src/App.tsx

**Checkpoint**: At this point, User Stories 1 and 2 work independently and can be validated together.

---

## Phase 5: User Story 3 - Revisar la evolución de las propuestas (Priority: P3)

**Goal**: Let the developer understand whether the system is trending toward certain technologies over time or across the full project history.

**Independent Test**: Generate projects in different moments and verify that the dashboard reflects the overall dominant values without requiring a full regeneration sequence.

### Tests for User Story 3

- [ ] T030 [P] [US3] Add a time-window or history-scope test for statistics in tests/test_integration/test_statistics_flow.py
- [ ] T031 [P] [US3] Add a UI test covering the historical/dominant view in frontend/src/components/StatisticsPanel.tsx or the relevant React test setup

### Implementation for User Story 3

- [ ] T032 [US3] Expose a scoped history summary in the backend so the statistics view can distinguish total history from recent trends in core/ensemble_project/ensemble_project_service.py
- [ ] T033 [US3] Add the trend toggle or summary section in frontend/src/App.tsx and frontend/src/components/StatisticsPanel.tsx for total-vs-recent comparison
- [ ] T034 [US3] Validate the state transitions for empty, recent-only, and mixed historical data without breaking the existing app flow

**Checkpoint**: All user stories are now independently functional and the feature is ready for polish.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final QA checks and small consistency improvements across backend, frontend, and docs.

- [ ] T040 [P] Review all stats response fields for naming consistency across core/ensemble_project/api/ensemble_project_models.py and frontend/src/types.ts
- [ ] T041 [P] Run the relevant backend tests for the feature and confirm the API remains stable for the rest of the app in tests/test_fastapi_endpoints/
- [ ] T042 [P] Run the frontend build and ensure the stats panel integrates cleanly with the current app shell in frontend/
- [ ] T043 Run the quickstart validation from specs/009-estadisticas-lenguajes-tecnologias/quickstart.md and document any follow-up edge cases before implementation is closed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational completion and is the default MVP.
- **User Story 2 (Phase 4)**: Depends on User Story 1 and can be delivered independently after the core ranking exists.
- **User Story 3 (Phase 5)**: Depends on User Story 2 and extends the analysis with trend context.
- **Polish (Phase 6)**: Depends on all desired stories being complete.

### User Story Dependencies

- **US1**: Can start after Foundational and is the primary value delivery.
- **US2**: Can proceed after US1, but it remains independently testable with the existing stats API.
- **US3**: Builds on US1/US2, but should remain optional if the MVP is restricted to the core ranking.

### Parallel Opportunities

- T002 and T003 can run in parallel during Setup.
- T005, T006, T007, and T008 can execute in parallel after the data contract is agreed.
- T010 and T011 can run in parallel for US1.
- T020 and T021 can run in parallel for US2.
- T030 and T031 can run in parallel for US3.
- T040, T041, and T042 can be done in parallel during polish if the rest of the feature is already stable.

---

## Parallel Example: User Story 1

```bash
# Launch contract and integration checks together
Task: "Add contract test for GET /api/v1/ensemble_project/statistics in tests/test_fastapi_endpoints/test_statistics.py"
Task: "Add integration test for repeated project-generation history in tests/test_integration/test_statistics_flow.py"

# Launch aggregation tasks together
Task: "Aggregate counts for language/technology/addon occurrences in core/database/crud.py"
Task: "Expose the endpoint response contract in core/ensemble_project/api/ensemble_project_models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate the ranking endpoint and UI in isolation
5. Extend with User Story 2 if additional comparison value is needed

### Incremental Delivery

- Ship the ranking endpoint and dashboard before adding trend/detail comparison.
- Leave US3 as a follow-up enhancement if time or scope constraints appear.
- Keep the backend read-only and the UI stateful in a single place to reduce regressions.
