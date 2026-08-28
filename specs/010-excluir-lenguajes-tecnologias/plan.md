# Implementation Plan: Excluir lenguajes y tecnologías antes de girar

**Branch**: `010-excluir-lenguajes-tecnologias` | **Date**: 2026-08-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-excluir-lenguajes-tecnologias/spec.md`

## Summary

Se añade una preferencia global de exclusión del catálogo para evitar que el generador proponga lenguajes o tecnologías que el desarrollador no desea aprender. La solución se integra con la rueda actual de elección sin introducir un nuevo dominio ni duplicar el catálogo: la interfaz mantiene la lista de exclusiones y, en cada tirada, filtra los valores disponibles antes de llamar a la generación.

La persistencia será local al navegador para cumplir la necesidad de “no volver a verlas” sin introducir sesión de usuario ni base de datos adicional. El frontend enviará la lista de exclusiones al servicio de generación, que la normalizará y aplicará a lenguajes y tecnologías de los rodillos y extras; los addons permanecerán siempre disponibles. Si no hay exclusiones, el comportamiento original seguirá intacto.

## Technical Context

**Language/Version**: Python 3.13 (backend) + TypeScript 5.x / React 19 (frontend)

**Primary Dependencies**: FastAPI, SQLModel, Pydantic v2, Vite, React 19

**Storage**: no cambio de esquema de base de datos; persistencia del estado de exclusión en localStorage del navegador, compatible con la ausencia de autenticación y con la política de “configuración global por perfil del cliente”

**Testing**: pytest para endpoints y servicio, plus frontend build verification via `npm run build`

**Target Platform**: web app current stack (FastAPI + React) running in the same browser session

**Project Type**: web application

**Performance Goals**: el filtro de catálogo se aplica en memoria y responde sin latencia perceptible; la operación no necesita llamadas al LLM ni a la base de datos

**Constraints**: no introducir tablas nuevas ni dependencias externas; la configuración de exclusiones debe ser reversible y no romper la generación ni el historial actual

**Scale/Scope**: 1 flujo nuevo de UI, 1 servicio de generación de proyectos con filtro, 1 pequeña capa de almacenamiento local y una ampliación aditiva de los payloads existentes

## Constitution Check

| Principio | Cumplimiento en este plan |
|---|---|
| I. SDD | La spec de la feature precede a la implementación. El plan y las tareas siguen la misma disciplina del repositorio. |
| II. Capas y SOLID | El comportamiento se modela como una preferencia de UI + un filtro de catálogo antes de la generación; la lógica de generación no toca almacenamiento ni atraviesa capas ajenas. |
| III. Test-First | Se añadirán pruebas del filtro de exclusiones y del caso sin exclusiones antes de cerrar la feature. |
| IV. Seguridad | Toda entrada de selección sigue validándose con Pydantic; no se exponen secretos ni se crean endpoints nuevos para un estado local. |
| V. Free-tier | No requiere nuevas dependencias ni servicios externos. |
| VI. Despliegue | No hay cambios de infraestructura ni de migración; la persistencia es local al navegador. |
| VII. YAGNI | Se evita un modelo de usuario, gestión de permisos o tabla de preferencias globales; no hay necesidad de un dominio propio si el requisito se resuelve con un filtro mínimo pero útil. |

**Resultado**: PASS — la solución usa la capa adecuada y evita complejidad que la spec no exige.

## Project Structure

### Documentation (this feature)

```text
specs/010-excluir-lenguajes-tecnologias/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
frontend/src/
├── App.tsx                        # manages excluded options + persisted preferences
├── api.ts                         # unchanged except optional filters if needed by backend contract
├── types.ts                       # add excluded catalog state type if necessary
├── components/
│   ├── SlotMachine.tsx            # expose excluded values in the selector UI
│   └── Reel.tsx                   # marks options as hidden/blocked by exclusion list
└── styles.css                     # add styles for exclusion badges/toggles

core/ensemble_project/
├── ensemble_project_service.py   # shared filter helper invoked before pick_random_base()
├── api/
│   └── ensemble_project_models.py # optional request fields for excluded values (if backend is made responsible)
└── api/ensemble_project_router.py # route accepts and forwards exclusions if needed
```

**Structure Decision**: the feature is resolved in the existing frontend flow and in the generation service, without creating a brand-new domain. The filter logic stays close to the places that already choose random catalog entries, so the `slot machine` behavior and the backend validation still line up.

## Design Decisions

**D-01 — localStorage as source of truth for the excluded list.** Since there is no authenticated user model in the repository, persisting exclusions in the browser is the smallest and least invasive way to keep them across sessions. It also matches the real requirement: “no quiero volver a ver esa tecnología” without multi-user complexity.

**D-02 — filter the catalog before a spin, not after generation.** If excluded names are removed before the random selection, the user cannot accidentally receive a forbidden stack in the final result. This is stronger than filtering only the output because it prevents excluded values from entering the candidate set at all.

**D-03 — keep the backend tolerant but deterministic.** If the UI sends deprecated names, duplicates, empty strings, or addon names, the backend ignores those entries. It never crashes generation; it applies valid language/technology exclusions and keeps the default flow when no exclusions exist.

**D-04 — no new schema when a UI preference is enough.** A dedicated database table would add migration, tests, and deployment work that the spec does not require for the first iteration. Local storage and client-side filtering satisfy the “persist across sessions” requirement without broadening scope.

## Complexity Tracking

*No project-level violation that requires explicit waiver. The feature stays within the existing architecture and avoids a second persistence model.*
