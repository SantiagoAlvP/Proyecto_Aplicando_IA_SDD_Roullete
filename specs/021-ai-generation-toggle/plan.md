# Implementation Plan: Desactivar generación por IA mediante variable de entorno

**Branch**: `021-ai-generation-toggle` | **Date**: 2026-08-25 | **Spec**: [spec.md](./spec.md)

## Summary

Añadir una variable de entorno `AI_GENERATION_ENABLED` que, cuando su valor sea distinto de
`true`/`1`/`on`, haga que toda llamada de generación use el `StubGateway` (descripción
determinística) en lugar del proveedor de IA configurado. El toggle se evalúa en cada
petición (no solo al arrancar) y se expone en el endpoint de diagnóstico. No se modifica
el frontend, la base de datos ni los endpoints de lectura.

## Technical Context

**Language/Version**: Python 3.13 backend; TypeScript 5.9 / React 19 frontend (sin cambios frontend)
**Primary Dependencies**: FastAPI, SQLModel, Pydantic Settings; sin dependencias nuevas
**Storage**: N/A (sin migración; el toggle es una variable de entorno)
**Testing**: pytest (contrato del diagnóstico, happy path degradado, verificación de no-llamada)
**Target Platform**: mismo entorno actual (Railway + Docker)
**Project Type**: web (monorepo `core/` + `frontend/`)
**Performance Goals**: sin impacto; lectura de setting por petición es O(1)
**Constraints**: sin migración DB, sin nuevas dependencias, sin cambios frontend
**Scale/Scope**: 1 setting nuevo, 2 métodos modificados, 1 endpoint ampliado, ~3 tests nuevos

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. SDD | Spec HU-21 versionada; sin `[NEEDS CLARIFICATION]` pendientes. |
| II. Capas | El toggle se lee en la capa de servicio (`AIProjectAdvisor`); el router no se toca. El setting vive en `AppSettings` (configuración, no lógica de negocio). |
| III. Test-First | Tests Rojo→Verde para: (a) descripción de respaldo al desactivar, (b) sin llamada al gateway, (c) diagnóstico refleja el estado. |
| IV. Seguridad | Fail-closed: cualquier valor no reconocido desactiva la IA; la API key no se expone; el diagnóstico ya redacta secretos. |
| V. Free-tier | Cero dependencias nuevas; el stub ya existe; el toggle reduce gasto de cuota. |
| VI. Despliegue | Sin migración; un solo artefacto Docker; variable de entorno es lo único que cambia entre entornos. |
| VII. YAGNI | Sin persistencia del estado, sin auditoría, sin control por usuario — solo un interruptor global. |

**Resultado**: PASS.

## Decisiones de diseño

Ver [research.md](./research.md): lectura por instancia de `AppSettings`, parsing
de valores truthy/falsy, reutilización del `StubGateway` existente, ampliación del
diagnóstico existente.

## Project Structure

```text
specs/021-ai-generation-toggle/
├── plan.md  research.md  data-model.md  quickstart.md  contracts/

core/settings/default.py                  # + AI_GENERATION_ENABLED: bool = True
                                          # + property ai_generation_enabled -> bool
core/ensemble_project/
├── ai_project_advisor.py                 # generate_description y choose_valid_project
│                                         # saltan al stub cuando toggle desactivado
├── api/ensemble_project_router.py        # (sin cambios — el toggle es transparente)
└── ensemble_project_service.py           # (sin cambios)
core/health/api/health.py                 # + "ai_generation_enabled" en diagnóstico

tests/
├── test_ai_toggle.py                     # nuevo: happy path degradado, no-llamada, diagnóstico
```

**Structure Decision**: toca 3 archivos de producción (setting, advisor, diagnóstico) y crea
1 archivo de tests. Sin migración, sin frontend, sin nuevos módulos.

## Complexity Tracking

No hay violaciones constitucionales. La feature es de baja complejidad: reutiliza el
`StubGateway` existente, amplía un setting existente y añade un campo al diagnóstico.
