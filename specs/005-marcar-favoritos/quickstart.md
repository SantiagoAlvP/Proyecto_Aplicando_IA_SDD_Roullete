# Quickstart: validar "marcar como favorito"

Prerrequisitos: entorno local ya funcionando según el quickstart de
`001-generador-de-proyectos` (Postgres arriba, `uv run` disponible, migraciones aplicadas).

## 1. Levantar el backend con la migración aplicada

```bash
uv run alembic upgrade head
uv run uvicorn core.main:app --reload --port 9600
```

Verificar que la migración `add_favorite_and_level_to_projects` corrió sin error y que
`GET /api/health` responde `200`.

## 2. Generar un proyecto y capturar su `id`

```bash
curl -s -X POST http://localhost:9600/api/v1/ensemble_project/generate_project_totally_random \
  | tee /tmp/project.json | jq '.id, .favorite, .level, .extras'
```

**Resultado esperado**: `id` es un entero, `favorite` es `false`, `level` y `extras` vienen
poblados igual que antes de esta funcionalidad (contrato en `contracts/favorites-api.md`,
ver "Cambios en endpoints existentes").

## 3. Marcarlo como favorito (US1)

```bash
PROJECT_ID=$(jq '.id' /tmp/project.json)
curl -s -X PUT http://localhost:9600/api/v1/ensemble_project/$PROJECT_ID/favorite | jq '.favorite'
```

**Resultado esperado**: `true`.

## 4. Repetir el marcado (idempotencia, FR-005)

```bash
curl -s -X PUT http://localhost:9600/api/v1/ensemble_project/$PROJECT_ID/favorite -w '\n%{http_code}\n'
```

**Resultado esperado**: `200`, sin error, `favorite` sigue en `true` (no hay duplicado que listar).

## 5. Consultar la lista de favoritos (US2)

```bash
curl -s http://localhost:9600/api/v1/ensemble_project/favorites | jq
```

**Resultado esperado**: una lista con exactamente el proyecto marcado, `favorite: true` en
todos los elementos, `level` y `extras` presentes (FR-009), orden del más reciente al más
antiguo.

## 6. Desmarcarlo (US3)

```bash
curl -s -X DELETE http://localhost:9600/api/v1/ensemble_project/$PROJECT_ID/favorite | jq '.favorite'
curl -s http://localhost:9600/api/v1/ensemble_project/favorites | jq 'length'
```

**Resultado esperado**: `favorite` en `false`; la lista de favoritos vuelve a tener longitud `0`.

## 7. Casos de error

```bash
# id inexistente -> 404, sin alterar nada
curl -s -o /dev/null -w '%{http_code}\n' -X PUT http://localhost:9600/api/v1/ensemble_project/999999/favorite

# limit fuera de rango -> 422
curl -s -o /dev/null -w '%{http_code}\n' "http://localhost:9600/api/v1/ensemble_project/favorites?limit=999"
```

**Resultado esperado**: `404` y `422` respectivamente.

## 8. Verificación end-to-end en la interfaz

```bash
cd frontend && npm run build
```

Con el backend corriendo y el bundle servido desde el mismo origen: girar los rodillos, marcar
el resultado como favorito, recargar la página y confirmar que la pestaña "Favoritos" lo
muestra sin haber vuelto a girar (Success Criteria SC-002 y SC-003 de la spec).
