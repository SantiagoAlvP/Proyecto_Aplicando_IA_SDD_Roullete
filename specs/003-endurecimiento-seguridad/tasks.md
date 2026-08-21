# Tasks: Endurecimiento de seguridad de la API

**Input**: [spec.md](./spec.md) · [plan.md](./plan.md)
**Branch**: `003-endurecimiento-seguridad`

## Fase 1 — Configuración (bloquea el resto)

- [X] **T001** Añadir a `AppSettings`: `ENVIRONMENT`, `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS`, `RATE_LIMIT_EXEMPT_PATHS`, `MAX_BODY_BYTES`, `CORS_ALLOWED_ORIGINS` → `core/settings/default.py`
- [X] **T002** Añadir la propiedad `cors_origins` que resuelve la lista blanca por entorno y **falla al arrancar** si en producción se configura `*` → `core/settings/default.py`
- [X] **T003** Crear `.env.example` documentando cada variable sin valores reales → `.env.example`

## Fase 2 — Middlewares (Historias 1, 2 y 3)

- [X] **T004** `[P]` `RequestContextMiddleware`: genera el `request_id`, lo adjunta al estado de la petición y a la cabecera `X-Request-ID`, y registra método, ruta, estado y duración → `core/security/errors.py`
- [X] **T005** `[P]` `SecurityHeadersMiddleware`: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`, `Permissions-Policy` y HSTS solo en producción → `core/security/headers.py`
- [X] **T006** `[P]` `RateLimitMiddleware`: ventana deslizante en memoria, identificación por `X-Forwarded-For` o IP, exención de rutas y `Retry-After` en el `429` → `core/security/rate_limit.py`
- [X] **T007** `[P]` `BodySizeLimitMiddleware`: rechaza con `413` los cuerpos que exceden `MAX_BODY_BYTES` → `core/security/rate_limit.py`
- [X] **T008** Manejadores de excepciones: `HTTPException`, `RequestValidationError` y `Exception` genérica, todos con `request_id` y sin filtrar detalles internos → `core/security/errors.py`
- [X] **T009** Registrar los middlewares en el orden correcto y conectar los manejadores → `core/settings/middleware.py`

## Fase 3 — Validación de entrada (Historia 4)

- [X] **T010** Acotar todos los campos de texto de los DTOs con `min_length`/`max_length` y limitar la lista de extras → `core/ensemble_project/api/ensemble_project_models.py`
- [X] **T011** Acotar el `limit` del historial (`ge=1, le=50`) → `core/ensemble_project/api/ensemble_project_router.py`

## Fase 4 — Puertas de CI (Historia 5)

- [X] **T012** `[P]` Añadir el escaneo de secretos con gitleaks al pipeline → `.github/workflows/ci.yml`
- [X] **T013** `[P]` Añadir la auditoría de dependencias con pip-audit al pipeline → `.github/workflows/ci.yml`
- [X] **T014** `[P]` Añadir gitleaks también a los hooks de pre-commit → `.pre-commit-config.yaml`

## Fase 5 — Pruebas y documentación

- [X] **T015** `[P]` Tests de cabeceras de seguridad: presentes siempre; HSTS solo en producción → `tests/test_security/test_headers.py`
- [X] **T016** `[P]` Tests del limitador: `429` tras el límite, `Retry-After`, aislamiento entre clientes, exención del endpoint de salud → `tests/test_security/test_rate_limit.py`
- [X] **T017** `[P]` Tests del manejo de errores: sin fuga de trazas, con `request_id` presente → `tests/test_security/test_errors.py`
- [X] **T018** `[P]` Tests de validación: payload sobredimensionado, cadena demasiado larga y nivel fuera de rango → `tests/test_security/test_input_validation.py`
- [X] **T019** Redactar `docs/security.md`: análisis OWASP Top 10, controles implementados y limitaciones conocidas → `docs/security.md`

## Dependencias

```
Fase 1 ──▶ Fase 2 ──▶ Fase 5
       └──▶ Fase 3 ──┘
Fase 4 (independiente)
```

## Reparto sugerido (6 integrantes)

| Integrante | Tareas |
|---|---|
| 1 | T001–T003 (configuración) |
| 2 | T004, T008 (contexto y errores) |
| 3 | T005 (cabeceras) |
| 4 | T006, T007 (limitador y tamaño del cuerpo) |
| 5 | T010, T011 (validación de entrada) |
| 6 | T012–T014 (puertas de CI) |
