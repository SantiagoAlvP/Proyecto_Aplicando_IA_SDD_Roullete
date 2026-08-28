# Data model for get-project-by-id

> Actualizado (2026-08-28) para reflejar el modelo `Project` real en
> core/database/models.py. El borrador original asumía UUID y campos
> (name, slug, tags, metadata, created_at/updated_at) que no existen hoy;
> se documentan ambos para que quede explícito qué fue implementado y qué
> quedaría pendiente si se necesita en el futuro.

Entities

- Project (implementado)
  - id: integer, autoincremental, primary key
  - description: string | null (max 500 chars)
  - is_favorite: boolean
  - level: integer | null
  - programming_language_id / project_tech_id / project_addon_id: foreign keys
  - owner_id: integer | null
  - owner_name: string | null (max 200 chars)
  - is_public: boolean (default true)

Validation rules (implementadas)

- id: debe ser un entero válido (FastAPI valida el path param automáticamente
  y responde 422 si no lo es)
- description: max 500 chars

Pendiente / no implementado (del borrador original de la spec)

- name, slug, tags, metadata, created_at, updated_at: no existen en el
  modelo actual. Si un consumidor de la API los necesita, requieren una
  migración de Alembic y actualizar el contrato antes de exponerlos.
- id tipo UUID: se descartó a favor de mantener consistencia con el resto
  del catálogo (todas las demás tablas usan enteros autoincrementales).
