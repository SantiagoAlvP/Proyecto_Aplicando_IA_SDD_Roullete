# Runbook de la demostración en vivo

**Equipo:** 6 integrantes
**Objetivo:** construir 2 Historias de Usuario asignadas por el profesor, con el
motor SDD corriendo en la máquina de cada integrante, y dejarlas **desplegadas**
en 5–10 minutos por spec.

---

## Parte 0 — Preparación (hacer ANTES de la presentación)

> Esto no se hace en vivo. Si alguien llega a la sala sin el paso 0 completo,
> el equipo pierde 10 minutos que no tiene.

### 0.1 Cada integrante, en su máquina

```bash
# 1. Herramientas base
#    - Python 3.12+, Node 22+, Git
#    - uv:  curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clonar y preparar
git clone https://github.com/SantiagoAlvP/Proyecto_Aplicando_IA_SDD_Roullete.git
cd Proyecto_Aplicando_IA_SDD_Roullete
uv sync
cd frontend && npm install && cd ..

# 3. Instalar el motor SDD (GitHub Spec Kit)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify check          # verifica que el agente de IA está disponible

# 4. Comprobar que la suite pasa ANTES de tocar nada
uv run pytest -q       # debe decir: 204 passed
```

### 0.2 Verificación de que el motor responde

Abre tu asistente (Claude Code o GitHub Copilot en VS Code) dentro del repositorio
y escribe `/speckit-` — deben aparecer los comandos `constitution`, `specify`,
`clarify`, `plan`, `tasks`, `analyze`, `implement`.

Si no aparecen, reinstala la integración:

```bash
specify init --here --force --integration claude    # o --integration copilot
```

### 0.3 Prueba en seco (ensayar el día anterior)

Inventen una HU cualquiera ("quiero poder marcar un proyecto como favorito"),
corran el flujo completo de principio a fin y midan cuánto tardan. **El ensayo es
lo que convierte 20 minutos improvisados en 8 minutos controlados.**

### 0.4 Checklist de la sala

- [ ] La URL pública responde: `curl -i https://TU-DOMINIO.up.railway.app/api/health`
- [ ] `main` está limpia y sin cambios sin fusionar
- [ ] Los 6 tienen `uv run pytest` en verde localmente
- [ ] Alguien tiene permisos de merge en GitHub
- [ ] Segunda conexión a Internet disponible (hotspot del teléfono)
- [ ] `RATE_LIMIT_REQUESTS` subido a 60 si el profesor va a probar la app desde su equipo

---

## Parte 1 — Guion de la presentación (línea base, ~8 min)

| Min | Quién | Qué muestra |
|---|---|---|
| 0–1 | Integrante 1 | La aplicación desplegada. Gira los rodillos, sale una idea con descripción de IA |
| 1–2 | Integrante 1 | Fija "Rust", vuelve a girar: se respeta. Muestra el historial actualizándose |
| 2–4 | Integrante 2 | `.specify/memory/constitution.md`: los 7 principios. **Este es el corazón de SDD** |
| 4–5 | Integrante 2 | `specs/001/spec.md` → `plan.md` → `tasks.md`: el recorrido de una idea a tickets |
| 5–6 | Integrante 3 | `docs/backlog.md`: las 10 HU con criterios Given/When/Then |
| 6–7 | Integrante 4 | `uv run pytest`: 204 tests en verde. Enseña cómo un criterio de aceptación de la spec **es** un test (`test_rate_limit.py`) |
| 7–8 | Integrante 5 | Seguridad en vivo: bucle de `curl` → `429` con `Retry-After`. Fuerza un error → `500` con `request_id` y **sin stack trace** |

**La frase que hay que decir en el minuto 4:**

> "La decisión de poner el modelo de lenguaje detrás de una interfaz la tomamos en
> el `plan.md` de la primera spec, antes de escribir código. Cuando descubrimos que
> Ollama no cabe en ninguna capa gratuita, cambiar a Groq costó una variable de
> entorno. Sin esa decisión escrita, eso son tres días de reescritura."

Es el mejor argumento del proyecto y es verificable en el repositorio.

---

## Parte 2 — Construcción en vivo de una HU (5–10 min por spec)

### Paso 1 — Crear la spec (1 integrante, ~2 min)

Quien conduzca escribe en el asistente, **con el enunciado del profesor tal cual**:

```
/speckit-specify Como <rol>, quiero <capacidad>, para <beneficio>.
```

Spec Kit crea la rama `005-nombre-corto` y `specs/005-nombre-corto/spec.md`.

Revisen en pantalla los criterios de aceptación y resuelvan las ambigüedades:

```
/speckit-clarify
```

> **Mostrar los `[NEEDS CLARIFICATION]` es parte de la demostración.** Es la
> evidencia visible de que la metodología obliga a resolver la ambigüedad antes
> de codificar, en lugar de dejar que el modelo la invente.

### Paso 2 — Plan y tickets (~2 min)

```
/speckit-plan
/speckit-tasks
```

`tasks.md` sale con los tickets marcados `[P]` cuando son paralelizables.

### Paso 3 — Reparto de los 6 tickets

Empujen la rama para que todos la tengan:

```bash
git push -u origin 005-nombre-corto
```

El resto:

```bash
git fetch && git checkout 005-nombre-corto
```

**Plantilla de reparto** — casi cualquier HU de esta aplicación se descompone así:

| # | Integrante | Rol | Archivos que toca | Depende de |
|---|---|---|---|---|
| T1 | 1 | Modelo y migración | `core/database/models.py`, `alembic/versions/` | — |
| T2 | 2 | Repositorio (acceso a datos) | `core/*/[dominio]_repository.py`, `core/database/crud.py` | T1 |
| T3 | 3 | Servicio (reglas de negocio) | `core/*/[dominio]_service.py` | T2 |
| T4 | 4 | Router y DTOs | `core/*/api/*_router.py`, `*_models.py` | T3 |
| T5 | 5 | Tests | `tests/**` | *(puede empezar ya: escribe los tests desde los criterios de aceptación)* |
| T6 | 6 | Frontend | `frontend/src/**` | T4 (pero el tipo se puede escribir antes) |

**Los tickets T5 y T6 arrancan de inmediato**, sin esperar a nadie: T5 traduce
los criterios Given/When/Then a tests que fallan (Red), y T6 escribe el tipo en
`types.ts` y el componente contra ese contrato. Si la HU no toca base de datos,
T1 y T2 se reasignan a documentación (`docs/`) y a revisión de seguridad.

### Paso 4 — Cada integrante implementa su ticket (~3 min)

En su asistente:

```
/speckit-implement T3
```

o, si prefieren dirigirlo a mano, le indican al agente el ticket concreto de
`tasks.md`. Cada uno hace **un commit**:

```bash
uv run pytest -q          # verde antes de subir, sin excepciones
uv run ruff check --fix .
git add -A && git commit -m "HU-11: implementa el servicio de favoritos"
git pull --rebase && git push
```

> `git pull --rebase` antes de cada push. Con seis personas en la misma rama,
> es la diferencia entre un historial limpio y diez minutos de conflictos en vivo.

### Paso 5 — Integrar y desplegar (~2 min)

Quien conduzca:

```bash
git checkout main
git merge 005-nombre-corto
uv run pytest -q                 # última verificación
git push origin main
```

Railway construye y despliega solo. Mientras tanto, muestren la pestaña de
**Deployments** en pantalla: el build en vivo es parte del espectáculo.

Al terminar:

```bash
curl -i https://TU-DOMINIO.up.railway.app/api/health
```

Y abran la aplicación para mostrar la funcionalidad nueva ya en producción.

---

## Parte 3 — Plan de contingencia

Lo que puede salir mal y qué hacer sin perder la calma:

| Problema | Qué hacer | Cuánto cuesta |
|---|---|---|
| **No hay Internet** | `AI_PROVIDER=ollama` en local; muestren el flujo SDD y la app corriendo en `localhost`. El despliegue se muestra desde el móvil | 0 min |
| **Groq cae o agota la cuota** | No hagan nada: la app entra en modo degradado sola y sigue respondiendo. **Menciónenlo como característica**, porque lo es | 0 min |
| **Railway falla el build** | Muestren la app corriendo en local con `docker compose up`. El log del build queda como evidencia | 2 min |
| **Un test se pone rojo tras el merge** | `git revert` del commit culpable, redesplieguen, y arreglen después. **Nunca** desplieguen con la suite en rojo delante del profesor | 1 min |
| **Conflicto de merge feo** | El conductor resuelve; los demás **no tocan nada**. Seis personas resolviendo el mismo conflicto es peor que una | 2 min |
| **El agente de IA se atasca o alucina** | Corten y escriban el código a mano: la spec ya dice exactamente qué hacer. **Esa es justamente la ventaja de SDD** y conviene decirlo en voz alta | 3 min |
| **La demo se pasa de tiempo** | Fusionen lo que esté listo y muestren `tasks.md` con los tickets pendientes marcados. El incremento parcial también es un resultado válido | — |

---

## Parte 4 — Qué evalúa el profesor y dónde está

| Requisito del enunciado | Dónde demostrarlo |
|---|---|
| Frontend integrado | La raíz de la URL pública |
| Backend / APIs | `/api/docs` en el mismo dominio |
| Base de datos | El historial persiste entre recargas; `alembic/versions/` |
| Herramienta SDD (Spec Kit) | `.specify/`, `specs/001` a `004`, y el flujo en vivo |
| Despliegue gratuito e integrado | Railway, `railway.json`, `docs/deployment.md` |
| Pruebas automatizadas | `uv run pytest` → 204 tests |
| Prácticas de seguridad | `docs/security.md`, el `429` en vivo, `gitleaks` y `pip-audit` en CI |
| 10 HU en la línea base | `docs/backlog.md` |
| 2 HU construidas en vivo | Esta sección, ejecutada |
| Cada integrante ejecuta el motor SDD | Los 6 corriendo `/speckit-implement` en su propia máquina |
| Caso de negocio y comparativa de costos | `docs/business-case.md` |

---

## Parte 5 — Comandos de emergencia

```bash
# La suite completa, rápido
uv run pytest -q

# Solo lo que rompiste
uv run pytest tests/test_security -v

# Levantar todo en local (sin nube)
docker compose up api postgres

# Backend y frontend por separado, con recarga en caliente
uv run python project_jackpot.py          # :9600
cd frontend && npm run dev                 # :5173, con proxy a :9600

# Volver a un estado bueno conocido
git reset --hard origin/main

# Ver qué proveedor de IA está activo
grep "ai_provider=" <(uv run python -c "from core.main import app" 2>&1)
```
