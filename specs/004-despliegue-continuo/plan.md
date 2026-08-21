# Implementation Plan: Despliegue continuo en la nube

**Branch**: `004-despliegue-continuo` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

## Summary

Dockerfile multi-stage que compila el frontend con Node y lo empaqueta junto al backend de
Python en una sola imagen. Railway construye esa imagen desde `main`, inyecta `DATABASE_URL`
y `PORT`, y verifica `/api/health`. GitHub Actions actúa como puerta previa: si tests, lint,
tipos, escaneo de secretos o auditoría de dependencias fallan, no hay despliegue.

El cambio arquitectónico que hace esto posible es sustituir Ollama por un proveedor de IA
con capa gratuita: Ollama necesita gigabytes de RAM y no cabe en ninguna capa gratuita,
mientras que la interfaz `AIGateway` permite cambiarlo con una variable de entorno.

## Technical Context

**Language/Version**: Python 3.13, Node 22 (solo en la etapa de build)
**Primary Dependencies**: Docker multi-stage, GitHub Actions, Railway
**Storage**: PostgreSQL gestionado por Railway (capa gratuita)
**Testing**: el pipeline de CI es la prueba; verificación de salud como prueba de humo posterior al despliegue
**Target Platform**: Railway (contenedor Linux)
**Project Type**: web
**Performance Goals**: build + despliegue en menos de 10 minutos
**Constraints**: USD 0.00 al mes; una sola réplica; sin GPU
**Scale/Scope**: 4 historias de usuario, 0 endpoints nuevos

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. SDD | Spec y plan preceden a la configuración. |
| II. Capas | Sin cambios en la arquitectura de la aplicación: solo empaquetado y configuración. |
| III. Test-First | CI ejecuta la suite completa antes de permitir el despliegue. |
| IV. Seguridad | Todos los secretos por variable de entorno en la plataforma. CI bloquea secretos versionados y dependencias vulnerables. |
| V. Free-tier | Railway (créditos de estudiante) + PostgreSQL gestionado + Groq: USD 0.00. Detalle en `docs/business-case.md`. |
| VI. Despliegue | Esta spec **es** la materialización del Principio VI. |
| VII. YAGNI | Sin Kubernetes, sin Terraform, sin múltiples entornos. Una plataforma, un entorno, un artefacto. |

**Resultado**: PASS.

## Project Structure

```
Dockerfile                     # etapa 1: build del frontend con Node · etapa 2: runtime de Python
docker-compose.yml             # desarrollo local: api + postgres + ollama
railway.json                   # comando de arranque, verificación de salud y política de reinicio
entrypoint.sh                  # migraciones -> siembra -> uvicorn en $PORT
.github/workflows/ci.yml       # tests, lint, tipos, secretos, auditoría, build del frontend
.env.example                   # contrato de configuración
docs/deployment.md             # procedimiento paso a paso
```

## Decisiones de diseño

**D-01 — Fuera Ollama de producción.** Ollama requiere varios GB de RAM para servir un modelo;
ninguna capa gratuita lo ofrece. Groq expone una API compatible con OpenAI con capa gratuita
y latencia muy baja. Como el LLM ya estaba detrás de `AIGateway`, el cambio es
`AI_PROVIDER=groq` más una clave. Ollama permanece como proveedor de desarrollo local.
*Esta es la prueba práctica de que la decisión D-01 de la spec 001 valía la pena.*

**D-02 — Un artefacto, no dos.** El frontend se compila dentro de la imagen y FastAPI lo sirve.
*Alternativa descartada*: Vercel para el frontend y Railway para la API. Implica dos pipelines,
dos URLs, configuración de CORS y un segundo punto de fallo en mitad de una demostración cronometrada.

**D-03 — `entrypoint.sh` en lugar de migraciones en el código de la aplicación.** Migrar es una
tarea de despliegue, no de tiempo de ejecución. Un script explícito permite ver en los logs
exactamente qué pasó y detener el arranque si una migración falla.

**D-04 — CI como puerta, Railway como ejecutor.** Railway despliega al detectar cambios en `main`;
GitHub Actions protege `main` con revisión obligatoria de estado. El resultado neto es que a
producción solo llega código verificado.

**D-05 — Salud sin base de datos.** `/api/health` responde sin consultar PostgreSQL, para que
un arranque en frío de la base de datos no haga fallar la verificación de vida.

## Complexity Tracking

| Complejidad introducida | Por qué es necesaria | Alternativa más simple descartada |
|---|---|---|
| Dockerfile multi-stage | Mantiene la imagen final pequeña: Node solo existe durante el build | Instalar Node en la imagen final: imagen mucho mayor y más superficie de ataque |
| `entrypoint.sh` propio | Necesitamos ordenar migraciones antes de servir, y fallar ruidosamente si algo va mal | `CMD` directo a uvicorn: arranca con un esquema potencialmente desactualizado |
| Un proveedor de IA distinto entre local y producción | Restricciones opuestas: local sin red pero con RAM, producción con red pero sin RAM | Usar el mismo en ambos: o rompe el desarrollo sin conexión, o rompe el despliegue gratuito |
