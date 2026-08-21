# EMPEZAR AQUÍ

> **Este archivo es el punto de entrada único del proyecto.**
> Si eres una persona: léelo de arriba abajo, tiene todo lo que hay que hacer.
> Si eres un asistente de IA: la Sección 1 son tus instrucciones. Léela completa
> antes de tocar un solo archivo.

---

## SECCIÓN 1 — INSTRUCCIONES PARA EL ASISTENTE DE IA

**Lee esto primero. No escribas código hasta terminar esta sección.**

### 1.1 Qué es este proyecto

**Project Jackpot** es una aplicación web que genera ideas de proyectos de
software ("máquina tragamonedas"): combina un lenguaje, una tecnología, un addon
y un nivel de dificultad, valida con IA que la combinación sea construible, y
redacta una descripción. Es un trabajo universitario cuyo objetivo es demostrar
**Spec-Driven Development (SDD)** con GitHub Spec Kit.

El producto importa, pero **lo que se evalúa es la metodología**. Cada línea de
código debe poder rastrearse hasta una especificación escrita.

### 1.2 Archivos que DEBES leer antes de trabajar

En este orden, sin saltarte ninguno:

1. **`.specify/memory/constitution.md`** — los 7 principios no negociables.
   Prevalece sobre cualquier preferencia tuya o del usuario.
2. **`AGENTS.md`** — reglas de código concretas: capas, inyección de
   dependencias, manejo de secretos, comandos.
3. **`docs/backlog.md`** — las 10 Historias de Usuario ya entregadas.
4. **`specs/00X-.../spec.md`** de la funcionalidad relacionada con tu tarea.

### 1.3 Reglas duras

- **Nunca escribas código de producción sin una especificación.** Si te piden
  una funcionalidad nueva, el primer paso es `/speckit-specify`, no editar un
  archivo.
- **Respeta las capas**: `router → service → repository → model`. Un router
  jamás consulta la base de datos.
- **Nunca pongas un secreto en un archivo versionado.** `gitleaks` corre en
  pre-commit y en CI, y bloqueará el commit.
- **Nunca uses `allow_origins=["*"]`.** La app se niega a arrancar en producción
  si lo detecta.
- **Nunca marques una tarea como terminada con la suite en rojo.**
- Si el usuario te pide algo que contradice la constitución, **díselo antes de
  hacerlo**.

### 1.4 Antes de decir "listo"

```bash
uv run pytest -q        # debe decir: 210 passed
uv run ruff check .     # All checks passed!
uv run ty check         # All checks passed!
```

Y además: la spec de la funcionalidad está actualizada y refleja lo implementado.

---

## SECCIÓN 2 — ESTADO ACTUAL (verificado el 2026-08-21)

### 2.1 La aplicación está desplegada y funcionando

**URL pública:** https://proyectoaplicandoiasddroullete-production.up.railway.app

| Recurso | Ruta |
|---|---|
| Aplicación (frontend) | `/` |
| Documentación de la API | `/api/docs` |
| Verificación de vida | `/api/health` |
| Diagnóstico de configuración | `/api/health/diagnostics` |

### 2.2 Verificación en un comando

```bash
curl -s https://proyectoaplicandoiasddroullete-production.up.railway.app/api/health/diagnostics | python3 -m json.tool
```

Debe responder `"resolved_provider": "groq"` y `"degraded": false`.
**Si dice `"degraded": true`, la IA no está activa** — ver Sección 6.

### 2.3 Qué está entregado

| Requisito del enunciado | Dónde está | Estado |
|---|---|---|
| Frontend integrado | `frontend/` (React 19 + Vite), servido en `/` | Hecho |
| Backend / APIs | `core/`, 12 endpoints bajo `/api` | Hecho |
| Base de datos | PostgreSQL en Railway + Alembic | Hecho |
| Herramienta SDD | `.specify/` (GitHub Spec Kit) | Hecho |
| Especificaciones | `specs/001` a `specs/004` (spec + plan + tasks) | Hecho |
| 10 HU priorizadas | `docs/backlog.md` | Hecho |
| Pruebas automatizadas | `tests/`, **210 tests en verde** | Hecho |
| Ciberseguridad | `docs/security.md` + controles activos | Hecho |
| Despliegue gratuito | Railway, USD 0.00 | Hecho |
| Caso de negocio / ROI | `docs/business-case.md` | Hecho |
| **2 HU construidas en vivo** | Sección 5 de este archivo | **Pendiente: en la clase** |

### 2.4 Stack

Backend FastAPI · SQLModel · Alembic · Python 3.13
Frontend React 19 · TypeScript · Vite (sin librería de componentes)
Datos PostgreSQL 17
IA Groq (`openai/gpt-oss-20b`) en producción; Ollama en local; stub como respaldo
Calidad Pytest · Ruff · ty · pre-commit · gitleaks · pip-audit
Infra Docker multi-stage · GitHub Actions · Railway

---

## SECCIÓN 3 — PREPARACIÓN (hacer ANTES de la clase)

> **Esto no se hace en vivo.** Si alguien llega sin el paso 3.1 completo, el
> equipo pierde 10 minutos que no tiene.

### 3.1 Cada uno de los 6 integrantes, en su máquina

```bash
# 1. Requisitos: Python 3.12+, Node 22+, Git
#    Instalar uv:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar y preparar
git clone https://github.com/SantiagoAlvP/Proyecto_Aplicando_IA_SDD_Roullete.git
cd Proyecto_Aplicando_IA_SDD_Roullete
uv sync
cd frontend && npm install && cd ..

# 3. Instalar el motor SDD
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify check

# 4. Confirmar que la suite pasa ANTES de tocar nada
uv run pytest -q          # debe decir: 210 passed
```

### 3.2 Confirmar que el motor SDD responde

Abre tu asistente (Claude Code o GitHub Copilot en VS Code) **dentro de la
carpeta del repositorio** y escribe `/speckit-`. Deben aparecer:

`constitution` · `specify` · `clarify` · `plan` · `tasks` · `analyze` · `implement`

Si no aparecen:

```bash
specify init --here --force --integration claude    # o --integration copilot
```

### 3.3 Ensayo (idealmente el día anterior)

Inventen una HU cualquiera —por ejemplo *"quiero marcar un proyecto como
favorito"*— y corran el flujo completo cronometrando. **El ensayo es lo que
convierte 20 minutos improvisados en 8 minutos controlados.**

### 3.4 Checklist de la sala

- [ ] La URL pública responde (Sección 2.2)
- [ ] `main` está limpia, sin cambios sin fusionar
- [ ] Los 6 tienen `uv run pytest` en verde localmente
- [ ] Alguien tiene permisos de merge en GitHub
- [ ] Segunda conexión disponible (hotspot del teléfono)
- [ ] La pestaña de Railway abierta, con el Agent **cerrado** (es de pago)

---

## SECCIÓN 4 — GUION DE LA PRESENTACIÓN (línea base, ~8 min)

| Min | Quién | Qué muestra |
|---|---|---|
| 0–1 | 1 | La app desplegada. Gira los rodillos: sale una idea con descripción de IA |
| 1–2 | 1 | Fija "Rust", vuelve a girar: se respeta. El historial se actualiza solo |
| 2–4 | 2 | `.specify/memory/constitution.md` — los 7 principios. **El corazón de SDD** |
| 4–5 | 2 | `specs/001/` → `spec.md`, `plan.md`, `tasks.md`: de la idea a los tickets |
| 5–6 | 3 | `docs/backlog.md` — las 10 HU con criterios Given/When/Then |
| 6–7 | 4 | `uv run pytest` → 210 en verde. Enseña cómo un criterio de aceptación **es** un test (`tests/test_security/test_rate_limit.py`) |
| 7–8 | 5 | Seguridad en vivo (ver 4.2) |

### 4.1 La frase clave (decirla en el minuto 4)

> "La decisión de poner el modelo de lenguaje detrás de una interfaz la tomamos
> en el `plan.md` de la primera spec, antes de escribir código. Cuando
> descubrimos que Ollama no cabe en ninguna capa gratuita, cambiar a Groq costó
> una variable de entorno. Sin esa decisión escrita, eso son tres días de
> reescritura."

Es el mejor argumento del proyecto y es verificable en el repositorio.
Está en `specs/001-generador-de-proyectos/plan.md`, decisión **D-01**.

### 4.2 Demostración de seguridad en vivo

```bash
URL=https://proyectoaplicandoiasddroullete-production.up.railway.app

# 1. Rate limiting: el bucle recibe 429 con Retry-After
for i in $(seq 1 70); do curl -s -o /dev/null -w "%{http_code} " $URL/api/v1/catalog/addons/random; done; echo

# 2. Cabeceras de seguridad
curl -sI $URL/api/health | grep -iE "strict-transport|content-security|x-frame|x-content-type"

# 3. Validación: nivel fuera de rango, rechazado antes de gastar tokens de IA
curl -s -X POST $URL/api/v1/ensemble_project/generate_project_by_level \
     -H "Content-Type: application/json" -d '{"level":9}'
```

El punto que hay que verbalizar en el tercer comando: **el `422` llega sin
haber llamado al modelo**. La validación es la defensa más barata que existe.

### 4.3 Si preguntan "¿y si se les cae la IA en plena demo?"

La respuesta ya está escrita y probada en producción: la app entra en **modo
degradado** y sigue respondiendo con descripciones determinísticas.
Está especificado en `specs/001/spec.md`, **FR-009**, y se puede demostrar
poniendo `AI_PROVIDER=stub` en Railway.

De hecho, ocurrió de verdad durante el despliegue: Groq rechazó peticiones
durante horas por un modelo retirado y **ningún usuario vio un error**.

---

## SECCIÓN 5 — CONSTRUCCIÓN EN VIVO DE UNA HU (5–10 min por spec)

### Paso 1 — Crear la spec (1 persona, ~2 min)

Quien conduzca escribe en su asistente, **con el enunciado del profesor tal cual**:

```
/speckit-specify Como <rol>, quiero <capacidad>, para <beneficio>.
```

Spec Kit crea la rama `005-nombre-corto` y `specs/005-nombre-corto/spec.md`.

Luego, en pantalla:

```
/speckit-clarify
```

> **Mostrar los `[NEEDS CLARIFICATION]` es parte de la demostración.** Es la
> evidencia visible de que la metodología obliga a resolver la ambigüedad antes
> de codificar, en vez de dejar que el modelo la invente.

### Paso 2 — Plan y tickets (~2 min)

```
/speckit-plan
/speckit-tasks
```

`tasks.md` sale con los tickets marcados `[P]` cuando son paralelizables.

### Paso 3 — Repartir

```bash
# El conductor:
git push -u origin 005-nombre-corto

# Los demás:
git fetch && git checkout 005-nombre-corto
```

**Plantilla de reparto** — casi cualquier HU de esta app se descompone así:

| # | Integrante | Rol | Archivos | Depende de |
|---|---|---|---|---|
| T1 | 1 | Modelo y migración | `core/database/models.py`, `alembic/versions/` | — |
| T2 | 2 | Repositorio | `core/*/*_repository.py`, `core/database/crud.py` | T1 |
| T3 | 3 | Servicio | `core/*/*_service.py` | T2 |
| T4 | 4 | Router y DTOs | `core/*/api/*_router.py`, `*_models.py` | T3 |
| T5 | 5 | Tests | `tests/**` | *(empieza ya)* |
| T6 | 6 | Frontend | `frontend/src/**` | T4 |

**T5 y T6 arrancan de inmediato**, sin esperar a nadie: T5 traduce los criterios
Given/When/Then a tests que fallan (Red), y T6 escribe el tipo en `types.ts` y el
componente contra ese contrato. Si la HU no toca base de datos, T1 y T2 se
reasignan a documentación y a revisión de seguridad.

### Paso 4 — Cada uno implementa su ticket (~3 min)

En su asistente:

```
/speckit-implement T3
```

Y al terminar:

```bash
uv run pytest -q              # verde antes de subir, sin excepciones
uv run ruff check --fix .
git add -A && git commit -m "HU-11: implementa el servicio de favoritos"
git pull --rebase && git push
```

> **`git pull --rebase` antes de cada push.** Con seis personas en la misma
> rama, es la diferencia entre un historial limpio y diez minutos de conflictos
> en vivo.

### Paso 5 — Integrar y desplegar (~2 min)

```bash
git checkout main
git merge 005-nombre-corto
uv run pytest -q              # última verificación
git push origin main
```

Railway construye y despliega solo. **Muestren la pestaña de Deployments en
pantalla**: el build en vivo es parte del espectáculo.

Al terminar:

```bash
curl -i https://proyectoaplicandoiasddroullete-production.up.railway.app/api/health
```

Y abran la app para mostrar la funcionalidad nueva ya en producción.

---

## SECCIÓN 6 — CUANDO ALGO FALLA

### 6.1 Contingencias de la demostración

| Problema | Qué hacer | Costo |
|---|---|---|
| **No hay Internet** | `AI_PROVIDER=ollama` en local; muestren el flujo SDD y la app en `localhost`. El despliegue se enseña desde el móvil | 0 min |
| **Groq cae o agota cuota** | No hagan nada: entra en modo degradado sola. **Menciónenlo como característica**, porque lo es | 0 min |
| **Railway falla el build** | Muestren la app con `docker compose up`. El log del build queda como evidencia | 2 min |
| **Un test se pone rojo tras el merge** | `git revert` del commit culpable y redespliegue. **Nunca** desplieguen en rojo delante del profesor | 1 min |
| **Conflicto de merge feo** | El conductor resuelve; los demás **no tocan nada** | 2 min |
| **El asistente se atasca o alucina** | Corten y escriban el código a mano: la spec ya dice qué hacer. **Esa es justamente la ventaja de SDD** — díganlo en voz alta | 3 min |
| **Se pasan de tiempo** | Fusionen lo que esté listo y muestren `tasks.md` con los pendientes. El incremento parcial también es un resultado | — |

### 6.2 Problemas de despliegue

Consulta el diagnóstico primero:

```bash
curl -s https://proyectoaplicandoiasddroullete-production.up.railway.app/api/health/diagnostics | python3 -m json.tool
```

| Síntoma | Causa | Solución |
|---|---|---|
| `"degraded": true` y `api_key_present: false` | `GROQ_API_KEY` no llegó | Añadirla en Railway → Variables |
| `"degraded": true` con la clave presente | `AI_PROVIDER` no está en `groq` | Corregir la variable |
| `degraded: false` pero las descripciones son siempre la misma plantilla | Groq rechaza las llamadas | El modelo fue retirado. Verificar el id vigente en https://console.groq.com/docs/models y actualizar `GROQ_MODEL` |
| Healthcheck falla, log dice `MIGRATION FAILED` | `DATABASE_URL` mal referenciada | En Variables, usar el botón `{}` para insertar la referencia a Postgres |
| Healthcheck falla, log dice `connection to server at "localhost"` | Las variables **no se aplicaron** | En el canvas hay un botón **Deploy** con los cambios en cola. Dale clic |
| La app no arranca, el log menciona `CORS_ALLOWED_ORIGINS` | Pusieron `*` en producción | Poner el dominio exacto |
| `429` constantes durante la demo | Límite bajo para varios espectadores | Subir `RATE_LIMIT_REQUESTS` a 100 y redesplegar |

> **Regla de oro con Railway:** los cambios de variables quedan **en cola**
> hasta que se presiona **Deploy**. Si algo "no toma efecto", eso es lo primero
> que hay que revisar.

### 6.3 Comandos de emergencia

```bash
uv run pytest -q                      # la suite completa, rápido
uv run pytest tests/test_security -v  # solo lo que rompiste
docker compose up api postgres        # levantar todo en local, sin nube

uv run python project_jackpot.py      # backend  :9600
cd frontend && npm run dev            # frontend :5173 con proxy al backend

git reset --hard origin/main          # volver a un estado bueno conocido
```

---

## SECCIÓN 7 — MAPA DE RESPUESTAS PARA EL PROFESOR

| Si pregunta... | Abrir |
|---|---|
| ¿Cómo aplicaron SDD? | `.specify/memory/constitution.md` y `specs/001/` completo |
| ¿Dónde están las 10 HU? | `docs/backlog.md` |
| ¿Cómo garantizan calidad? | `uv run pytest` (210) + `.github/workflows/ci.yml` |
| ¿Qué hicieron en seguridad? | `docs/security.md` + demo en vivo (4.2) |
| ¿Cuánto cuesta operarlo? | `docs/business-case.md` — USD 0.00/mes |
| ¿Cuál es el ROI frente a lo tradicional? | `docs/business-case.md` §3.3 — 1 400 % |
| ¿Y si se cae la IA? | `specs/001/spec.md` FR-009 — modo degradado, ya ocurrió en producción |
| ¿Por qué no usaron Ollama en producción? | `specs/004/plan.md` D-01 — no cabe en capa gratuita |
| ¿Cómo trabajan en paralelo 6 personas? | `tasks.md` con tickets `[P]` de archivos disjuntos |
| ¿Cómo saben qué corre en producción? | `/api/health/diagnostics` |

---

## SECCIÓN 8 — LÍMITES CONOCIDOS (decirlos antes de que los encuentren)

Un equipo que declara sus límites se ve mejor que uno al que se los descubren.

1. **El rate limiting vive en memoria del proceso.** Con varias réplicas el
   límite se multiplica, y un reinicio lo resetea. Adecuado para una réplica en
   capa gratuita; migrar a Redis está identificado para la siguiente iteración.
   Documentado en `docs/security.md` §5.
2. **No hay autenticación.** Intencional: añadir cuentas multiplicaría la
   superficie de ataque sin aportar a los objetivos. Está en el backlog como
   *Won't have*.
3. **Groq free tier: ~1 000 peticiones/día.** Cada generación consume 2
   llamadas → techo de ~500 generaciones diarias.
4. **Sin alertado automático.** Los logs quedan en Railway; nadie recibe
   notificación ante un pico de errores.
5. **Los tiempos del caso de negocio son estimaciones**, declaradas como tales
   en `docs/business-case.md` §3.1. Los precios de proveedores sí están
   verificados y citados.

---

## SECCIÓN 9 — ÍNDICE DE DOCUMENTACIÓN

| Archivo | Contenido |
|---|---|
| `.specify/memory/constitution.md` | Los 7 principios no negociables |
| `AGENTS.md` | Reglas de código para humanos y agentes de IA |
| `docs/backlog.md` | Las 10 HU con criterios Given/When/Then |
| `docs/security.md` | Modelo de amenaza, OWASP, limitaciones |
| `docs/business-case.md` | ROI, OPEX/CAPEX, comparativa de metodologías |
| `docs/deployment.md` | Despliegue en Railway paso a paso |
| `docs/live-demo-runbook.md` | Versión extendida de las secciones 3 a 6 |
| `docs/endpoints.md` | Referencia de la API |
| `specs/001-generador-de-proyectos/` | Generación de proyectos (HU-01 a HU-06) |
| `specs/002-interfaz-tragamonedas/` | Frontend e historial (HU-07, HU-08) |
| `specs/003-endurecimiento-seguridad/` | Seguridad (HU-09) |
| `specs/004-despliegue-continuo/` | Despliegue y CI (HU-10) |
