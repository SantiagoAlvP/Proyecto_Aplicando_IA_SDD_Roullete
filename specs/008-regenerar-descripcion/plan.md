# Implementation Plan: Regenerar la descripción de un proyecto existente

**Branch**: `008-regenerar-descripcion` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

## Summary

Se añadirá una operación HTTP que cargue un proyecto persistido por su identificador,
reconstruya su combinación actual y solicite al gateway de IA una descripción alternativa.
La operación actualizará únicamente la columna de descripción del proyecto existente y
devolverá la combinación completa, incluido el nivel y sus extras.

La base actual no persiste el nivel en `projects` y la respuesta de generación no incluye el
identificador. Se corregirá la persistencia del nivel mediante migración y se incorporará un
DTO específico para la regeneración, sin cambiar el contrato de las rutas de generación
existentes.

## Technical Context

**Language/Version**: Python >= 3.12
**Primary Dependencies**: FastAPI, SQLModel, Pydantic, Alembic, Pytest
**Storage**: PostgreSQL mediante el modelo y repositorio SQLModel existentes
**AI Integration**: `ProjectAIAdvisor.generate_description(project)` mediante el gateway ya inyectado
**Testing**: Pytest con repositorio y advisor simulados; migración verificada con la suite existente
**API**: `POST /api/v1/ensemble_project/{project_id}/regenerate_description`, sin cuerpo
**Constraints**: solo se actualiza `description`; no se crean proyectos ni relaciones; `project_id` positivo

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. SDD | Esta spec, el plan y las tareas preceden a la implementación. |
| II. Capas | La ruta traduce HTTP; servicio aplica reglas; repositorio lee y actualiza persistencia; el advisor sigue inyectado. |
| III. Test-First | Se añaden tests de contrato, éxito, proyecto inexistente, respuesta inválida y preservación de combinación. |
| IV. Seguridad | El identificador se valida como entero positivo; no se aceptan cuerpos innecesarios; se conserva el rate limiting global para llamadas al LLM. |
| V. Free-tier | Se reutiliza el gateway configurable y el respaldo determinístico; no se añaden servicios. |
| VI. Despliegue | El cambio de esquema se entrega mediante una migración Alembic reversible. |
| VII. YAGNI | No se introduce historial de versiones, autenticación ni una abstracción paralela para descripciones. |

**Resultado**: PASS.

## Design

### Request flow

1. FastAPI valida `project_id` con una cota mínima de 1.
2. El servicio pide al repositorio el proyecto y sus relaciones, incluyendo extras.
3. Si no existe, el servicio lanza un error de dominio que la ruta traduce a `404`; el advisor no se invoca.
4. El servicio forma un contexto de solo lectura con lenguaje, tecnología, addon, nivel y extras.
5. El advisor genera el texto. Si el proveedor falla, se usa el respaldo determinístico. Si devuelve texto vacío, inválido o igual al anterior, se conserva la descripción actual.
6. El repositorio actualiza únicamente `Project.description`, confirma la transacción y devuelve el mismo proyecto reconstruido.

### Persistence compatibility

- `Project.level` será un entero entre 1 y 5 persistido en `projects`.
- La migración añadirá la columna con un valor temporal compatible, calculará el nivel de los
  registros existentes a partir de `count(project_extras) / 2` acotado al rango 1-5 cuando sea
  posible y dejará 1 como respaldo para registros legacy sin extras; después establecerá el
  valor por defecto y la restricción de no nulo.
- La generación existente deberá guardar el nivel elegido al crear un proyecto.
- Los extras se leerán desde las relaciones existentes y no se recrearán durante la regeneración.

### Description validation

El servicio validará texto plano no vacío, entre 2 y 4 frases y menor de 400 caracteres para
una respuesta normal. La comparación con la descripción anterior será exacta después de
normalizar espacios exteriores. Una respuesta inválida no se persiste. El respaldo para una
caída del proveedor debe ser estable y distinto de la descripción actual; si no puede cumplir
esa diferencia, se conserva la anterior.

### Error mapping

| Situación | Respuesta |
|---|---|
| `project_id < 1` o no entero | `422`, sin advisor |
| Proyecto inexistente | `404`, sin advisor ni escritura |
| Proveedor no disponible | `200` con respaldo persistido y evento registrado |
| Respuesta IA vacía, inválida o repetida | `200` con descripción anterior, sin escritura |

## Project Structure

```text
core/database/models.py                                  # campo level en Project
core/database/crud.py                                    # lectura y actualización de Project
core/ensemble_project/api/ensemble_project_models.py     # DTO de regeneración
core/ensemble_project/ensemble_project_repository.py     # reconstrucción y update atómico
core/ensemble_project/ensemble_project_service.py        # reglas de regeneración
core/ensemble_project/api/ensemble_project_router.py     # endpoint y errores HTTP
alembic/versions/<revision>_add_level_to_projects.py     # migración compatible
tests/test_database/test_project_crud.py                 # persistencia del nivel/update
tests/test_fastapi_endpoints/test_regenerate_description.py # contrato y escenarios
```

## Complexity Tracking

| Complejidad introducida | Por qué es necesaria | Alternativa más simple descartada |
|---|---|---|
| Columna `level` y migración de datos | La operación debe devolver y preservar el nivel de proyectos ya guardados | Inferirlo siempre desde extras, lo que no es fiable para registros legacy incompletos |
| DTO específico de regeneración | El contrato necesita `id` y extras sin alterar respuestas existentes | Cambiar `ProjectResponse`, lo que rompería clientes del endpoint de generación |
| Validación de la respuesta de IA | La spec exige diferencia, formato y conservación ante respuestas inválidas | Persistir cualquier texto y permitir descripciones vacías o repetidas |