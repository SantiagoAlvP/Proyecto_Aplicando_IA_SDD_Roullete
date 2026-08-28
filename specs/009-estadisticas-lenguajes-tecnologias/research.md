# Research: Estadísticas de lenguajes y tecnologías más propuestas

## Decision

Se reutiliza el historial de proyectos ya generado como fuente de verdad para calcular las estadísticas. El backend agregará una consulta de resumen sobre las tablas existentes (`projects`, `project_programming_languages`, `project_techs`, `project_addons`) y devolverá los conteos normalizados por categoría.

## Rationale

- El sistema ya persiste cada propuesta con los campos de lenguaje, tecnología y addon; no hace falta introducir una segunda fuente de datos.
- La vista de historial y favoritos ya está construida sobre los mismos modelos, así que la estadística queda alineada con el comportamiento real del sistema.
- El cálculo se hace en lectura, sin afectar la generación ni la experiencia del usuario en el giro de rodillos.

## Alternatives considered

### 1. Nueva tabla de estadísticas

Se descartó porque introduce duplicación de estado: el historial de proyectos ya representa la realidad de las propuestas, y una tabla paralela requeriría mantenimiento manual de contadores con riesgo de inconsistencia.

### 2. Calcular en frontend únicamente

Se descartó porque el navegador no debe cargar ni procesar todo el historial de forma excesiva y porque la misma lógica debe estar centralizada en la capa de negocio para poder reutilizarse.

### 3. Contar solo el historial reciente

Se descartó porque la especificación exige entender qué está proponiendo el sistema en general, no solo lo generado en la última ventana.

## Implications

- La API de estadísticas debe ser de solo lectura, sin mutar el historial ni los proyectos.
- El agregado debe distinguir entre categorías (`programming_language`, `technology`, `addon`) y mostrar un ranking ordenado por frecuencia.
- La respuesta debe incluir un total de registros analizados y un porcentaje para comparar la frecuencia relativa de cada valor.
