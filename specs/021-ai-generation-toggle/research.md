# Research: HU-21 Desactivar generación por IA mediante variable de entorno

**Branch**: `021-ai-generation-toggle` | **Date**: 2026-08-25

## D-01 — El toggle se evalúa por instancia de `AppSettings`, no por caché global

- **Decision**: la variable `AI_GENERATION_ENABLED` se lee como campo de `AppSettings`
  (pydantic-settings). Como `AppSettings()` se instancia en cada petición de generación
  (vía `get_project_service` → `AppSettings()`), un cambio en la variable de entorno
  surte efecto tras reinicio del contenedor, sin rebuild.
- **Rationale**: FR-001 pide lectura "al momento de cada petición"; la arquitectura
  existente ya instancia `AppSettings()` por petición en los routers, así que el
  patrón es natural y no requiere inyección adicional.
- **Alternatives considered**:
  - *Caché global leída una vez*: más eficiente pero FR-001 lo prohíbe explícitamente.
  - *Lectura directa de `os.environ`*: evita pydantic-settings pero pierde validación
    y documentación automática en `/api/docs`.

## D-02 — Parsing de valores truthy/falsy

- **Decision**: el setting es un `bool` con default `True`. Pydantic-settings convierte
  automáticamente los strings `"true"`, `"1"`, `"on"` (case-insensitive) a `True` y
  cualquier otro valor a `False` (incluyendo `"false"`, `"0"`, `""`, `"no"`).
  Esto cumple FR-002 (fail-closed) sin lógica custom de parsing.
- **Rationale**: pydantic-settings ya resuelve el problema de conversión de env vars
  a tipos Python. Un `bool` field es el tipo correcto para un toggle binario.
- **Alternatives considered**:
  - *String parsing manual*: reintroduce código que pydantic ya resuelve.
  - *Enum con valores allowlist*: más estricto pero más complejo para un binario.

## D-03 — Reutilización del `StubGateway` existente

- **Decision**: cuando el toggle desactiva la IA, `AIProjectAdvisor` reemplaza
  `self._gateway` por `self._fallback` (un `StubGateway` que ya existe como atributo
  del advisor). Esto afecta tanto a `generate_description` como a `choose_valid_project`.
- **Rationale**: el `StubGateway` ya está diseñado para esto: genera descripciones
  determinísticas y acepta el primer candidato. No hay que crear nueva lógica.
  Constitución V (Principle V) exige que "el sistema arranque y responda aunque no
  haya proveedor de IA disponible"; el stub cumple exactamente esto.
- **Alternatives considered**:
  - *Nuevo gateway `DisabledGateway`*: duplica la funcionalidad del stub.
  - *Flag en el gateway existente*: viola el principio de que el gateway es intercambiable.

## D-04 — El diagnóstico existente se amplía, no se crea uno nuevo

- **Decision**: se añade `"ai_generation_enabled": bool` al diccionario que devuelve
  `/api/health/diagnostics`. El campo se lee directamente de `settings` en cada petición.
- **Rationale**: FR-006 pide que el endpoint "indique si la IA está activada o desactivada".
  El endpoint ya existe y reporta estado del AI provider; añadir un campo es lo más
  coherente con la arquitectura existente.
- **Alternatives considered**:
  - *Endpoint nuevo `/api/health/ai-toggle`*: más endpoints que mantener; YAGNI.

## D-05 — Sin cambios en el frontend

- **Decision**: el frontend recibe la descripción del API y la muestra. Cuando la IA
  está desactivada, la descripción es un texto de respaldo determinístico; el frontend
  no distingue entre "descripción de IA" y "descripción de respaldo".
- **Rationale**: US3 dice "el frontend muestra la combinación completa, el nivel, los
  extras y la descripción de respaldo sin errores visibles." El frontend ya cumple esto
  porque la descripción de respaldo tiene la misma forma que la generada por IA.
- **Alternatives considered**:
  - *Badge "modo degradado" en el frontend*: no lo pide la spec; YAGNI.

## D-06 — Scope del toggle: solo generación de descripciones

- **Decision**: el toggle afecta las dos llamadas a IA en `AIProjectAdvisor`:
  `choose_valid_project` (selecciona el mejor candidato) y `generate_description`
  (escribe la descripción). Ambas se redirigen al stub.
- **Rationale**: estas son las únicas llamadas que consumen cuota del LLM.
  Los endpoints de lectura, catálogo y salud no tocan la IA (FR-007).
- **Alternatives considered**:
  - *Toggle solo para descripciones*: dejaría que `choose_valid_project` consumiera
    cuota; no cumple la intención de "proteger la cuota gratuita".
