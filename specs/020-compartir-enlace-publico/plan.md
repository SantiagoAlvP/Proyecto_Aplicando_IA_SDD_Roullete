# Implementation Plan: Compartir proyectos mediante enlace público (HU-20)

**Branch**: `020-compartir-enlace-publico` | **Date**: 2026-08-23 | **Spec**: [spec.md](./spec.md)

## Summary

Cada proyecto generado recibe un token opaco no adivinable (`share_token`) persistido
junto a él; la URL `{origin}/proyecto/{token}` abre una vista pública de solo lectura
servida por el SPA existente, que consume un endpoint JSON nuevo
`GET /api/v1/ensemble_project/shared/{share_token}`. La acción "Compartir" en la tarjeta
de resultado y en cada entrada del historial copia ese enlace con degradación digna.
Migración retroactiva que dota de token a todos los proyectos previos y persiste `level`
y `created_at`, hoy inexistentes pero exigidos por la vista.

## Technical Context

**Language/Version**: Python 3.13 backend; TypeScript 5.9 / React 19 frontend
**Primary Dependencies**: FastAPI, SQLModel, Alembic, Pydantic; React + Vite. Sin dependencias nuevas
**Storage**: PostgreSQL 17 vía repositorio existente (una migración Alembic)
**Testing**: pytest (contrato, happy path, error por endpoint nuevo); `npm run build` en CI
**Target Platform**: navegadores modernos desde 360 px; mismo origen API+SPA
**Project Type**: web (monorepo `core/` + `frontend/`)
**Performance Goals**: primera apertura del enlace < 5 s (SC-001); lectura indexada por clave única
**Constraints**: sin cuentas ni sesiones; enlaces permanentes; USD 0.00 de OPEX adicional
**Scale/Scope**: 3 historias de usuario, 1 endpoint nuevo, 1 migración, ~4 componentes frontend

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. SDD | Spec HU-20 versionada en esta rama; sin `[NEEDS CLARIFICATION]` pendientes. |
| II. Capas | El endpoint sigue `router -> service -> repository`; DTOs en la capa api; nada de ORM fuera del repositorio. |
| III. Test-First | Tests Rojo→Verde para esquema, contrato del endpoint público y exposición del token en historial/generación. |
| IV. Seguridad | Path param acotado con patrón explícito; 404 neutro sin filtraciones; token opaco impide enumeración; hereda rate limiting y cabeceras existentes. |
| V. Free-tier | Cero dependencias nuevas, cero servicios externos; el token se genera en proceso. |
| VI. Despliegue | Migración Alembic versionada que corre al arrancar; un solo artefacto Docker sin cambios. |
| VII. YAGNI | Ruta nueva resuelta inspeccionando `pathname` (sin react-router); token como columna, sin tabla nueva ni revocación. |

**Resultado**: PASS.

## Project Structure

```text
specs/020-compartir-enlace-publico/
├── plan.md  research.md  data-model.md  quickstart.md  contracts/

alembic/versions/<rev>_add_share_token_level_created_at_to_projects.py

core/database/
├── models.py                            # + share_token, level, created_at en Project
└── crud.py                              # ProjectCRUD.create persiste token/nivel; + get_by_share_token

core/ensemble_project/
├── api/
│   ├── ensemble_project_models.py       # + SharedProjectResponse; ProjectResponse/HistoryEntry amplían campos
│   └── ensemble_project_router.py       # + GET /shared/{share_token}
├── ensemble_project_service.py          # + get_shared_project()
└── ensemble_project_repository.py       # + get_by_share_token(); save_project persiste level

frontend/src/
├── types.ts  api.ts                     # tipos espejo + api.sharedProject(token)
├── App.tsx                              # detección de ruta /proyecto/{token}
├── components/
│   ├── SharedProject.tsx                # vista pública + estado "no disponible" + CTA
│   ├── ShareButton.tsx                  # clipboard + fallback + confirmación
│   ├── ResultCard.tsx  History.tsx      # integran ShareButton
└── styles.css

tests/
├── test_database/test_crud.py           # ampliación
└── test_fastapi_endpoints/test_shared_project.py   # nuevo
```

**Structure Decision**: monorepo ya establecido — la historia toca ambos lados y cabe en
un PR; ninguna carpeta nueva de código.

## Decisiones de diseño

Ver [research.md](./research.md) (D-01…D-06): token opaco `secrets.token_urlsafe(12)`;
persistencia de `level`/`created_at`; vista como ruta del SPA sin librería de routing;
endpoint JSON acotado; backfill retroactivo en la migración; portapapeles con fallback.

## Complexity Tracking

| Complejidad introducida | Por qué es necesaria | Alternativa más simple descartada |
|---|---|---|
| Columnas nuevas en migración (3) | FR-002 exige mostrar nivel; Key Entity exige fecha; el enlace necesita identidad pública estable | No persistir el nivel: obligaría a inventarlo al mostrar; tabla aparte de "enlaces": relación 1:1 sin valor |
