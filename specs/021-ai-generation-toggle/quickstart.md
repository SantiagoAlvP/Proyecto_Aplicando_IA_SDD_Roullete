# Quickstart: validar HU-21 de punta a punta

**Branch**: `021-ai-generation-toggle`

## Prerrequisitos

```bash
uv sync                                   # dependencias Python
docker compose up -d postgres             # base de datos local
```

## 1. Puertas automatizadas

```bash
uv run pytest -q          # unitarios en verde
uv run ruff check
uv run ruff format --check
uv run ty check
```

Los tests nuevos que deben existir antes de dar por terminada la historia:

- `tests/test_ai_toggle.py` — toggle desactivado devuelve descripción de respaldo,
  no llama al gateway; diagnóstico refleja el estado.

## 2. Recorrido feliz: IA desactivada

```bash
AI_GENERATION_ENABLED=false docker compose up api
# o: AI_GENERATION_ENABLED=false uv run uvicorn core.main:app --port 9600
```

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | `curl http://localhost:9600/api/health/diagnostics \| jq .ai.ai_generation_enabled` | `false` |
| 2 | Generar un proyecto vía UI o `curl -X POST` | `201` con descripción de respaldo (texto template, no generada por IA) |
| 3 | Consultar historial | `200` con las entradas, incluyendo descripciones de respaldo |
| 4 | Abrir un enlace compartido | `200` con el proyecto completo |

## 3. Recorrido feliz: IA activada (default)

```bash
docker compose up api
# sin AI_GENERATION_ENABLED → default True
```

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | `curl http://localhost:9600/api/health/diagnostics \| jq .ai.ai_generation_enabled` | `true` |
| 2 | Generar un proyecto vía UI | `201` con descripción generada por IA (o de respaldo si el provider está caído) |

## 4. Recorridos negativos

| Acción | Resultado esperado |
|---|---|
| `AI_GENERATION_ENABLED=false` + generar proyecto | `201` con descripción de respaldo, sin error |
| `AI_GENERATION_ENABLED=` (vacío) | IA desactivada (fail-closed) |
| `AI_GENERATION_ENABLED= maybe` | IA desactivada (fail-closed) |
| `curl /api/health` con toggle desactivado | `200` con `{"status": "healthy"}` |

## 5. Verificación de diagnóstico

```bash
# Con IA activa:
curl -s http://localhost:9600/api/health/diagnostics | jq .ai.ai_generation_enabled
# → true

# Con IA desactivada:
AI_GENERATION_ENABLED=false uv run uvicorn core.main:app --port 9600 &
curl -s http://localhost:9600/api/health/diagnostics | jq .ai.ai_generation_enabled
# → false
```

## 6. Verificación de fail-closed

```bash
# Cualquier valor no truthy desactiva la IA:
for val in "false" "0" "no" "" "maybe" "2" "False" "NO"; do
  echo "AI_GENERATION_ENABLED=$val"
  AI_GENERATION_ENABLED=$val uv run python -c "
from core.settings.default import AppSettings
s = AppSettings()
print(f'  ai_generation_enabled={s.ai_generation_enabled}')
"
done
```

Salida esperada: todos los valores excepto los vacíos y "maybe"/"2" muestran `False`.
