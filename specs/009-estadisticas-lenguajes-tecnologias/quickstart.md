# Quickstart: validación de la funcionalidad de estadísticas

## Prerrequisitos

- El backend del proyecto levantado con Docker Compose o el entorno local del repositorio.
- Base de datos disponible con datos de proyectos generados.
- Frontend disponible para comprobar la vista de estadísticas.

## Validación del backend

1. Inicia la aplicación con el flujo habitual del repositorio.
2. Genera varios proyectos para crear historial con combinaciones repetidas.
3. Ejecuta la petición:

```bash
curl "http://localhost:9600/api/v1/ensemble_project/statistics?limit=10"
```

4. Comprueba que la respuesta devuelve un conjunto ordenado por frecuencia con categorías y recuentos.
5. Repite la operación con un historial vacío y confirma que la respuesta es consistente y no rompe el flujo.

## Validación del frontend

1. Abre la interfaz de la aplicación.
2. Revisa la vista de estadísticas o el panel correspondiente.
3. Confirma que aparecen los lenguajes y tecnologías con el orden esperado.
4. Comprueba que la vista refleja los cambios cuando se genera nuevo contenido.

## Verificación de regresión

```bash
uv run pytest -q
cd frontend && npm run build
```

La validación debe garantizar que la nueva vista no rompe la generación ni la navegación actual.
