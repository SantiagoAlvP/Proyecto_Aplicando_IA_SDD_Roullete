# Tasks: Despliegue continuo en la nube

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md)
**Branch**: `004-despliegue-continuo`

## Fase 1 — Preparar la aplicación para la nube (bloquea el resto)

- [X] **T001** Aceptar `DATABASE_URL` completa además de los componentes separados, y normalizar el esquema `postgres://` a `postgresql://` → `core/settings/default.py`
- [X] **T002** Escuchar en el puerto indicado por la variable `PORT` en lugar de un puerto fijo → `project_jackpot.py`
- [X] **T003** Arrancar en modo degradado, con advertencia en el log, cuando no haya proveedor de IA configurado → `core/ai_gateway/factory.py`
- [X] **T004** Servir el frontend compilado desde la raíz sin ocultar las rutas de `/api` → `core/main.py`
- [X] **T005** Garantizar que `/api/health` responde sin consultar la base de datos → `core/health/api/health.py`

## Fase 2 — Empaquetado

- [X] **T006** Reescribir el Dockerfile como multi-stage: etapa Node para compilar el frontend, etapa Python para el runtime → `Dockerfile`
- [X] **T007** Crear `entrypoint.sh`: aplicar migraciones, sembrar el catálogo y lanzar uvicorn en `$PORT`; abortar si una migración falla → `entrypoint.sh`
- [X] **T008** Añadir `.dockerignore` para excluir `node_modules`, `.venv`, `.git` y artefactos de test → `.dockerignore`
- [X] **T009** Actualizar `docker-compose.yml` para desarrollo local con Ollama, y documentar la diferencia con producción → `docker-compose.yml`

## Fase 3 — Pipeline de CI

- [X] **T010** Job de calidad: `uv sync`, `pytest`, `ruff check`, `ruff format --check`, `ty check` → `.github/workflows/ci.yml`
- [X] **T011** `[P]` Job de seguridad: gitleaks y pip-audit → `.github/workflows/ci.yml`
- [X] **T012** `[P]` Job de frontend: `npm ci` y `npm run build` → `.github/workflows/ci.yml`
- [X] **T013** `[P]` Job de Docker: construir la imagen para verificar que el Dockerfile es válido → `.github/workflows/ci.yml`

## Fase 4 — Plataforma

- [X] **T014** Crear `railway.json` con el comando de arranque, la ruta de verificación de salud y la política de reinicio → `railway.json`
- [X] **T015** Documentar el procedimiento de despliegue: crear el proyecto, añadir PostgreSQL, configurar variables y obtener la URL pública → `docs/deployment.md`
- [X] **T016** Documentar el contrato completo de variables de entorno → `.env.example`

## Fase 5 — Verificación

- [X] **T017** Prueba de humo posterior al despliegue: `/api/health` responde `200`
- [X] **T018** Verificar que la raíz sirve el frontend y que `/api/docs` sirve la documentación, en el mismo dominio
- [X] **T019** Verificar que una generación funciona de extremo a extremo contra el proveedor de IA de producción
- [X] **T020** Verificar que un CI en rojo impide el despliegue

## Dependencias

```
Fase 1 ──▶ Fase 2 ──▶ Fase 4 ──▶ Fase 5
Fase 3 (paralela a la Fase 2)
```

## Reparto sugerido (6 integrantes)

| Integrante | Tareas |
|---|---|
| 1 | T001–T003 (configuración para la nube) |
| 2 | T004, T005 (estáticos y salud) |
| 3 | T006–T009 (empaquetado) |
| 4 | T010 (job de calidad) |
| 5 | T011–T013 (jobs de seguridad, frontend y Docker) |
| 6 | T014–T016 (plataforma y documentación) |
