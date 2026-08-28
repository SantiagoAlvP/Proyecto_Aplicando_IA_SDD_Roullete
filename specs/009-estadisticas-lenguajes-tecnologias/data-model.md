# Data Model: Estadísticas de lenguajes y tecnologías más propuestas

## Entities

### Project

Representa una propuesta generada y ya persistida.

- `id`: identificador único del proyecto
- `description`: texto descriptivo de la idea generada
- `is_favorite`: indicador de favorito
- `level`: nivel de complejidad de la generación
- `programming_language_id`: referencia al lenguaje principal
- `project_tech_id`: referencia a la tecnología principal
- `project_addon_id`: referencia al addon principal

### ProgrammingLanguage

- `id`: identificador único
- `name`: nombre del lenguaje, por ejemplo "Python" o "TypeScript"

### Tech

- `id`: identificador único
- `name`: nombre de la tecnología, por ejemplo "React", "FastAPI" o "PostgreSQL"

### Addon

- `id`: identificador único
- `name`: nombre del addon o componente complementario

### AggregatedStatistic

Resumen calculado para la vista de estadísticas.

- `category`: tipo de dato analizado (`programming_language`, `technology`, `addon`)
- `label`: nombre representativo del valor observado
- `count`: número de proyectos en los que aparece
- `share`: proporción del total analizado
- `rank`: posición dentro del ranking de frecuencia

## Relationships

- Cada `Project` tiene exactamente un `ProgrammingLanguage` asociado.
- Cada `Project` tiene exactamente una `Tech` asociada.
- Cada `Project` tiene exactamente un `Addon` asociado.
- La vista de estadísticas agrega esos valores sobre el conjunto completo de proyectos históricos, sin crear nuevas tablas de persistencia.

## Validation rules

- Los nombres de lenguaje/tecnología/addon deben ser no vacíos.
- La suma de conteos de un mismo tipo no debe superar la cantidad total de proyectos analizados.
- Los resultados deben ordenarse por `count` descendente y, en caso de empate, por `label` ascendente.

## State transitions

No aplica un ciclo de estado complejo: la estadística es un cálculo derivado del historial existente que se recomputará cada vez que se actualiza el conjunto de proyectos.
