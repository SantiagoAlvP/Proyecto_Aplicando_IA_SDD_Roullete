# Project Jackpot Constitution

> Documento raíz del motor Spec-Driven Development (SDD).
> Toda especificación (`/speckit-specify`), plan (`/speckit-plan`), lista de tareas
> (`/speckit-tasks`) e implementación (`/speckit-implement`) se valida contra estos
> principios antes de fusionarse a `main`. Ninguna excepción se acepta sin quedar
> registrada en la sección **Complexity Tracking** del plan correspondiente.

## Core Principles

### I. Spec-Driven Development (NO NEGOCIABLE)

Ninguna línea de código de producción nace de un prompt suelto. El flujo obligatorio es:

`/speckit-constitution` -> `/speckit-specify` -> `/speckit-clarify` -> `/speckit-plan` ->
`/speckit-tasks` -> `/speckit-analyze` -> `/speckit-implement`

Reglas duras:

- Cada funcionalidad vive en una rama `NNN-nombre-corto` con su carpeta `specs/NNN-nombre-corto/`.
- La especificación describe **QUÉ** y **POR QUÉ** (lenguaje de negocio, sin stack ni nombres de clases).
  El plan describe el **CÓMO** (stack, contratos, modelo de datos).
- Toda ambigüedad se marca `[NEEDS CLARIFICATION: ...]` y se resuelve antes de planear.
  Un `[NEEDS CLARIFICATION]` sin resolver bloquea el merge.
- Si el código y la especificación divergen, **la especificación es la fuente de verdad**:
  se corrige el código o se enmienda la spec con un commit explícito, nunca se deja la deriva.
- Las especificaciones se versionan en Git junto al código. El diff de la spec es parte del PR.

### II. Arquitectura en capas y SOLID

El backend mantiene una separación estricta en cuatro capas, sin saltos:

`router (HTTP/DTO)` -> `service (reglas de negocio)` -> `repository (acceso a datos)` -> `model (SQLModel)`

Reglas duras:

- Un router **nunca** consulta la base de datos ni instancia un repositorio concreto;
  recibe sus colaboradores por inyección de dependencias (`Depends`).
- Todo servicio y todo gateway externo se define primero como clase abstracta (`ABC`)
  y se consume por su interfaz, nunca por su implementación concreta (DIP).
- Un servicio no importa `fastapi` ni conoce códigos de estado HTTP; lanza excepciones
  de dominio que el router traduce.
- Toda integración con un sistema externo (LLM, correo, pagos) pasa por un *gateway*
  intercambiable en tiempo de arranque mediante configuración. Cambiar de proveedor
  no debe tocar servicios ni routers.
- Las funciones superan 50 líneas solo con justificación escrita en el plan.

### III. Test-First y contratos verificables

Reglas duras:

- Toda Historia de Usuario aporta al menos un test que falla antes de implementarla
  y pasa después (ciclo Red -> Green -> Refactor).
- Todo endpoint nuevo trae: un test de contrato (forma de la respuesta y código de estado),
  un test de camino feliz y un test de error/validación.
- Los tests **no** dependen de servicios externos vivos: la base de datos y el gateway
  de IA se sustituyen por dobles de prueba. Un test que solo pasa con Ollama encendido
  es un test roto.
- `uv run pytest` debe quedar en verde antes de cualquier push. Un test rojo bloquea el merge.
- La cobertura no baja entre PRs. Bajarla exige justificación en el plan.

### IV. Seguridad por defecto (Secure by Default)

Reglas duras:

- **Cero secretos en el repositorio.** Credenciales, URLs de base de datos y API keys
  se leen únicamente de variables de entorno. `.env` está en `.gitignore`;
  `.env.example` documenta las variables sin valores reales.
- Toda entrada externa se valida con un modelo Pydantic con restricciones explícitas
  (`min_length`, `max_length`, `ge`, `le`, `pattern`). Nada de `str` sin cota.
- Los errores devueltos al cliente **nunca** exponen stack traces, rutas del sistema,
  SQL ni nombres de tablas. El detalle técnico va al log; al cliente va un mensaje neutro
  y un identificador de correlación.
- CORS se configura por lista blanca explícita según entorno. `allow_origins=["*"]`
  está prohibido en producción.
- Todo endpoint que consuma un LLM (recurso costoso) está protegido por rate limiting.
- El acceso a datos usa siempre el ORM o consultas parametrizadas. Prohibida
  la concatenación de strings para construir SQL.
- Las respuestas incluyen cabeceras de seguridad (`X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`, HSTS en producción).
- Las dependencias se auditan en CI. Una vulnerabilidad de severidad alta bloquea el merge.

### V. Frugalidad de infraestructura (Free-Tier First)

El proyecto debe poder operarse con un costo monetario de USD 0.00.

Reglas duras:

- Toda dependencia de infraestructura debe tener una alternativa viable en capa gratuita
  documentada en `docs/business-case.md`.
- El modelo de IA es un detalle de configuración, no de arquitectura: en desarrollo local
  se usa Ollama (costo cero, sin salida a Internet); en producción, un proveedor con
  capa gratuita. El sistema arranca y responde aunque no haya proveedor de IA disponible
  (modo degradado determinístico), porque una demo caída cuesta más que una descripción imperfecta.
- Cada PR que agregue un servicio de pago o una dependencia con costo recurrente
  debe declarar su impacto en OPEX en la sección de costos del plan.

### VI. Despliegue reproducible y continuo

Reglas duras:

- Un único artefacto (imagen Docker) sirve para local, CI y producción.
  Lo que cambia entre entornos son variables de entorno, nunca el código.
- `main` siempre debe ser desplegable. Cada merge a `main` dispara build, tests y despliegue.
- Las migraciones de base de datos son versionadas con Alembic y se ejecutan
  automáticamente al arrancar. Nunca se modifica el esquema a mano en producción.
- Existe un endpoint `/api/health` que CI y la plataforma de hosting usan como
  verificación de vida. Un despliegue cuya salud no responde se considera fallido.

### VII. Simplicidad (YAGNI)

Reglas duras:

- Se implementa lo que la especificación pide, ni una abstracción más.
- Toda capa, patrón o dependencia adicional debe justificarse en la sección
  **Complexity Tracking** del plan: qué problema resuelve y qué alternativa más simple se descartó.
- Prohibido el código muerto, los `TODO` sin ticket y las funcionalidades "por si acaso".

## Restricciones tecnológicas

Estas decisiones están fijadas para toda la línea base y sus incrementos:

| Capa | Tecnología | Notas |
|---|---|---|
| Lenguaje backend | Python >= 3.12 | Tipado explícito obligatorio |
| Framework API | FastAPI | Async first |
| ORM | SQLModel sobre SQLAlchemy | |
| Base de datos | PostgreSQL 17 | Integridad referencial explícita, sin redundancia |
| Migraciones | Alembic | Una migración por cambio de esquema |
| Frontend | React 19 + Vite + TypeScript | Build estático servido por el backend |
| Gateway de IA | Interfaz `AIGateway` | Proveedores: Groq (prod), Ollama (local), stub (tests/degradado) |
| Gestión de paquetes | `uv` | `uv.lock` versionado |
| Calidad | Ruff (lint + format), `ty` (tipos), Pytest | Ejecutados en pre-commit y en CI |
| Contenedores | Docker + Docker Compose | Un Dockerfile multi-stage |
| Hosting | Railway (capa gratuita) | Backend + PostgreSQL gestionado |
| Motor SDD | GitHub Spec Kit | Integraciones: Claude Code y GitHub Copilot |

Cambiar cualquier fila de esta tabla es una **enmienda constitucional** (ver Governance).

## Flujo de trabajo y puertas de calidad

**Flujo por Historia de Usuario:**

1. `specify` crea la rama y la spec; se completan criterios de aceptación en formato Given/When/Then.
2. `clarify` resuelve los `[NEEDS CLARIFICATION]`.
3. `plan` produce el diseño técnico y la verificación explícita contra esta constitución.
4. `tasks` descompone en tickets ejecutables e independientes, marcando cuáles son paralelizables `[P]`.
5. `analyze` verifica consistencia entre spec, plan y tasks antes de escribir código.
6. `implement` ejecuta los tickets. Cada ticket = un commit con mensaje `HU-XX: descripción`.
7. PR a `main` con la spec incluida en el diff.

**Puertas de calidad (todas obligatorias antes del merge):**

- [ ] `uv run pytest -v` en verde
- [ ] `uv run ruff check` sin hallazgos
- [ ] `uv run ruff format --check` sin cambios pendientes
- [ ] `uv run ty check` sin errores
- [ ] Sin secretos en el diff (verificado por `gitleaks` en CI)
- [ ] Sin vulnerabilidades altas en dependencias (`pip-audit` en CI)
- [ ] La spec de la funcionalidad está actualizada y versionada
- [ ] El despliegue en Railway responde `200` en `/api/health`

**Trabajo en paralelo (equipo de 6):** cada integrante ejecuta el motor SDD desde su
propia máquina sobre un ticket distinto de la misma spec. Los tickets marcados `[P]`
tocan archivos disjuntos y por tanto no generan conflictos de merge. Los tickets
secuenciales declaran su dependencia en `tasks.md`.

## Governance

- Esta constitución **prevalece** sobre cualquier práctica, preferencia personal
  o sugerencia de un asistente de IA. Si un agente propone algo que la contradice,
  se rechaza la propuesta, no el principio.
- **Enmiendas**: requieren (a) un PR que modifique este archivo, (b) justificación escrita
  del problema que resuelve, (c) el impacto sobre las specs ya existentes, y
  (d) aprobación de al menos 2 integrantes del equipo.
- **Versionado semántico de la constitución**:
  - MAJOR: se elimina o se redefine incompatiblemente un principio.
  - MINOR: se agrega un principio o una sección normativa nueva.
  - PATCH: aclaraciones de redacción que no cambian la obligación.
- **Cumplimiento**: toda revisión de PR verifica el cumplimiento explícitamente.
  La complejidad no justificada se devuelve al autor.
- **Guía en tiempo de ejecución para agentes**: `AGENTS.md` en la raíz del repositorio.

**Version**: 1.0.0 | **Ratified**: 2026-08-21 | **Last Amended**: 2026-08-21
