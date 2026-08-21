# Despliegue en Railway

**Spec de referencia:** `specs/004-despliegue-continuo/`
**Tiempo estimado la primera vez:** 15 minutos.
**Costo:** USD 0.00.

---

## 0. Antes de empezar

Necesitas dos cuentas gratuitas. Créalas ahora, tardan un minuto cada una:

| Cuenta | Para qué | Dónde |
|---|---|---|
| **Groq** | API key del modelo de lenguaje (capa gratuita) | https://console.groq.com |
| **Railway** | Hosting del backend + PostgreSQL | https://railway.com (entra con GitHub) |

> Si no configuras Groq, la aplicación **igual funciona**: arranca en modo
> degradado con descripciones generadas por plantilla y lo advierte en el log.
> Es preferible desplegar sin IA que no desplegar.

---

## 1. Obtener la API key de Groq

1. Entra a https://console.groq.com y regístrate.
2. Ve a **API Keys** → **Create API Key**.
3. Cópiala. Empieza por `gsk_...`.
4. **No la pegues en ningún archivo del repositorio.** Va únicamente en las
   variables de entorno de Railway. `gitleaks` bloqueará el commit si lo intentas.

Límites de la capa gratuita: 30 peticiones/minuto, 1 000 peticiones/día.
Cada generación consume 2 llamadas, así que el techo es ~500 generaciones diarias.

---

## 2. Crear el proyecto en Railway

1. Entra a https://railway.com y **Login with GitHub**.
2. **New Project** → **Deploy from GitHub repo**.
3. Autoriza el acceso y elige `Proyecto_Aplicando_IA_SDD_Roullete`.
4. Railway detecta el `Dockerfile` y `railway.json`, y empieza a construir.
   El primer build tarda unos 3-5 minutos (compila el frontend y sincroniza Python).

---

## 3. Añadir PostgreSQL

1. Dentro del proyecto: **+ New** → **Database** → **Add PostgreSQL**.
2. Railway crea la base de datos y expone la variable `DATABASE_URL`.
3. Ve al servicio de la aplicación → **Variables** → **Add Variable Reference**
   → selecciona `DATABASE_URL` de Postgres.

> La aplicación acepta `DATABASE_URL` completa **o** los componentes por separado,
> y normaliza el esquema `postgres://` heredado. No hay nada que ajustar a mano.

---

## 4. Configurar las variables de entorno

En el servicio de la aplicación → **Variables**, añade:

```
ENVIRONMENT=production
AI_PROVIDER=groq
GROQ_API_KEY=gsk_tu_clave_aqui
GROQ_MODEL=openai/gpt-oss-20b
CORS_ALLOWED_ORIGINS=https://TU-DOMINIO.up.railway.app
RATE_LIMIT_REQUESTS=20
RATE_LIMIT_WINDOW_SECONDS=60
LOG_LEVEL=INFO
```

**No definas `PORT`**: Railway la inyecta y `entrypoint.sh` la lee.

> `CORS_ALLOWED_ORIGINS` no admite `*` en producción: la aplicación **se niega a
> arrancar** si lo detecta. Es intencional (ver `docs/security.md`). Pon el dominio
> exacto que Railway te asigne en el paso 5.

---

## 5. Generar el dominio público

1. Servicio de la aplicación → **Settings** → **Networking** → **Generate Domain**.
2. Railway devuelve algo como `project-jackpot-production-a1b2.up.railway.app`.
3. Copia ese dominio y **actualiza `CORS_ALLOWED_ORIGINS`** con él (paso 4).
   Railway redesplegará solo.

---

## 6. Verificar el despliegue

```bash
DOMINIO=https://TU-DOMINIO.up.railway.app

# 1. Salud (debe responder 200)
curl -i $DOMINIO/api/health

# 2. Cabeceras de seguridad (debe aparecer strict-transport-security)
curl -sI $DOMINIO/api/health | grep -i -E "strict-transport|x-frame|content-security"

# 3. Catálogo sembrado
curl -s $DOMINIO/api/v1/catalog/programming-languages | head -c 200

# 4. Generación real contra Groq
curl -s -X POST $DOMINIO/api/v1/ensemble_project/generate_project_totally_random \
     -H "Content-Type: application/json"

# 5. Frontend en la raíz y documentación en el mismo dominio
open $DOMINIO
open $DOMINIO/api/docs
```

Si el paso 4 devuelve una descripción con estilo de plantilla siempre igual,
la aplicación está en modo degradado: revisa que `GROQ_API_KEY` esté bien puesta
y busca en los logs la línea `ai_provider=`.

---

## 7. Despliegue continuo

Ya está activo: Railway observa la rama `main` y redespliega en cada push.

Para que **solo llegue código verificado**, protege la rama en GitHub:

1. Repositorio → **Settings** → **Branches** → **Add branch protection rule**.
2. Patrón: `main`.
3. Marca **Require status checks to pass before merging** y selecciona los jobs
   `backend`, `security`, `frontend` y `docker`.

Con eso, un test rojo, un lint sucio, un secreto detectado o una dependencia
vulnerable impiden el merge y, por tanto, el despliegue (spec 004, FR-002).

---

## 8. Resolución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| El build falla en `npm ci` | Falta `frontend/package-lock.json` | Haz commit del lock file |
| `MIGRATION FAILED` en el log | `DATABASE_URL` mal referenciada | Revisa la referencia de variable al servicio de Postgres |
| La app no arranca y el log menciona `CORS_ALLOWED_ORIGINS` | Pusiste `*` en producción | Pon el dominio exacto |
| Todo responde 200 pero las descripciones son siempre iguales | Modo degradado | `GROQ_API_KEY` ausente o inválida, **o `GROQ_MODEL` apunta a un modelo retirado** |
| El log dice `AI description failed` | Groq rechaza la petición | Groq retira modelos con frecuencia. Verifica el id en https://console.groq.com/docs/models y actualiza `GROQ_MODEL` |
| `429` constantes durante la demostración | Límite de tasa demasiado bajo para varios espectadores | Sube `RATE_LIMIT_REQUESTS` a 60 y redespliega |
| La verificación de salud falla tras el deploy | Arranque en frío de Postgres | Railway reintenta; `healthcheckTimeout` está en 120 s |

---

## 9. Alternativa gratuita si Railway agota el crédito

El artefacto es un contenedor estándar, así que cualquier plataforma que corra
Docker sirve. Opciones probadas por el equipo:

| Plataforma | Base de datos | Advertencia |
|---|---|---|
| Render | Neon (PostgreSQL serverless) | El servicio gratuito duerme tras 15 min de inactividad: el primer acceso tarda ~30 s |
| Fly.io | Fly Postgres | Requiere tarjeta para verificar, aunque no cobre |
| Koyeb | Neon | Menos generoso en RAM |

En todos los casos las variables de entorno son exactamente las mismas: es lo que
significa el Principio VI de la constitución.
