# Research: HU-20 Compartir proyectos mediante enlace público

**Branch**: `020-compartir-enlace-publico` | **Date**: 2026-08-23

> Nota: la pregunta de clarificación sobre el formato del identificador público quedó
> abierta en `/speckit-clarify` sin respuesta. Se adoptó aquí la opción recomendada (A)
> por ser el patrón estándar de la industria para enlaces tipo "no listado". Si el equipo
> prefiere otra, es una decisión barata de revertir ANTES de escribir la migración (T004).

## D-01 — Identificador público: token opaco no adivinable

- **Decision**: columna `projects.share_token` generada con `secrets.token_urlsafe(12)`
  (~16 caracteres URL-safe, ~96 bits de entropía), única e indexada. La URL pública es
  `/proyecto/{share_token}`.
- **Rationale**: cualquiera con el enlace entra (sin cuentas, según los supuestos de la
  spec), pero nadie puede enumerar proyectos ajenos probando identificadores. Cumple
  FR-006 (enlace estable y permanente) porque el token vive junto al proyecto.
- **Alternatives considered**:
  - *ID secuencial visible*: simple, pero permite recorrer todos los proyectos cambiando
    el número; rompe la expectativa razonable de privacidad de quien comparte.
  - *UUID de 36 caracteres*: misma seguridad, URLs más largas sin beneficio adicional.
  - *ID secuencial interno + token solo en la URL*: dos identificadores que mantener;
    el ID secuencial deja de tener valor de exposición si nadie lo consume.

## D-02 — Persistir `level` y `created_at` en `projects`

- **Decision**: la migración añade también `level` (entero 1–5, anulable) y
  `created_at` (timestamp con zona, no nulo para filas nuevas).
- **Rationale**: FR-002 obliga a mostrar el nivel en la vista pública, pero hoy el nivel
  se descarta al guardar (`save_project` nunca lo persiste; solo sobrevive en la respuesta
  HTTP de generación). La Key Entity de la spec declara visible la fecha de creación.
- **Alternatives considered**: derivar el nivel desde el conteo de extras — frágil y falso.

## D-03 — Vista pública como ruta del SPA existente, sin librería de routing

- **Decision**: `App.tsx` inspecciona `window.location.pathname`; si coincide con
  `/proyecto/{token}`, renderiza la vista pública. Sin `react-router`.
- **Rationale**: hay exactamente una ruta nueva; `core/main.py` ya hace fallback de
  cualquier ruta desconocida al `index.html` (client-side routing listo). Añadir una
  dependencia para un caso sería complejidad injustificada (Principio VII).
- **Alternatives considered**: react-router-dom — útil con ≥3–4 rutas; hoy es peso muerto.

## D-04 — Datos de la vista vía endpoint JSON, no HTML del servidor

- **Decision**: `GET /api/v1/ensemble_project/shared/{share_token}` devuelve el DTO
  completo (combinación, extras, nivel, descripción); el SPA lo renderiza.
- **Rationale**: respeta el patrón existente (API JSON + SPA de mismo origen) y las capas
  `router -> service -> repository`. El parámetro de ruta va acotado
  (`min_length=10, max_length=64`, patrón `[A-Za-z0-9_-]+`) según el Principio IV.
- **Rate limiting**: hereda el middleware global existente; no es un endpoint de LLM,
  así que no requiere cuota propia (Principio IV).

## D-05 — Alcance retroactivo (FR-007)

- **Decision**: la migración rellena `share_token` de todas las filas existentes dentro
  de la propia migración (loop con `secrets.token_urlsafe`); los niveles históricos
  quedan `NULL`.
- **Rationale**: SC-003 exige que el 100 % del historial tenga enlace funcional. El
  volumen de datos de la demo es pequeño; hacer el backfill en Python dentro de la
  migración mantiene un único formato de token.

## D-06 — Copiar al portapapeles con degradación digna (FR-005)

- **Decision**: botón "Compartir" usa `navigator.clipboard.writeText`; si falla o no está
  disponible (HTTP sin TLS, permisos), muestra el enlace completo seleccionable y copia
  vía `textarea` + `execCommand('copy')` como segundo intento. Confirmación visual breve.
- **Rationale**: cubre navegadores que bloquean el Clipboard API sin mostrar error crudo
  al usuario, tal como pide el escenario 3 de la Historia 2.

## Errores y mensajes (FR-008)

- Token inexistente o mal formado → `404` con mensaje neutro ("Proyecto no disponible");
  el detalle técnico queda en el log con identificador de correlación. Nunca stack traces
  ni nombres de tablas (Principio IV).
- El SPA muestra la página amigable de la Historia 3 tanto para 404 como para token con
  formato inválido detectado en cliente (ni siquiera llama a la API).

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Colisión de tokens | Restricción UNIQUE; con 96 bits la probabilidad es despreciable |
| Filas legadas sin nivel | DTO admite `null`; la vista muestra texto neutral ("Nivel no registrado") |
| Enlaces compartidos antes de un cambio de dominio | El frontend construye el enlace con `window.location.origin`; el token es lo único estable |
