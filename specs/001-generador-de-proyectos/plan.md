# Implementation Plan: Generador de ideas de proyectos asistido por IA

**Branch**: `001-generador-de-proyectos` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

## Summary

API REST asíncrona que combina tres dimensiones de catálogo (lenguaje, tecnología, addon)
más un nivel de dificultad para producir ideas de proyecto. Un gateway de IA intercambiable
evalúa la viabilidad de los candidatos, elige el mejor y redacta la descripción. El resultado
se persiste en PostgreSQL con integridad referencial explícita.

La decisión estructural central es aislar el LLM detrás de una interfaz (`AIGateway`) resuelta
por configuración en tiempo de arranque, para que el proveedor sea un detalle sustituible
y una caída del modelo degrade el servicio en lugar de tumbarlo.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: FastAPI, SQLModel, Pydantic v2, Alembic, Strands Agents, httpx
**Storage**: PostgreSQL 17
**Testing**: pytest con dobles de prueba para base de datos y gateway de IA
**Target Platform**: contenedor Linux (Docker), desplegado en Railway
**Project Type**: web (API + frontend desacoplado servido estáticamente)
**Performance Goals**: p95 < 10 s por generación (dominado por la latencia del LLM); catálogo < 200 ms
**Constraints**: costo de infraestructura USD 0.00; el servicio responde aunque el LLM no esté disponible
**Scale/Scope**: 5 historias de usuario, 9 endpoints, 4 tablas

## Constitution Check

| Principio | Cumplimiento en este plan |
|---|---|
| I. SDD | Esta spec, este plan y `tasks.md` preceden al código. Rama `001-generador-de-proyectos`. |
| II. Capas y SOLID | `router -> service -> repository -> model`. `CatalogService` y `AIGateway` son `ABC`; los routers reciben sus colaboradores por `Depends`. |
| III. Test-First | Cada endpoint lleva test de contrato, camino feliz y error. La base de datos y el LLM se sustituyen por dobles; ningún test requiere servicios vivos. |
| IV. Seguridad | Credenciales por variable de entorno; DTOs con cotas (`level` con `ge=1, le=5`); acceso a datos solo por ORM; errores sin stack trace. *Rate limiting y cabeceras se especifican en `003`.* |
| V. Free-tier | Ollama local (USD 0) en desarrollo, Groq (capa gratuita) en producción, stub determinístico como respaldo. |
| VI. Despliegue | Migraciones Alembic y siembra del catálogo automáticas al arrancar. `/api/health` expuesto. |
| VII. YAGNI | Sin caché, sin cola de trabajos, sin autenticación. Se añadirán cuando una spec los pida. |

**Resultado**: PASS — sin desviaciones que registrar.

## Project Structure

### Documentation

```
specs/001-generador-de-proyectos/
├── spec.md
├── plan.md
└── tasks.md
```

### Source Code

```
core/
├── main.py                       # factory boostrap(): crea la app, monta routers y middleware
├── routers.py                    # /api (health) y /api/v1 (catalog, ensemble_project)
├── settings/
│   └── default.py                # AppSettings: lee entorno, expone db_url
├── database/
│   ├── database.py               # engine, init_db(), get_db() como dependencia
│   ├── models.py                 # Project, ProjectExtra y las tres tablas de catálogo
│   ├── crud.py                   # operaciones atómicas por tabla
│   └── load_database_data.py     # siembra idempotente desde data/data.yaml
├── catalog/
│   ├── api/catalog_router.py     # 6 endpoints de consulta
│   ├── catalog_service.py        # ABC + implementación por defecto
│   └── catalog_repository.py     # acceso a datos del catálogo
├── ensemble_project/
│   ├── api/
│   │   ├── ensemble_project_router.py      # 3 endpoints de generación
│   │   ├── ensemble_project_models.py      # DTOs de entrada y salida
│   │   └── ensemble_project_validation.py  # resolución get-or-create de catálogo
│   ├── ensemble_project_service.py         # orquestación de la generación
│   └── ensemble_project_repository.py      # persistencia del proyecto y sus extras
└── ai_gateway/
    ├── ai_gateway.py             # interfaz AIGateway (ABC)
    ├── factory.py                # resuelve el proveedor según AI_PROVIDER
    ├── groq_provider.py          # producción (capa gratuita)
    ├── ollama_provider.py        # desarrollo local
    └── stub_provider.py          # respaldo determinístico y tests
```

**Structure Decision**: se agrupa por dominio (`catalog`, `ensemble_project`, `ai_gateway`)
y no por tipo técnico (`controllers/`, `services/`). Cada carpeta de dominio contiene su
router, su servicio y su repositorio, de modo que una historia de usuario toca una sola
carpeta y varios integrantes pueden trabajar en paralelo sin colisionar.

## Decisiones de diseño

**D-01 — El LLM detrás de una interfaz.** `AIGateway` es una clase abstracta con un único
método `generate(prompt) -> str`. La orquestación (elegir candidato, redactar descripción)
vive en `ProjectGeneratorAIGateway`, que consume la interfaz. Consecuencia: cambiar de
Ollama a Groq es una variable de entorno.
*Alternativa descartada*: llamar al SDK del proveedor desde el servicio. Más corto, pero ata
la lógica de negocio a un proveedor y hace imposible probar sin red.

**D-02 — Dos llamadas al modelo por generación.** Una para validar y seleccionar, otra para
describir. Separarlas permite usar salida estructurada (`ProjectSelection`) en la primera,
donde el formato importa, y texto libre en la segunda.
*Costo*: duplica la latencia. Aceptado porque la validación evita persistir basura.

**D-03 — `extras = nivel * 2`.** Regla determinística en lugar de pedirle al modelo que
decida la complejidad. Es predecible, comprobable en un test y no consume tokens.

**D-04 — Get-or-create para valores de catálogo.** Un valor desconocido enviado por el usuario
se inserta en lugar de rechazarse. El catálogo crece con el uso. La restricción `unique`
sobre `name` evita duplicados bajo concurrencia.

**D-05 — Modo degradado.** Si el proveedor falla, `stub_provider` produce una descripción
por plantilla a partir de los mismos datos. El usuario recibe una respuesta correcta aunque
menos rica; el incidente queda en el log. *Sin esto, una demo en vivo depende de que un
servicio de terceros esté de buen humor.*

## Complexity Tracking

| Complejidad introducida | Por qué es necesaria | Alternativa más simple descartada |
|---|---|---|
| Capa de repositorio separada del servicio | Permite probar la lógica de generación sin base de datos y fue lo que hizo posible tener 131 tests unitarios sin Postgres | Consultar el ORM desde el servicio: más corto, pero obliga a levantar Postgres en cada test |
| Tres implementaciones de `AIGateway` | Cada entorno tiene una restricción distinta: local sin red, producción sin RAM, tests sin latencia | Un solo proveedor: rompe o el desarrollo local o el despliegue gratuito |
| Tabla `project_extras` separada | Normalización: un proyecto tiene N extras y cada extra referencia hasta tres catálogos | Guardar los extras como JSON en `projects`: pierde integridad referencial y hace imposible consultar por tecnología |
