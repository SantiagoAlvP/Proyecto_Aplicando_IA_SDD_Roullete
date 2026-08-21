# Project Jackpot 🎰

You dont what to code/VibeCode , NO problem

<p align="center">
  <img src="https://github.com/jero98772/project_roulette/blob/dev/docs/pictures/logo_animated.gif?raw=true" alt="Project Jackpot" width="500">
</p>

<p align="center">
Genera ideas de proyectos de software para retarte, aprender tecnologías nuevas y construir un portafolio.
</p>

<p align="center">
<b>Construido de principio a fin con Spec-Driven Development (GitHub Spec Kit).</b>
</p>

---

> ## 👉 [**EMPEZAR-AQUI.md**](EMPEZAR-AQUI.md)
>
> **Punto de entrada único del proyecto.** Estado actual, URL desplegada,
> preparación del equipo, guion de la presentación, procedimiento de
> construcción en vivo y resolución de problemas.
> Su Sección 1 son instrucciones para asistentes de IA: ábrelo con Claude Code
> o Copilot y el agente sabe qué hacer.

---

## 🚀 Qué es

**Project Jackpot** es una máquina tragamonedas de ideas de proyectos: combina un
lenguaje de programación, una tecnología, un addon y un nivel de dificultad, valida
con IA que la combinación sea *construible*, y redacta una descripción que explica
qué vas a construir y qué vas a aprender.

Ejemplos reales generados por la aplicación:

* Un caché distribuido en Rust
* Un acortador de URLs en Prolog
* Un servidor DNS en C
* Un motor de recomendación en Clojure

---

## 📐 Este repositorio es un ejercicio de SDD

El código no se escribió a base de prompts sueltos. Cada funcionalidad nació de una
especificación versionada:

```
.specify/memory/constitution.md      ← 7 principios no negociables
specs/001-generador-de-proyectos/    ← spec.md · plan.md · tasks.md
specs/002-interfaz-tragamonedas/
specs/003-endurecimiento-seguridad/
specs/004-despliegue-continuo/
```

| Documento | Qué contiene |
|---|---|
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md) | Los principios que gobiernan todo el proyecto |
| [`AGENTS.md`](AGENTS.md) | Guía obligatoria para cualquier agente de IA que toque el repositorio |
| [`docs/backlog.md`](docs/backlog.md) | Las 10 Historias de Usuario con criterios Given/When/Then |
| [`docs/security.md`](docs/security.md) | Modelo de amenaza, controles, OWASP y limitaciones conocidas |
| [`docs/business-case.md`](docs/business-case.md) | ROI y comparativa OPEX/CAPEX: SDD vs. tradicional vs. prompting |
| [`docs/deployment.md`](docs/deployment.md) | Despliegue en Railway paso a paso, costo USD 0.00 |
| [`docs/live-demo-runbook.md`](docs/live-demo-runbook.md) | Procedimiento para construir historias en vivo con 6 personas |
| [`docs/endpoints.md`](docs/endpoints.md) | Referencia de la API |

---

# ✨ Funcionalidades

* 🎲 Ideas de proyecto completamente aleatorias
* 🎯 Generación por nivel de dificultad (1 a 5)
* 🔒 Fija los rodillos que quieras y deja el resto al azar
* 🤖 Descripción redactada por IA, con **modo degradado** si el proveedor cae
* 🕘 Historial de las últimas ideas generadas
* 🖥️ Interfaz web de máquina tragamonedas, responsiva
* ⚡ API REST documentada con OpenAPI
* 🐘 PostgreSQL con integridad referencial explícita
* 🛡️ Rate limiting, cabeceras de seguridad, CORS con lista blanca, errores sin fugas
* 🧪 204 pruebas automatizadas
* 🐳 Un solo contenedor: frontend + API
* ☁️ Despliegue continuo en Railway

---

# 🏗 Stack

**Backend** FastAPI · SQLModel · SQLAlchemy · Pydantic v2 · Alembic · uv
**Frontend** React 19 · TypeScript · Vite (sin librería de componentes)
**Datos** PostgreSQL 17
**IA** Interfaz `AIGateway` con proveedores Groq (producción), Ollama (local), LM Studio, Clojure (PoC) y stub determinístico
**Calidad** Pytest · Ruff · ty · pre-commit · gitleaks · pip-audit
**Infra** Docker multi-stage · GitHub Actions · Railway

---

# 🚀 Arranque rápido

## Con Docker (todo incluido)

```bash
git clone https://github.com/SantiagoAlvP/Proyecto_Aplicando_IA_SDD_Roullete.git
cd Proyecto_Aplicando_IA_SDD_Roullete
docker compose up api postgres
```

Abre http://localhost:9600

## Desarrollo local

```bash
uv sync
cp .env.example .env          # ajusta lo que necesites

# Base de datos
docker compose up -d postgres

# Backend (:9600)
uv run python project_jackpot.py

# Frontend con recarga en caliente (:5173, proxy a :9600)
cd frontend && npm install && npm run dev
```

> **Sin API key de IA la aplicación funciona igual**: arranca en modo degradado con
> descripciones por plantilla y lo advierte en el log. Para activar el LLM, consigue
> una clave gratuita en [console.groq.com](https://console.groq.com) y ponla en
> `GROQ_API_KEY`. Nunca la escribas en un archivo versionado.

---

# 📖 Documentación de la API

```
http://localhost:9600/api/docs      # Swagger UI
http://localhost:9600/api/redocs    # ReDoc
```

Referencia completa en [`docs/endpoints.md`](docs/endpoints.md).

---

# 🎲 Ejemplo de respuesta

```json
{
  "programming_language": "C",
  "technologies": "DNS Server",
  "addons": "Session Management",
  "extras": [
    { "programming_language": "Erlang", "technologies": "API Gateway", "addons": "Closest Pair of Points" },
    { "programming_language": "COBOL", "technologies": "Event Streaming Platform", "addons": null }
  ],
  "level": 3,
  "description": "Build a DNS Server project in C, using Session Management as a supporting tool. You will practise designing the core domain, wiring the pieces together and testing them end to end."
}
```

<p align="center">
  <img src="https://github.com/jero98772/project_roulette/blob/dev/docs/pictures/meme.png?raw=true" alt="meme" width="500">
</p>

---

# 📂 Estructura

```text
.
├── .specify/                # motor SDD: constitución, plantillas, scripts
├── specs/                   # una carpeta por funcionalidad: spec, plan, tasks
├── alembic/                 # migraciones
├── core/
│   ├── ai_gateway/          # AIGateway (ABC) + proveedores + factory
│   ├── catalog/             # router → service → repository
│   ├── database/            # engine, modelos, CRUD, siembra
│   ├── ensemble_project/    # generación de proyectos + advisor de IA
│   ├── health/              # verificación de vida
│   ├── security/            # rate limit, cabeceras, errores con request_id
│   └── settings/            # configuración y middleware
├── frontend/                # React 19 + Vite + TypeScript
├── data/                    # catálogo semilla
├── docs/                    # backlog, seguridad, caso de negocio, runbook
├── tests/                   # 204 pruebas
├── Dockerfile               # multi-stage: Node compila, Python sirve
├── entrypoint.sh            # migra y arranca
├── railway.json             # configuración de despliegue
└── AGENTS.md                # reglas para agentes de IA
```

---

# 🤝 Contribuir

Antes de abrir un Pull Request:

```bash
uv run pytest -q            # 204 passed
uv run ruff format
uv run ruff check --fix
uv run ruff check
uv run ty check
```

Y además, porque este repositorio se rige por una constitución:

* La funcionalidad tiene su especificación en `specs/` y está incluida en el diff.
* Los cambios de esquema traen su migración de Alembic.
* No hay secretos en el diff, ni `allow_origins=["*"]`, ni SQL concatenado.

Lee [`AGENTS.md`](AGENTS.md) antes de escribir código —también si eres un agente de IA.

---

# 📄 Licencia

**GNU General Public License v3.0 (GPL-3.0)** — ver [LICENSE](LICENSE).
