# Implementation Plan: Endurecimiento de seguridad de la API

**Branch**: `003-endurecimiento-seguridad` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

## Summary

Se añade una capa transversal de seguridad implementada como middleware de FastAPI, más
el ajuste de los DTOs para acotar toda entrada, más dos análisis estáticos en CI.
Ninguna regla de negocio cambia: la seguridad se aplica en los bordes del sistema
(entrada HTTP y salida HTTP), no dentro de los servicios.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: FastAPI y Starlette (middleware nativo). **Sin dependencias nuevas en tiempo de ejecución**: el limitador se implementa con la biblioteca estándar
**Storage**: contadores del limitador en memoria del proceso (sin Redis; ver Complexity Tracking)
**Testing**: pytest sobre las cabeceras, el `429`, la forma del error y los límites de validación
**Target Platform**: contenedor detrás del proxy de Railway
**Project Type**: web
**Performance Goals**: sobrecarga del middleware < 1 ms por petición
**Constraints**: costo USD 0.00; no romper ninguno de los 131 tests existentes
**Scale/Scope**: 5 historias de usuario, 0 endpoints nuevos, 3 módulos nuevos

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. SDD | Spec y plan preceden al código. |
| II. Capas | La seguridad vive en middleware y en DTOs, no dentro de los servicios. Ningún servicio conoce códigos HTTP. |
| III. Test-First | Cada historia trae su test: `429`, cabeceras, forma del error, límites de validación. |
| IV. Seguridad | Esta spec **es** la materialización del Principio IV. Cada regla dura del principio se mapea a un requisito funcional. |
| V. Free-tier | Limitador en memoria en lugar de Redis gestionado: cero costo. |
| VI. Despliegue | Los análisis de seguridad son una puerta de CI previa al despliegue. |
| VII. YAGNI | Sin WAF, sin autenticación, sin gestor de secretos externo. Se añadirán cuando una spec los justifique. |

**Resultado**: PASS.

## Project Structure

```
core/security/
├── __init__.py
├── rate_limit.py        # RateLimitMiddleware: ventana deslizante en memoria
├── headers.py           # SecurityHeadersMiddleware
└── errors.py            # manejadores de excepciones + RequestContextMiddleware (request_id)

core/settings/
├── default.py           # + ENVIRONMENT, RATE_LIMIT_*, MAX_BODY_BYTES, cors_origins
└── middleware.py        # orquesta el orden de los middlewares

core/ensemble_project/api/
└── ensemble_project_models.py   # cotas explícitas en todos los DTOs

.github/workflows/ci.yml         # + gitleaks + pip-audit
.env.example                     # documenta las variables sin valores reales
docs/security.md                 # análisis OWASP y limitaciones conocidas
```

## Decisiones de diseño

**D-01 — Limitador propio en memoria, no `slowapi` ni Redis.** Una ventana deslizante con
`collections.deque` por cliente resuelve el requisito en ~60 líneas, sin dependencia nueva
y sin costo de infraestructura.
*Alternativa descartada*: Redis gestionado. Es la solución correcta para múltiples réplicas,
pero cuesta dinero y en capa gratuita el servicio corre en un solo proceso. La limitación
queda documentada en `docs/security.md` en lugar de disimulada.

**D-02 — El `request_id` viaja en la respuesta.** Se genera en un middleware, se adjunta al
estado de la petición, se incluye en la cabecera `X-Request-ID` y en el cuerpo del error.
Un usuario puede reportar "me falló con el id abc123" y el equipo encuentra la traza exacta.

**D-03 — Orden de los middlewares.** `RequestContext` → `SecurityHeaders` → `RateLimit` → `CORS`.
El contexto debe existir antes de que algo falle; las cabeceras deben aplicarse incluso a
las respuestas `429`; CORS va al final para que su preflight no consuma cuota del limitador.

**D-04 — CSP restrictiva compatible con el frontend.** `default-src 'self'` con
`style-src 'self' 'unsafe-inline'`, porque React inyecta estilos en línea. No se permite
`unsafe-eval` ni orígenes de scripts externos.

**D-05 — La validación es la primera línea de defensa.** Acotar `technologies` a 100 caracteres
y `extras` a 20 elementos en el DTO es más barato y más fiable que cualquier control posterior:
Pydantic rechaza antes de que el servicio se ejecute y, por tanto, antes de gastar cuota del LLM.

## Complexity Tracking

| Complejidad introducida | Por qué es necesaria | Alternativa más simple descartada |
|---|---|---|
| Cuatro middlewares en lugar de uno | Cada uno tiene una única responsabilidad y se prueba por separado (SRP) | Un middleware que lo haga todo: imposible de probar de forma aislada y difícil de ordenar |
| `request_id` propagado por toda la petición | Sin correlación, un error en producción es inauditable | Registrar solo la excepción: no permite ligar el reporte del usuario con la traza |

## Limitación conocida (documentada, no oculta)

El limitador mantiene su estado en memoria del proceso. Con múltiples réplicas, el límite
efectivo se multiplica por el número de réplicas, y un reinicio lo reinicia. Es una defensa
de mejor esfuerzo adecuada al despliegue actual (una réplica en capa gratuita).
Migrar a Redis es una tarea ya identificada para la siguiente iteración.
