# Contracts: HU-21 Desactivar generación por IA mediante variable de entorno

**Branch**: `021-ai-generation-toggle` | **Base**: `/api/v1`

## Endpoint modificado (ampliado)

### `GET /health/diagnostics`

El campo `ai` del response ahora incluye `ai_generation_enabled`.

**Respuesta con IA habilitada** (default):

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "ai": {
    "configured_provider": "auto",
    "resolved_provider": "groq",
    "model": "openai/gpt-oss-20b",
    "api_key_present": true,
    "api_key_length": 56,
    "degraded": false,
    "ai_generation_enabled": true
  },
  "database": { "using_platform_url": false },
  "security": { "rate_limit_enabled": true, "rate_limit_requests": 20, "cors_origins": [...] }
}
```

**Respuesta con IA desactivada** (`AI_GENERATION_ENABLED=false`):

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "ai": {
    "configured_provider": "auto",
    "resolved_provider": "groq",
    "model": "openai/gpt-oss-20b",
    "api_key_present": true,
    "api_key_length": 56,
    "degraded": false,
    "ai_generation_enabled": false
  },
  "database": { "using_platform_url": false },
  "security": { "rate_limit_enabled": true, "rate_limit_requests": 20, "cors_origins": [...] }
}
```

**Nota**: `resolved_provider` sigue reflejando el provider configurado (groq, ollama, etc.).
`ai_generation_enabled` es independiente: reporta si la generación por IA está activa
incluso cuando el provider está configurado pero el toggle la desactiva.

## Sin nuevos endpoints

No se crean endpoints nuevos. El toggle es transparente para el cliente:
- `POST /generate_project_*` sigue devolviendo `201` con la misma forma.
- La descripción puede ser generada por IA o de respaldo; el frontend no distingue.

## Contrato de comportamiento (no HTTP)

| Escenario | Comportamiento |
|---|---|
| `AI_GENERATION_ENABLED` no definida | IA activa (default) |
| `AI_GENERATION_ENABLED=true` | IA activa |
| `AI_GENERATION_ENABLED=1` | IA activa |
| `AI_GENERATION_ENABLED=on` | IA activa |
| `AI_GENERATION_ENABLED=false` | IA desactivada → stub |
| `AI_GENERATION_ENABLED=0` | IA desactivada → stub |
| `AI_GENERATION_ENABLED=no` | IA desactivada → stub |
| `AI_GENERATION_ENABLED=cualquierotro` | IA desactivada → stub (fail-closed) |
