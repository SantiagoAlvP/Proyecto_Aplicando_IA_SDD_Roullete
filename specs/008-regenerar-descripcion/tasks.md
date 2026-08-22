# Tasks: Regenerar la descripción de un proyecto existente

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md)
**Branch**: `008-regenerar-descripcion`

**Convención**: `[P]` = paralelizable cuando toca archivos disjuntos. Cada tarea debe ser un
commit con mensaje `HU-XX: descripción`.

## Fase 1 — Persistencia compatible

- [X] **T001** Añadir `level` al modelo `Project` con rango 1-5 y hacer que la creación de proyectos persista el nivel elegido → `core/database/models.py`, `core/ensemble_project/ensemble_project_repository.py`
- [X] **T002** Crear migración Alembic para añadir `projects.level`, backfill compatible de registros existentes y downgrade reversible → `alembic/versions/`
- [X] **T003** Añadir al CRUD la lectura de un proyecto con sus relaciones/extras y la actualización exclusiva de su descripción → `core/database/crud.py`
- [X] **T004** `[P]` Tests del modelo, migración y CRUD: nivel persistido, proyecto inexistente, update sin duplicar relaciones → `tests/test_database/`

## Fase 2 — Contratos y lógica de negocio

- [X] **T005** Definir el DTO de respuesta de regeneración con identificador, combinación, nivel, extras y descripción → `core/ensemble_project/api/ensemble_project_models.py`
- [X] **T006** Implementar la reconstrucción del proyecto persistido y el update de descripción sin crear entidades nuevas → `core/ensemble_project/ensemble_project_repository.py`
- [X] **T007** Implementar la regeneración en el servicio: cargar por id, construir contexto inmutable, validar 2-4 frases/<400 caracteres, garantizar diferencia y aplicar las decisiones de fallback/conservación → `core/ensemble_project/ensemble_project_service.py`
- [X] **T008** `[P]` Tests unitarios del servicio con advisor y repositorio simulados: contexto exacto, id inexistente, respuesta válida, inválida, repetida y fallo del proveedor → `tests/test_fastapi_endpoints/test_regenerate_description_service.py`

## Fase 3 — Endpoint y contrato HTTP

- [X] **T009** Exponer `POST /api/v1/ensemble_project/{project_id}/regenerate_description` con validación positiva del id, inyección del servicio y traducción a `200`, `404` y `422` → `core/ensemble_project/api/ensemble_project_router.py`
- [X] **T010** `[P]` Añadir tests de contrato y camino feliz: forma de respuesta, mismo id/combinación, una sola entrada de historial y no llamada a IA para `404`/`422` → `tests/test_fastapi_endpoints/test_regenerate_description.py`
- [X] **T011** Verificar que el endpoint queda cubierto por el rate limiting existente y documentar la ruta y códigos de estado → `docs/endpoints.md`, `docs/security.md`

## Fase 4 — Verificación

- [ ] **T012** Ejecutar migraciones y suite focalizada; después `uv run pytest -q`, `uv run ruff check`, `uv run ruff format --check` y `uv run ty check` → `tests/`, configuración del proyecto
- [ ] **T013** Confirmar con una prueba de integración que dos regeneraciones no crean proyectos ni extras y que la última escritura prevalece → `tests/test_integration/`

## Dependencias

```text
T001 ──▶ T002 ──▶ T003 ──▶ T006 ──▶ T007 ──▶ T009 ──▶ T010 ──▶ T012
                  └────▶ T004                  └────▶ T011
T005 ───────────────────────────────▶ T007
T008 ───────────────────────────────▶ T009
T012 ──▶ T013
```

T004, T005 y T008 pueden avanzar en paralelo cuando sus contratos estén acordados; T009
espera a la lógica del servicio y a sus pruebas unitarias. T013 requiere una base de datos
real y permanece marcado como integración.