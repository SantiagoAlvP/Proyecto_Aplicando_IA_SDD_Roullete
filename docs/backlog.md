# Backlog priorizado — Project Jackpot

**Producto:** generador de ideas de proyectos de software asistido por IA ("máquina tragamonedas de proyectos").
**Metodología:** Spec-Driven Development con GitHub Spec Kit.
**Equipo:** 6 integrantes.
**Última actualización:** 2026-08-21

---

## Cómo leer este backlog

- **Prioridad (MoSCoW):** `M` Must have · `S` Should have · `C` Could have · `W` Won't have (esta iteración).
- **Estimación:** puntos de historia (Fibonacci). 1 punto ≈ 1 hora de trabajo asistido por SDD.
- **Spec:** carpeta de Spec Kit donde vive la especificación formal de la historia.
- **Estado:** `Hecho` = implementado, probado y desplegado en la línea base.

---

## Resumen

| # | Historia de Usuario | Prioridad | Pts | Spec | Estado |
|---|---|---|---|---|---|
| HU-01 | Generar una idea de proyecto totalmente aleatoria | M | 5 | `001-generador-de-proyectos` | Hecho |
| HU-02 | Generar una idea de proyecto por nivel de dificultad | M | 3 | `001-generador-de-proyectos` | Hecho |
| HU-03 | Generar una idea de proyecto eligiendo la tecnología | M | 5 | `001-generador-de-proyectos` | Hecho |
| HU-04 | Consultar el catálogo de lenguajes, tecnologías y addons | M | 3 | `001-generador-de-proyectos` | Hecho |
| HU-05 | Obtener una descripción del proyecto redactada por IA | M | 8 | `001-generador-de-proyectos` | Hecho |
| HU-06 | Persistir cada proyecto generado en la base de datos | M | 5 | `001-generador-de-proyectos` | Hecho |
| HU-07 | Usar la aplicación desde una interfaz web tipo tragamonedas | M | 8 | `002-interfaz-tragamonedas` | Hecho |
| HU-08 | Consultar el historial de proyectos generados | S | 5 | `002-interfaz-tragamonedas` | Hecho |
| HU-09 | Proteger la API contra abuso y ataques comunes | M | 8 | `003-endurecimiento-seguridad` | Hecho |
| HU-10 | Desplegar la aplicación en la nube con verificación de salud | M | 5 | `004-despliegue-continuo` | Hecho |
| | **Total línea base** | | **55** | | |

**Historias en vivo (asignadas por el profesor en la demostración):** HU-11 y HU-12.
Ver `docs/live-demo-runbook.md` para el procedimiento de ejecución en vivo.

---

## HU-01 — Generar una idea de proyecto totalmente aleatoria

> **Como** desarrollador que busca un proyecto para practicar,
> **quiero** obtener una idea de proyecto completamente aleatoria con un clic,
> **para** empezar a construir algo sin perder tiempo decidiendo qué hacer.

**Prioridad:** M · **Puntos:** 5 · **Spec:** `specs/001-generador-de-proyectos/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Dado** que el catálogo tiene al menos un lenguaje, una tecnología y un addon,
   **cuando** envío `POST /api/v1/ensemble_project/generate_project_totally_random`,
   **entonces** recibo `201` con un proyecto que contiene lenguaje, tecnología, addon, nivel (1-5), extras y descripción.
2. **Dado** que el catálogo está vacío,
   **cuando** solicito un proyecto aleatorio,
   **entonces** recibo un error `422` con un mensaje claro y **no** se crea ningún registro.
3. **Dado** que solicito dos proyectos seguidos,
   **cuando** comparo los resultados,
   **entonces** las combinaciones son independientes entre sí (aleatoriedad real, no cacheada).

**Definición de terminado:** tests de contrato, camino feliz y catálogo vacío en verde; endpoint documentado en OpenAPI.

---

## HU-02 — Generar una idea de proyecto por nivel de dificultad

> **Como** desarrollador que conoce su propio nivel,
> **quiero** pedir un proyecto de dificultad 1 a 5,
> **para** que el reto sea proporcional a mi experiencia y no me frustre ni me aburra.

**Prioridad:** M · **Puntos:** 3 · **Spec:** `specs/001-generador-de-proyectos/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Dado** un nivel válido entre 1 y 5,
   **cuando** envío `POST /api/v1/ensemble_project/generate_project_by_level` con `{"level": 3}`,
   **entonces** recibo `201` y el proyecto devuelto tiene exactamente ese nivel.
2. **Dado** un nivel fuera de rango (0, 6, negativo o texto),
   **cuando** envío la solicitud,
   **entonces** recibo `422` sin invocar al modelo de IA (no se gasta cuota).
3. **Dado** un nivel N,
   **cuando** se genera el proyecto,
   **entonces** el número de restricciones extra es `N * 2`, de modo que a mayor nivel, mayor complejidad.

---

## HU-03 — Generar una idea de proyecto eligiendo la tecnología

> **Como** desarrollador que quiere practicar una tecnología concreta,
> **quiero** fijar el lenguaje, la tecnología o el addon y dejar que el resto sea aleatorio,
> **para** dirigir mi aprendizaje hacia lo que necesito sin renunciar a la sorpresa.

**Prioridad:** M · **Puntos:** 5 · **Spec:** `specs/001-generador-de-proyectos/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Dado** que fijo `programming_language = "Rust"` y dejo el resto vacío,
   **cuando** envío `POST /api/v1/ensemble_project/generate_project_by_value`,
   **entonces** el proyecto devuelto usa Rust y completa los campos vacíos con valores aleatorios del catálogo.
2. **Dado** que envío un valor que no existe en el catálogo,
   **cuando** se genera el proyecto,
   **entonces** el valor se registra en el catálogo y queda disponible para futuras generaciones.
3. **Dado** que la combinación solicitada es técnicamente inviable,
   **cuando** la IA la evalúa,
   **entonces** recibo `422` con la razón explicada en lenguaje natural y **no** se persiste el proyecto.

---

## HU-04 — Consultar el catálogo de lenguajes, tecnologías y addons

> **Como** usuario de la interfaz,
> **quiero** ver la lista de opciones disponibles para cada rodillo,
> **para** poder elegir conscientemente en lugar de adivinar qué valores acepta el sistema.

**Prioridad:** M · **Puntos:** 3 · **Spec:** `specs/001-generador-de-proyectos/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Cuando** consulto `GET /api/v1/catalog/programming-languages`, `/technologies` o `/addons`,
   **entonces** recibo `200` con la lista completa de entradas, cada una con `id` y `name`.
2. **Cuando** consulto la variante `/random` de cualquiera de las tres,
   **entonces** recibo `200` con una única entrada elegida al azar.
3. **Dado** que una tabla del catálogo está vacía,
   **cuando** pido un valor aleatorio,
   **entonces** la respuesta es `null` en lugar de un error `500`.

---

## HU-05 — Obtener una descripción del proyecto redactada por IA

> **Como** desarrollador,
> **quiero** que la idea venga acompañada de una descripción que explique qué voy a construir y qué voy a aprender,
> **para** entender el valor del proyecto sin tener que interpretar una lista de tecnologías sueltas.

**Prioridad:** M · **Puntos:** 8 · **Spec:** `specs/001-generador-de-proyectos/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Dado** un proyecto generado,
   **cuando** se solicita su descripción,
   **entonces** recibo texto plano de 2 a 4 frases, de menos de 400 caracteres, sin markdown ni listas.
2. **Dado** que se generan varias combinaciones candidatas,
   **cuando** la IA las evalúa,
   **entonces** descarta las técnicamente imposibles y selecciona la más coherente para el nivel indicado.
3. **Dado** que el proveedor de IA no está disponible o agotó su cuota,
   **cuando** se solicita una descripción,
   **entonces** el sistema responde igualmente con una descripción determinística de respaldo y registra el incidente en el log
   *(modo degradado: la aplicación nunca se cae por culpa del LLM).*
4. **Dado** que cambio el proveedor de IA por configuración (`AI_PROVIDER`),
   **cuando** reinicio la aplicación,
   **entonces** funciona sin modificar una sola línea de los servicios ni de los routers.

---

## HU-06 — Persistir cada proyecto generado en la base de datos

> **Como** dueño del producto,
> **quiero** que cada idea generada quede almacenada con sus relaciones,
> **para** poder analizar qué combinaciones se piden más y construir funcionalidades sobre ese histórico.

**Prioridad:** M · **Puntos:** 5 · **Spec:** `specs/001-generador-de-proyectos/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Dado** un proyecto generado con éxito,
   **cuando** termina la petición,
   **entonces** existe una fila en `projects` con claves foráneas válidas a `project_programming_languages`, `project_techs` y `project_addons`.
2. **Dado** un proyecto con N extras,
   **cuando** se persiste,
   **entonces** existen N filas en `project_extras` asociadas a ese proyecto.
3. **Dado** un valor de catálogo repetido,
   **cuando** se guarda otro proyecto que lo usa,
   **entonces** se reutiliza la fila existente y **no** se duplica (restricción `unique` sobre `name`).
4. **Dado** un cambio en el esquema,
   **cuando** se despliega,
   **entonces** existe una migración de Alembic que lo aplica automáticamente.

---

## HU-07 — Usar la aplicación desde una interfaz web tipo tragamonedas

> **Como** visitante que llega por primera vez,
> **quiero** una interfaz visual con rodillos que giran,
> **para** entender y usar el producto sin tocar Swagger ni saber qué es un `POST`.

**Prioridad:** M · **Puntos:** 8 · **Spec:** `specs/002-interfaz-tragamonedas/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Dado** que abro la raíz del sitio,
   **cuando** carga la página,
   **entonces** veo tres rodillos (lenguaje, tecnología, addon), un selector de nivel y un botón de girar.
2. **Cuando** presiono girar,
   **entonces** los rodillos se animan, se llama al backend, y al terminar se muestran el resultado y su descripción.
3. **Dado** que el backend tarda o falla,
   **cuando** presiono girar,
   **entonces** veo un estado de carga y, si falla, un mensaje de error comprensible — nunca una pantalla en blanco.
4. **Dado** que fijo manualmente uno o más rodillos,
   **cuando** giro,
   **entonces** esos valores se respetan y solo los libres cambian.
5. **Dado** que uso un teléfono,
   **cuando** abro la aplicación,
   **entonces** la interfaz es usable en pantallas de 360 px de ancho.

---

## HU-08 — Consultar el historial de proyectos generados

> **Como** desarrollador que ya usó la aplicación,
> **quiero** ver las últimas ideas generadas,
> **para** recuperar una que me gustó y no perderla al recargar la página.

**Prioridad:** S · **Puntos:** 5 · **Spec:** `specs/002-interfaz-tragamonedas/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Cuando** consulto `GET /api/v1/ensemble_project/history?limit=10`,
   **entonces** recibo `200` con los últimos 10 proyectos, del más reciente al más antiguo.
2. **Dado** un `limit` mayor que el máximo permitido (50),
   **cuando** hago la petición,
   **entonces** recibo `422` en lugar de una consulta sin cota que pueda tumbar la base de datos.
3. **Dado** que no hay proyectos,
   **cuando** consulto el historial,
   **entonces** recibo `200` con una lista vacía, no un `404`.
4. **Cuando** abro la interfaz,
   **entonces** el historial se muestra en un panel lateral y se actualiza tras cada giro.

---

## HU-09 — Proteger la API contra abuso y ataques comunes

> **Como** responsable del servicio,
> **quiero** que la API resista peticiones abusivas y no filtre información sensible,
> **para** que la cuota gratuita de IA no se agote en minutos y no expongamos datos internos.

**Prioridad:** M · **Puntos:** 8 · **Spec:** `specs/003-endurecimiento-seguridad/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Dado** que supero el límite de peticiones por minuto en un endpoint de generación,
   **cuando** envío una más,
   **entonces** recibo `429` con la cabecera `Retry-After`.
2. **Cuando** recibo cualquier respuesta,
   **entonces** incluye `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy` y `Content-Security-Policy`.
3. **Dado** un origen no autorizado,
   **cuando** hace una petición desde el navegador,
   **entonces** CORS la bloquea (la lista blanca es explícita, nunca `*`).
4. **Dado** que ocurre un error interno,
   **cuando** se devuelve la respuesta,
   **entonces** el cliente recibe un mensaje genérico con un `request_id`, y el detalle técnico solo aparece en el log del servidor.
5. **Dado** el repositorio completo,
   **cuando** CI ejecuta el escaneo de secretos y la auditoría de dependencias,
   **entonces** no hay secretos versionados ni vulnerabilidades de severidad alta.
6. **Dado** un payload desproporcionado (miles de extras o cadenas enormes),
   **cuando** se envía,
   **entonces** se rechaza con `422` antes de llegar al modelo de IA.

---

## HU-10 — Desplegar la aplicación en la nube con verificación de salud

> **Como** equipo,
> **quiero** que cada merge a `main` publique automáticamente la versión actualizada,
> **para** poder mostrar en la demostración la funcionalidad recién construida, ya desplegada y funcionando.

**Prioridad:** M · **Puntos:** 5 · **Spec:** `specs/004-despliegue-continuo/` · **Estado:** Hecho

**Criterios de aceptación**

1. **Dado** un push a `main`,
   **cuando** CI termina en verde,
   **entonces** Railway construye la imagen y publica la nueva versión sin intervención manual.
2. **Cuando** consulto `GET /api/health` en la URL pública,
   **entonces** recibo `200 {"status": "healthy"}`.
3. **Dado** el arranque de la aplicación,
   **cuando** el contenedor inicia,
   **entonces** las migraciones de Alembic se aplican y el catálogo se siembra automáticamente.
4. **Dado** que CI falla (test rojo, lint sucio o vulnerabilidad alta),
   **cuando** termina el pipeline,
   **entonces** el despliegue **no** ocurre.
5. **Cuando** abro la URL pública en el navegador,
   **entonces** se sirve el frontend compilado desde el mismo dominio que la API (sin CORS cruzado).

---

## Historias en vivo (a definir por el profesor)

### HU-11 — *(asignada en la demostración)*
### HU-12 — *(asignada en la demostración)*

Procedimiento: `docs/live-demo-runbook.md`.
Cada integrante ejecuta el motor SDD en su máquina sobre un ticket independiente de la spec generada en vivo.

---

## Fuera de alcance en esta iteración (Won't have)

| Idea | Razón |
|---|---|
| Cuentas de usuario y autenticación | No aporta valor a la demostración y multiplica la superficie de ataque. Se agregaría en la iteración 2. |
| Rodillos ilimitados configurables por el usuario | La combinatoria ya se cubre con los extras derivados del nivel. YAGNI. |
| Exportar el proyecto como repositorio inicial en GitHub | Depende de OAuth de GitHub; excede el tiempo disponible. |
| Traducción multi-idioma de las descripciones | Duplica el consumo de tokens del LLM sin aportar a los objetivos de la entrega. |
