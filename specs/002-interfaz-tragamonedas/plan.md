# Implementation Plan: Interfaz web tipo máquina tragamonedas

**Branch**: `002-interfaz-tragamonedas` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

## Summary

Aplicación de una sola página en React 19 + TypeScript compilada con Vite, que consume la
API existente. El bundle resultante se copia dentro de la imagen del backend y FastAPI lo
sirve como archivos estáticos en la raíz, de modo que frontend y API comparten origen
(sin CORS cruzado, un solo despliegue, un solo dominio).

Se añade un endpoint de historial en el dominio `ensemble_project`, respetando las capas ya establecidas.

## Technical Context

**Language/Version**: TypeScript 5.9 / React 19; Python 3.13 en el backend
**Primary Dependencies**: React, Vite. **Cero dependencias de UI de terceros** (CSS propio)
**Storage**: reutiliza PostgreSQL a través del repositorio existente
**Testing**: pytest para el endpoint de historial; `npm run build` como verificación de compilación en CI
**Target Platform**: navegadores modernos; el bundle se sirve desde el contenedor del backend
**Project Type**: web
**Performance Goals**: bundle < 300 KB comprimido; primera pintura < 1.5 s
**Constraints**: mismo origen que la API; sin dependencias de pago
**Scale/Scope**: 3 historias de usuario, 1 endpoint nuevo, ~6 componentes

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. SDD | Spec y plan escritos antes del primer componente. |
| II. Capas | El endpoint de historial sigue `router -> service -> repository`. Ningún componente de React conoce SQL. |
| III. Test-First | El endpoint de historial lleva tests de contrato, de límite y de lista vacía. |
| IV. Seguridad | El `limit` está acotado (`ge=1, le=50`) para impedir consultas sin cota. El frontend no maneja secretos. |
| V. Free-tier | Cero dependencias de UI de pago, cero servicios externos, mismo contenedor. |
| VI. Despliegue | El build del frontend es una etapa del Dockerfile multi-stage: un solo artefacto. |
| VII. YAGNI | Sin gestor de estado global, sin router de cliente, sin librería de componentes. El estado local de React alcanza. |

**Resultado**: PASS.

## Project Structure

```
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts            # proxy /api -> :9600 en desarrollo
└── src/
    ├── main.tsx
    ├── App.tsx               # estado del giro y composición de la pantalla
    ├── api.ts                # única capa que habla con el backend
    ├── types.ts              # tipos compartidos con los DTOs del backend
    ├── styles.css
    └── components/
        ├── Reel.tsx          # un rodillo: valor, bloqueo, animación
        ├── SlotMachine.tsx   # los tres rodillos + nivel + botón de girar
        ├── ResultCard.tsx    # combinación resultante y descripción
        └── History.tsx       # panel lateral de historial

core/ensemble_project/
├── api/ensemble_project_router.py     # + GET /history
├── ensemble_project_service.py        # + get_history()
└── ensemble_project_repository.py     # + list_recent()

core/main.py                           # + montaje de los archivos estáticos
```

**Structure Decision**: el frontend vive en el mismo repositorio para que una historia de
usuario que toque ambos lados quepa en un solo PR y en una sola spec. La alternativa
(repositorio separado) obligaría a coordinar dos despliegues durante la demostración en vivo.

## Decisiones de diseño

**D-01 — Mismo origen en lugar de Vercel + Railway.** Servir el bundle desde FastAPI elimina
la configuración de CORS, un segundo pipeline y una segunda variable de URL base.
*Alternativa descartada*: Vercel para el frontend. Se ve más moderno pero introduce un punto
de fallo adicional durante una demostración cronometrada.

**D-02 — Sin gestor de estado ni librería de componentes.** Tres rodillos, un nivel y una
lista caben en `useState`. Añadir Redux o Material UI sería complejidad sin problema que resolver
(Principio VII).

**D-03 — `api.ts` como única frontera.** Ningún componente llama a `fetch` directamente.
Si mañana cambia una ruta, cambia un archivo.

**D-04 — Animación por CSS, no por librería.** `@keyframes` sobre `transform: translateY`.
Cero kilobytes de JavaScript adicionales.

## Complexity Tracking

| Complejidad introducida | Por qué es necesaria | Alternativa más simple descartada |
|---|---|---|
| Etapa de build de Node en el Dockerfile | Es lo que permite un único artefacto desplegable con frontend y API dentro | Versionar el `dist/` compilado: contamina el repositorio y se desincroniza del código fuente |
| Endpoint de historial nuevo | La Historia 3 lo exige y la tabla `projects` ya guarda todo lo necesario | Guardar el historial en `localStorage`: se pierde entre dispositivos y desperdicia datos ya persistidos |
