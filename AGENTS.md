# AGENTS.md — Guía en tiempo de ejecución para agentes de IA

Este archivo lo leen Claude Code, GitHub Copilot y cualquier otro agente que trabaje
en este repositorio. **Es de lectura obligatoria antes de escribir código.**

## 0. Regla cero

La fuente de verdad normativa es `.specify/memory/constitution.md`.
Si algo en este archivo contradice la constitución, gana la constitución.
Si el usuario te pide algo que contradice la constitución, díselo antes de hacerlo.

## 1. Flujo obligatorio (Spec-Driven Development)

No escribas código de producción sin una especificación. El orden es:

```
/speckit-constitution   # solo si cambian los principios
/speckit-specify        # QUÉ y POR QUÉ  -> specs/NNN-nombre/spec.md
/speckit-clarify        # resuelve [NEEDS CLARIFICATION]
/speckit-plan           # CÓMO           -> specs/NNN-nombre/plan.md
/speckit-tasks          # tickets        -> specs/NNN-nombre/tasks.md
/speckit-analyze        # consistencia entre los tres artefactos
/speckit-implement      # recién aquí se escribe código
```

## 2. Mapa del repositorio

```
.specify/memory/constitution.md   # principios NO negociables
specs/NNN-nombre/                 # spec.md, plan.md, tasks.md por funcionalidad
core/
  main.py                         # bootstrap de FastAPI (factory `boostrap`)
  routers.py                      # registro de routers bajo /api y /api/v1
  settings/default.py             # AppSettings (pydantic-settings, lee env)
  settings/middleware.py          # CORS, security headers, rate limiting
  security/                       # rate limiter, cabeceras, manejo de errores
  database/                       # engine, modelos SQLModel, CRUD, seed
  catalog/                        # router -> service -> repository (catálogo)
  ensemble_project/               # router -> service -> repository (generación)
  ai_gateway/                     # AIGateway (ABC) + providers intercambiables
frontend/                         # React 19 + Vite + TypeScript
tests/                            # pytest; unitarios por defecto, integración opt-in
alembic/                          # migraciones
data/data.yaml                    # semillas del catálogo
docs/                             # backlog, seguridad, caso de negocio, runbook
```

## 3. Reglas de código que no se negocian

- **Capas**: `router -> service -> repository -> model`. Un router no toca la base de datos.
- **Inyección de dependencias**: los routers reciben servicios vía `Depends(...)`.
  Nunca instancies un gateway concreto dentro de un router.
- **Gateways**: toda llamada a un LLM pasa por una implementación de `AIGateway`
  obtenida con `get_ai_gateway()` (factory por configuración). No importes
  `GroqGateway` ni `OllamaGateway` directamente fuera de `core/ai_gateway/`.
- **Secretos**: solo por variable de entorno. Si escribes una API key en un archivo
  versionado, has roto la constitución.
- **Validación**: todo DTO de entrada es un modelo Pydantic con cotas explícitas.
- **Errores**: lanza excepciones de dominio en el service; el router las traduce a HTTP.
  Nunca devuelvas el texto de una excepción interna al cliente.
- **Tipos**: anota todo. `uv run ty check` debe pasar.

## 4. Comandos

```bash
# entorno
uv sync

# calidad (esto es lo que corre CI)
uv run pytest -q                    # unitarios (los de integración se saltan)
uv run pytest -m integration        # requieren Postgres y/o Ollama levantados
uv run ruff format
uv run ruff check --fix
uv run ty check

# levantar todo en local
docker compose up api postgres ollama

# frontend
cd frontend && npm install && npm run dev    # dev server con proxy a :9600
cd frontend && npm run build                 # genera frontend/dist servido por FastAPI
```

## 5. Convenciones

- Ramas: `NNN-nombre-corto` (el número lo asigna `create-new-feature.sh`).
- Commits: `HU-XX: descripción en imperativo`.
- Un ticket de `tasks.md` = un commit.
- Tickets marcados `[P]` tocan archivos disjuntos y pueden hacerse en paralelo
  por distintos integrantes.

## 6. Antes de decir "listo"

- [ ] `uv run pytest -q` en verde
- [ ] `uv run ruff check` limpio
- [ ] `uv run ty check` limpio
- [ ] La spec correspondiente refleja lo implementado
- [ ] No agregaste secretos, ni `allow_origins=["*"]`, ni SQL concatenado
