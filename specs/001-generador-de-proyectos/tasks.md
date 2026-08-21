# Tasks: Generador de ideas de proyectos asistido por IA

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md)
**Branch**: `001-generador-de-proyectos`

**Convención**: `[P]` = paralelizable (toca archivos disjuntos de las demás tareas `[P]` de la misma fase).
Cada tarea es un commit con mensaje `HU-XX: descripción`.

---

## Fase 1 — Cimientos (secuencial, bloquea todo lo demás)

- [X] **T001** Configurar `AppSettings` con pydantic-settings leyendo `.env` y variables de entorno → `core/settings/default.py`
- [X] **T002** Definir el modelo de datos SQLModel con claves foráneas explícitas y `unique` sobre los nombres de catálogo → `core/database/models.py`
- [X] **T003** Crear el engine, `init_db()` (crear base si no existe, crear tablas, sembrar) y la dependencia `get_db()` → `core/database/database.py`
- [X] **T004** Implementar la siembra idempotente desde `data/data.yaml` → `core/database/load_database_data.py`
- [X] **T005** Configurar Alembic y generar la migración inicial → `alembic/`
- [X] **T006** Crear la factory `boostrap()` de FastAPI y el registro de routers bajo `/api` y `/api/v1` → `core/main.py`, `core/routers.py`

## Fase 2 — Historia 4: catálogo (P3, habilitador de las demás)

- [X] **T007** `[P]` CRUD por tabla de catálogo → `core/database/crud.py`
- [X] **T008** `[P]` `CatalogRepository` con lectura completa y selección aleatoria → `core/catalog/catalog_repository.py`
- [X] **T009** Definir `CatalogService` como `ABC` e implementar `DefaultCatalogService` → `core/catalog/catalog_service.py`
- [X] **T010** Exponer los 6 endpoints de catálogo con `Depends(get_catalog_service)` → `core/catalog/api/catalog_router.py`
- [X] **T011** `[P]` Tests de contrato del router de catálogo con servicio simulado → `tests/test_fastapi_endpoints/test_catalog_router.py`
- [X] **T012** `[P]` Tests del servicio de catálogo con repositorio simulado → `tests/test_fastapi_endpoints/test_catalog_service.py`
- [X] **T013** `[P]` Tests del CRUD y de la siembra → `tests/test_database/`

## Fase 3 — Historia 5: gateway de IA intercambiable (P1, habilitador crítico)

- [X] **T014** Definir la interfaz `AIGateway` como `ABC` con `generate(prompt) -> str` → `core/ai_gateway/ai_gateway.py`
- [X] **T015** `[P]` Implementar `OllamaGateway` para desarrollo local → `core/ai_gateway/ollama_provider.py`
- [X] **T016** `[P]` Implementar `OpenAIGateway` (compatible LM Studio) → `core/ai_gateway/llmstudio_provider.py`
- [X] **T017** `[P]` Implementar `GroqGateway` para producción en capa gratuita → `core/ai_gateway/groq_provider.py`
- [X] **T018** `[P]` Implementar `StubGateway` determinístico para tests y modo degradado → `core/ai_gateway/stub_provider.py`
- [X] **T019** Implementar `get_ai_gateway()` que resuelve el proveedor según `AI_PROVIDER` y cae al stub si falta configuración → `core/ai_gateway/factory.py`
- [X] **T020** Implementar `ProjectGeneratorAIGateway`: selección estructurada de candidato y redacción de la descripción → `core/ensemble_project/ensemble_project_ai_gatway_service.py`
- [X] **T021** `[P]` Tests del factory: cada valor de `AI_PROVIDER` devuelve la clase correcta; valor desconocido cae al stub → `tests/test_ai_gateway/test_factory.py`

## Fase 4 — Historias 1, 2 y 3: generación de proyectos

- [X] **T022** Definir los DTOs de entrada y salida con cotas explícitas (`level` `ge=1 le=5`) → `core/ensemble_project/api/ensemble_project_models.py`
- [X] **T023** Implementar la resolución get-or-create de valores de catálogo → `core/ensemble_project/api/ensemble_project_validation.py`
- [X] **T024** Implementar `EnsembleProjectRepository.save_project` con sus extras y truncado de la descripción a 500 caracteres → `core/ensemble_project/ensemble_project_repository.py`
- [X] **T025** Implementar `ProjectGeneratorService.generate_random` (Historia 1) → `core/ensemble_project/ensemble_project_service.py`
- [X] **T026** Implementar `ProjectGeneratorService.generate_by_level` y la regla `extras = nivel * 2` (Historia 2) → mismo archivo
- [X] **T027** Implementar `ProjectGeneratorService.generate_by_value` con relleno aleatorio de campos vacíos (Historia 3) → mismo archivo
- [X] **T028** Exponer los 3 endpoints de generación con inyección del servicio → `core/ensemble_project/api/ensemble_project_router.py`
- [X] **T029** `[P]` Tests de `generate_project_totally_random`: contrato, camino feliz y catálogo vacío → `tests/test_fastapi_endpoints/test_generate_project_totally_random.py`
- [X] **T030** `[P]` Tests de `generate_project_by_level`: nivel válido, fuera de rango y conteo de extras → `tests/test_fastapi_endpoints/test_generate_project_by_level.py`
- [X] **T031** `[P]` Tests de `generate_project_by_value`: valor fijado, valor nuevo y combinación inviable → `tests/test_fastapi_endpoints/test_generate_project_by_value.py`

## Fase 5 — Robustez y cierre

- [X] **T032** Endpoint `/api/health` → `core/health/api/health.py`
- [X] **T033** `[P]` Test de salud → `tests/test_fastapi_endpoints/test_health.py`
- [X] **T034** Marcar los tests que requieren servicios vivos como `@pytest.mark.integration` y excluirlos de la ejecución por defecto → `pyproject.toml`, `tests/test_integration/`
- [X] **T035** Manejo del modo degradado: si el proveedor de IA falla, responder con la descripción de respaldo y registrar el incidente → `core/ensemble_project/ensemble_project_ai_gatway_service.py`
- [X] **T036** Documentar los endpoints en `docs/endpoints.md` y en el README

## Dependencias

```
Fase 1  ──▶ Fase 2 ──┐
        └──▶ Fase 3 ──┴──▶ Fase 4 ──▶ Fase 5
```

- La Fase 4 depende de que existan el catálogo (Fase 2) y el gateway (Fase 3).
- Dentro de cada fase, las tareas `[P]` pueden repartirse entre integrantes distintos.

## Reparto sugerido (6 integrantes)

| Integrante | Tareas |
|---|---|
| 1 | T001–T006 (cimientos) |
| 2 | T007–T010 (catálogo) |
| 3 | T014–T019 (gateway y factory) |
| 4 | T022–T028 (generación) |
| 5 | T011–T013, T021 (tests de catálogo y factory) |
| 6 | T029–T034 (tests de generación y salud) |
