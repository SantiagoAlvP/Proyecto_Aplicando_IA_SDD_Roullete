# Implementation Plan: Verificar conexión a base de datos en el endpoint de salud

**Branch**: `022-health-db-check` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Ampliar `/api/health` y `/api/health/diagnostics` para verificar la conectividad a PostgreSQL mediante una consulta ligera (`SELECT 1`). El health check siempre devuelve `200` (preservando compatibilidad con Railway), pero el cuerpo incluye `database.connected` para que el responsable detecte una base caída. Si la DB no está configurada, se reporta "no configurado" en lugar de "caído".

## Technical Context

**Language/Version**: Python 3.13 backend; TypeScript 5.9 / React 19 frontend (sin cambios frontend)
**Primary Dependencies**: FastAPI, SQLModel/SQLAlchemy (engine existente), psycopg2 (ya instalado)
**Storage**: PostgreSQL 17 (ya existente)
**Testing**: pytest (tests de contrato del health check, happy path, DB caída, DB no configurada)
**Target Platform**: mismo entorno actual (Railway + Docker)
**Project Type**: web (monorepo `core/` + `frontend/`)
**Performance Goals**: health check con DB < 1s en condiciones normales; timeout máximo 5s
**Constraints**: sin migración DB, sin nuevas dependencias, sin cambios frontend; health check siempre `200`
**Scale/Scope**: 1 función nueva en `database.py`, 1 endpoint modificado, 1 endpoint ampliado, ~4 tests nuevos

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. SDD | Spec HU-22 versionada; sin `[NEEDS CLARIFICATION]` pendientes. |
| II. Capas | La verificación de DB se añade al router de health (capa HTTP) llamando a una función de utilidad en `database.py` (capa de acceso a datos). No se viola la separación de capas. |
| III. Test-First | Tests Rojo→Verde para: (a) DB caída devuelve `connected: false`, (b) DB funcionando devuelve `connected: true`, (c) DB no configurada reporta "no configurado", (d) health check toujours `200`. |
| IV. Seguridad | No se exponen errores de SQL al cliente; solo se registra en log. No se crean endpoints nuevos que expongan información sensible. |
| V. Free-tier | Cero dependencias nuevas; se reutiliza el engine existente de SQLAlchemy. |
| VI. Despliegue | Health check siempre `200` (tras aclaración); no causa reinicios en Railway. Sin migración; variable de entorno es lo único que cambia. |
| VII. YAGNI | Sin cache del estado de DB, sin métricas de latencia, sin health check por separado — solo un campo booleano en los endpoints existentes. |

**Resultado**: PASS.

## Decisiones de diseño

Ver [research.md](./research.md): verificación mediante `SELECT 1` con timeout, inyección del engine via Depends, health siempre `200`.

## Project Structure

```text
specs/022-health-db-check/
├── plan.md  research.md  data-model.md  quickstart.md  contracts/

core/database/
├── database.py                             # + check_db_connectivity() function

core/health/api/
├── health.py                               # + get_engine() dependency, db check en health() y diagnostics()

tests/
├── test_health_db_check.py                 # nuevo: DB caída, DB OK, DB no configurada, health siempre 200
```

**Structure Decision**: toca 2 archivos de producción (database.py, health.py) y crea 1 archivo de tests. Sin migración, sin frontend, sin nuevos módulos.

## Complexity Tracking

No hay violaciones constitucionales. La feature es de baja complejidad: reutiliza el engine existente, añade una función de verificación y amplía dos endpoints existentes.
