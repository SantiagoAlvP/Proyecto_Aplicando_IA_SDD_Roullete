# Quickstart: validar HU-20 de punta a punta

**Branch**: `020-compartir-enlace-publico`

## Prerrequisitos

```bash
uv sync                                   # dependencias Python
cd frontend && npm install && cd ..       # dependencias del SPA
docker compose up -d postgres             # base de datos local
```

## 1. Puertas automatizadas

```bash
uv run pytest -q          # unitarios en verde (los de integración se saltan sin servicios)
uv run ruff check
uv run ruff format --check
uv run ty check
```

Los tests nuevos que deben existir antes de dar por terminada la historia:

- `tests/test_database/test_crud.py` — token/level/created_at persistidos; `get_by_share_token`.
- `tests/test_fastapi_endpoints/test_shared_project.py` — contrato del endpoint público:
  200 con forma completa, 404 neutro, 422 con token fuera de cotas, sin filtraciones técnicas.
- `tests/test_fastapi_endpoints/test_history.py` — cada entrada expone `share_token`.

## 2. Levantar y recorrer el feliz

```bash
docker compose up api        # o: uv run uvicorn core.main:app --port 9600
cd frontend && npm run dev   # proxy /api -> :9600
```

| Paso | Acción | Resultado esperado |
|---|---|---|
| 1 | Girar la máquina en `/` | La tarjeta de resultado incluye el botón "Compartir" |
| 2 | Pulsar "Compartir" | Enlace `{origin}/proyecto/{token}` copiado + confirmación visual |
| 3 | Abrir ese enlace (ventana privada, sin sesión) | Se ve combinación completa, nivel y descripción; nada que girar; CTA hacia la máquina |
| 4 | Pulsar "Compartir" sobre una entrada del historial | El enlace copiado corresponde a ESE proyecto |
| 5 | Abrir `/` desde 360 px | Historial y vista pública usables |

## 3. Recorridos negativos

| Acción | Resultado esperado |
|---|---|
| Abrir `/proyecto/token-quenoexiste` (bien formado) | Página "Proyecto no disponible" + botón hacia la máquina |
| Abrir `/proyecto/!!` (mal formado) | Misma página amigable, sin llamada al API ni texto técnico |
| `curl -i /api/v1/ensemble_project/shared/nope-token-inexistente` | `404` con `detail` neutro; sin stack trace ni nombres de tablas |

## 4. Retroactividad (SC-003)

Con datos previos a la migración:

```bash
docker compose exec postgres psql -U jackpot -c "SELECT count(*), count(share_token) FROM projects;"
```

Ambos conteos iguales: todo proyecto antiguo tiene enlace funcional.

## 5. Portapapeles bloqueado

En las DevTools, denegar permisos del portapapeles y pulsar "Compartir": el enlace se
muestra completo y seleccionable, sin error aparente para el usuario.
