# Tasks: Interfaz web tipo máquina tragamonedas

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md)
**Branch**: `002-interfaz-tragamonedas`

## Fase 1 — Backend: historial (Historia 3)

- [X] **T001** Añadir `list_recent(limit)` al repositorio, ordenado por `id` descendente con `limit` acotado → `core/ensemble_project/ensemble_project_repository.py`
- [X] **T002** Añadir `get_history(limit)` al servicio, devolviendo DTOs y no entidades del ORM → `core/ensemble_project/ensemble_project_service.py`
- [X] **T003** Definir el DTO `HistoryEntry` → `core/ensemble_project/api/ensemble_project_models.py`
- [X] **T004** Exponer `GET /api/v1/ensemble_project/history` con `limit` validado (`ge=1, le=50`, por defecto 10) → `core/ensemble_project/api/ensemble_project_router.py`
- [X] **T005** `[P]` Tests del historial: orden, límite máximo, lista vacía → `tests/test_fastapi_endpoints/test_history.py`

## Fase 2 — Andamiaje del frontend (bloquea la Fase 3)

- [X] **T006** Inicializar el proyecto Vite + React + TypeScript → `frontend/package.json`, `tsconfig.json`, `index.html`
- [X] **T007** Configurar el proxy de desarrollo `/api` → `http://localhost:9600` → `frontend/vite.config.ts`
- [X] **T008** Definir los tipos espejo de los DTOs del backend → `frontend/src/types.ts`
- [X] **T009** Implementar `api.ts` como única frontera de red, con manejo de errores tipado → `frontend/src/api.ts`
- [X] **T010** Escribir la hoja de estilos base con variables de tema y diseño responsivo → `frontend/src/styles.css`

## Fase 3 — Componentes (Historias 1 y 2)

- [X] **T011** `[P]` Componente `Reel`: valor, estado de bloqueo y animación de giro por CSS → `frontend/src/components/Reel.tsx`
- [X] **T012** `[P]` Componente `ResultCard`: combinación, nivel, extras y descripción → `frontend/src/components/ResultCard.tsx`
- [X] **T013** `[P]` Componente `History`: panel de las últimas ideas → `frontend/src/components/History.tsx`
- [X] **T014** Componente `SlotMachine`: compone los tres rodillos, el selector de nivel y el botón de girar → `frontend/src/components/SlotMachine.tsx`
- [X] **T015** `App.tsx`: estado del giro, bloqueo de rodillos, carga del catálogo, manejo de errores y actualización del historial → `frontend/src/App.tsx`
- [X] **T016** Bloquear el botón de girar mientras hay una petición en curso (evita el doble envío) → `frontend/src/App.tsx`

## Fase 4 — Integración y entrega

- [X] **T017** Montar los archivos estáticos del build en la raíz de FastAPI, sin ocultar `/api` → `core/main.py`
- [X] **T018** Añadir la etapa de build de Node al Dockerfile multi-stage → `Dockerfile`
- [X] **T019** Añadir el build del frontend al pipeline de CI → `.github/workflows/ci.yml`
- [X] **T020** Verificar el recorrido completo con la aplicación levantada: girar, bloquear, error y móvil

## Dependencias

```
Fase 1 (independiente) ─┐
Fase 2 ──▶ Fase 3 ──────┴──▶ Fase 4
```

## Reparto sugerido (6 integrantes)

| Integrante | Tareas |
|---|---|
| 1 | T001–T004 (historial en backend) |
| 2 | T005 (tests del historial) |
| 3 | T006–T010 (andamiaje del frontend) |
| 4 | T011, T012 (componentes de presentación) |
| 5 | T013, T014 (historial y máquina) |
| 6 | T017–T019 (integración, Docker y CI) |
