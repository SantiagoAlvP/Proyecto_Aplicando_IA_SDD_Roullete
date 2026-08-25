# Quickstart: validar HU-22 de punta a punta

**Branch**: `022-health-db-check`

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

- `tests/test_health_db_check.py` — DB conectada, DB caída, DB no configurada, health siempre 200.

## 2. Recorrido feliz: DB conectada

```bash
docker compose up api postgres
```

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | `curl http://localhost:9600/api/health \| jq .database.connected` | `true` |
| 2 | `curl http://localhost:9600/api/health \| jq .database.configured` | `true` |
| 3 | `curl http://localhost:9600/api/health/diagnostics \| jq .database.connected` | `true` |

## 3. Recorrido: DB caída

```bash
docker compose stop postgres
# o: cambiar DATABASE_URL a un host inalcanzable
```

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | `curl http://localhost:9600/api/health \| jq .database.connected` | `false` |
| 2 | `curl http://localhost:9600/api/health \| jq .status` | `"healthy"` (siempre 200) |
| 3 | `curl http://localhost:9600/api/health/diagnostics \| jq .database.connected` | `false` |

## 4. Recorrido: DB no configurada

```bash
# Arrancar sin DATABASE_URL y sin variables DB_*
DATABASE_URL= uv run uvicorn core.main:app --port 9600
```

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | `curl http://localhost:9600/api/health \| jq .database.configured` | `false` |
| 2 | `curl http://localhost:9600/api/health \| jq .database.connected` | `false` |

## 5. Verificación de no exposición de errores

```bash
# Con DB caída, el body no debe contener mensajes de error de SQL
curl -s http://localhost:9600/api/health | grep -c "SELECT" # → 0
curl -s http://localhost:9600/api/health | grep -c "pg_"   # → 0
```
