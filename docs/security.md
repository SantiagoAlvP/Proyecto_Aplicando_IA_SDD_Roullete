# Seguridad y gestión de riesgo

**Proyecto:** Project Jackpot
**Spec de referencia:** `specs/003-endurecimiento-seguridad/`
**Última revisión:** 2026-08-21

Este documento explica qué protege la aplicación, cómo se verifica automáticamente
y —igual de importante— **qué no protege todavía**. Un documento de seguridad que
solo enumera logros es propaganda; este declara también sus límites.

---

## 1. Modelo de amenaza

La aplicación es pública, sin autenticación, y consume un modelo de lenguaje con
cuota gratuita limitada. De ahí salen los tres riesgos que realmente importan:

| # | Riesgo | Impacto si se materializa | Probabilidad |
|---|---|---|---|
| R1 | Agotamiento de la cuota de IA por peticiones automatizadas | La aplicación deja de generar descripciones **para todos**, incluida la demostración | Alta |
| R2 | Fuga de información interna en mensajes de error | Un atacante obtiene el mapa del sistema (rutas, tablas, versiones) gratis | Media |
| R3 | Secreto versionado por error humano | Clave comprometida; rotarla y limpiar el historial de Git | Media |
| R4 | Inyección SQL | Lectura o destrucción de la base de datos | Baja (ORM en todo el acceso) |
| R5 | XSS / clickjacking sobre el frontend | Robo de sesión — hoy sin sesiones, pero el riesgo aparece al añadir cuentas | Baja |
| R6 | Agotamiento de recursos por payload desproporcionado | Degradación del servicio | Media |

**Activo más valioso:** no son los datos (el catálogo es público y las ideas
generadas no son sensibles). Es **la disponibilidad del servicio**, porque la
entrega académica depende de que la aplicación esté en línea y respondiendo.

---

## 2. Controles implementados

### 2.1 Límite de tasa (mitiga R1, R6)

`core/security/rate_limit.py` — ventana deslizante en memoria, por cliente.

- Por defecto: **20 peticiones / 60 s** por cliente (`RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW_SECONDS`).
- Identifica al cliente por el primer salto de `X-Forwarded-For` (detrás del proxy de Railway) o por IP directa.
- Devuelve `429` con `Retry-After` y cabeceras `X-RateLimit-*`.
- **Exime `/api/health`**: la plataforma lo usa como verificación de vida; limitarlo tumbaría los despliegues.
- **Exime el preflight `OPTIONS`**: no es una petición real; contarlo reduciría a la mitad el presupuesto de cada cliente de navegador.

Verificado en `tests/test_security/test_rate_limit.py` (6 tests) y probado en vivo.

### 2.2 Cabeceras de endurecimiento (mitiga R5)

`core/security/headers.py` — aplicadas a **toda** respuesta, incluidos los `429`, `413` y `500`.

| Cabecera | Valor | Qué evita |
|---|---|---|
| `X-Content-Type-Options` | `nosniff` | Que el navegador adivine el tipo MIME y ejecute lo que no debe |
| `X-Frame-Options` | `DENY` | Clickjacking |
| `Referrer-Policy` | `no-referrer` | Fuga de URLs internas a terceros |
| `Content-Security-Policy` | `default-src 'self'`, sin `unsafe-eval` | Ejecución de scripts externos o inyectados |
| `Permissions-Policy` | cámara, micrófono y geolocalización denegados | Acceso a capacidades del dispositivo |
| `Strict-Transport-Security` | `max-age=31536000` **solo en producción** | Degradación a HTTP |

HSTS se emite únicamente en producción a propósito: enviarlo sobre HTTP en
desarrollo dejaría a los integrantes bloqueados en `localhost`.

### 2.3 Errores sin fuga (mitiga R2)

`core/security/errors.py`.

- Toda petición recibe un `request_id` (cabecera `X-Request-ID`).
- Una excepción no controlada devuelve `500` con un mensaje neutro **más** el `request_id`. El stack trace va solo al log del servidor, bajo el mismo identificador.
- Los errores de validación indican el campo inválido sin revelar la estructura interna del modelo.
- El cuerpo de las peticiones **nunca** se registra: es entrada de usuario y puede contener cualquier cosa.

Verificado en `tests/test_security/test_errors.py`, incluyendo un test que
comprueba explícitamente que la respuesta **no** contiene `Traceback`, nombres de
tabla ni rutas del sistema de archivos.

### 2.4 Validación estricta de entrada (mitiga R6)

- Nombres de catálogo: máximo 100 caracteres.
- Lista de extras: máximo 20 elementos.
- Nivel: entero entre 1 y 5.
- `limit` del historial: entre 1 y 50 — **nunca** un `SELECT` sin cota.
- Cuerpo de la petición: máximo 64 KiB, rechazado con `413` antes de deserializarlo.

Todo se rechaza con `422` **antes** de que el servicio se ejecute y, por tanto,
antes de gastar un solo token del modelo. Es el control más barato y más fiable del sistema.

### 2.5 CORS con lista blanca explícita (mitiga R5)

`CORS_ALLOWED_ORIGINS` es una lista separada por comas. Si en producción contiene
`*`, **la aplicación se niega a arrancar**. Preferimos una caída ruidosa en el
despliegue a una API abierta al mundo que nadie note.

### 2.6 Gestión de secretos (mitiga R3)

- Ningún secreto tiene valor por defecto en el código.
- `.env` está en `.gitignore`; `.env.example` documenta el contrato sin valores reales.
- `gitleaks` corre como hook de pre-commit **y** en CI: una clave se detiene antes de llegar al remoto, donde eliminarla ya no basta y hay que rotar la credencial.

### 2.7 Acceso a datos (mitiga R4)

Todo el acceso pasa por SQLModel/SQLAlchemy con consultas parametrizadas. No existe
una sola concatenación de strings para construir SQL en el repositorio. El único
uso de `psycopg2` en crudo (`CREATE DATABASE` local) emplea `sql.Identifier`,
que escapa el identificador correctamente.

### 2.8 Contenedor

- Corre como usuario sin privilegios (`appuser`, uid 1001), no como root.
- Imagen mínima: Node existe solo en la etapa de compilación y no llega al runtime.
- `.dockerignore` excluye `.git`, `.env`, tests y documentación del contexto de build.

---

## 3. Verificación automática

| Control | Dónde se verifica |
|---|---|
| Límite de tasa | `tests/test_security/test_rate_limit.py` |
| Cabeceras | `tests/test_security/test_headers.py` |
| No fuga en errores | `tests/test_security/test_errors.py` |
| Validación de entrada | `tests/test_security/test_input_validation.py` |
| CORS sin comodín en producción | `tests/test_security/test_cors_policy.py` |
| Secretos versionados | `gitleaks` (pre-commit + CI) |
| Dependencias vulnerables | `pip-audit --strict` (CI) |
| Degradación segura sin proveedor de IA | `tests/test_ai_gateway/test_factory.py` |

**Suite completa: 204 tests, todos en verde.** CI bloquea el despliegue ante
cualquier fallo (`.github/workflows/ci.yml`).

---

## 4. Cobertura frente a OWASP Top 10

| Categoría | Estado | Detalle |
|---|---|---|
| A01 Control de acceso roto | **No aplica** | No hay recursos por usuario; todos los endpoints son públicos por diseño |
| A02 Fallos criptográficos | **Cubierto** | TLS terminado por Railway; HSTS en producción; sin datos sensibles almacenados |
| A03 Inyección | **Cubierto** | ORM con consultas parametrizadas; validación estricta de entrada |
| A04 Diseño inseguro | **Cubierto** | Modelo de amenaza explícito; límite de tasa y modo degradado diseñados desde la spec |
| A05 Configuración incorrecta | **Cubierto** | Sin secretos por defecto; CORS con lista blanca; contenedor sin root; `/api/docs` visible a propósito (API pública) |
| A06 Componentes vulnerables | **Cubierto** | `pip-audit` en CI; dependencias fijadas en `uv.lock` y `package-lock.json` |
| A07 Fallos de identificación | **No aplica** | Sin autenticación en esta iteración |
| A08 Integridad de software y datos | **Parcial** | Dependencias fijadas por lock; **falta** firmar las imágenes de contenedor |
| A09 Fallos de registro y monitoreo | **Parcial** | Log estructurado con `request_id` por petición; **falta** alertado automático |
| A10 SSRF | **No aplica** | La aplicación no obtiene URLs suministradas por el usuario |

---

## 5. Limitaciones conocidas

Se declaran en lugar de disimularse.

1. **El límite de tasa vive en memoria del proceso.** Con varias réplicas, el
   límite efectivo se multiplica por el número de réplicas, y un reinicio lo
   reinicia a cero. Es una defensa de mejor esfuerzo adecuada a una réplica en
   capa gratuita. *Mitigación futura: Redis compartido.*

2. **No hay autenticación.** Cualquiera puede generar proyectos. Es intencional
   para esta iteración: añadir cuentas multiplicaría la superficie de ataque sin
   aportar a los objetivos de la entrega. *Está en el backlog como "Won't have".*

3. **`X-Forwarded-For` es falsificable** si la aplicación se expusiera sin proxy.
   Detrás de Railway, la plataforma reescribe la cabecera. Fuera de ese entorno,
   el límite de tasa se puede eludir cambiando la cabecera.

4. **El escaneo de secretos no reescribe el historial.** `gitleaks` detecta, pero
   si un secreto llegó al remoto, el procedimiento correcto sigue siendo **rotar
   la credencial**, no solo borrar el commit.

5. **Sin alertado.** Los logs quedan en la plataforma; nadie recibe una
   notificación automática ante un pico de `429` o de `500`.

6. **Sin firma de imágenes ni SBOM.** La cadena de suministro del contenedor no
   está verificada criptográficamente.

---

## 6. Procedimiento ante un incidente

1. Obtener el `request_id` que vio el usuario.
2. Buscarlo en los logs de Railway: `request_id=<id>` aparece en la línea de la petición y en la traza.
3. Si es un secreto expuesto: **rotar primero la credencial** en el proveedor, después limpiar el repositorio.
4. Si es abuso: bajar `RATE_LIMIT_REQUESTS` mediante variable de entorno y redesplegar (no requiere cambio de código).
5. Registrar el incidente y, si revela un hueco, abrir una nueva spec — no un parche suelto (Constitución, Principio I).
