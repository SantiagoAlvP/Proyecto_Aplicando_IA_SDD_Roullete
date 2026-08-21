# Caso de negocio: SDD vs. desarrollo tradicional vs. prompting suelto

**Proyecto:** Project Jackpot
**Fecha:** 2026-08-21
**Naturaleza:** caso de negocio **sintético** con fines académicos. Los precios de
proveedores son verificados y están citados; los tiempos de desarrollo son
estimaciones declaradas como tales, salvo los que se midieron en este proyecto.

---

## 1. Resumen ejecutivo

| | Tradicional | Prompting suelto | **Spec-Driven Development** |
|---|---|---|---|
| Esfuerzo de construcción (CAPEX) | 110 h | 46 h | **38 h** |
| Retrabajo por deriva de requisitos | 22 h | 30 h | **4 h** |
| **Esfuerzo total** | **132 h** | **76 h** | **42 h** |
| Costo de construcción @ USD 12/h | USD 1 584 | USD 912 | **USD 504** |
| Costo mensual de operación (OPEX) | USD 0 – 12 | USD 0 – 12 | **USD 0** |
| Cobertura de pruebas al entregar | Variable | Baja | **204 tests, suite verde** |
| Tiempo para añadir una HU nueva | 4 – 6 h | 1 – 3 h (impredecible) | **10 – 20 min por spec** |

**Conclusión:** frente al desarrollo tradicional, SDD reduce el esfuerzo estimado
un **68 %** para el mismo alcance. Frente al prompting suelto, la reducción es del
**45 %**, y la diferencia real no está en la velocidad de escribir código —ahí el
prompting también es rápido— sino en **cuánto código hay que rehacer** cuando
nadie escribió antes qué debía hacer el sistema.

---

## 2. Alcance valorado

Las 10 Historias de Usuario de `docs/backlog.md`, estimadas en 55 puntos de
historia, más los cuatro artefactos de especificación (`specs/001` a `specs/004`).

Entregable real medido en este proyecto:

| Métrica | Valor |
|---|---|
| Historias de usuario entregadas | 10 |
| Especificaciones formales (spec + plan + tasks) | 4 features, 12 documentos |
| Tests automatizados | 204 (131 heredados + 73 nuevos) |
| Endpoints de API | 11 |
| Componentes de frontend | 4 |
| Tamaño del bundle del frontend | 63 KB comprimido |
| Hallazgos de lint y de tipos | 0 |

---

## 3. CAPEX — costo de construir

### 3.1 Supuestos declarados

| Supuesto | Valor | Justificación |
|---|---|---|
| Tarifa por hora | USD 12 | Costo por hora de un desarrollador junior en el mercado colombiano, incluyendo prestaciones. **Ajustable**: todas las cifras salen de multiplicar horas por esta tarifa |
| Tamaño del equipo | 6 personas | Composición real del equipo |
| Herramienta de IA | GitHub Copilot Pro | **USD 0** para el equipo mediante el GitHub Student Developer Pack |
| Punto de historia | ≈ 1 hora asistida por IA | Calibrado contra la línea base ya construida |

### 3.2 Comparativa por fase

| Fase | Tradicional | Prompting suelto | SDD |
|---|---|---|---|
| Levantamiento de requisitos | 12 h | 2 h | 6 h *(la spec **es** el requisito)* |
| Diseño de arquitectura | 14 h | 0 h *(emerge sola)* | 5 h *(el plan lo fija)* |
| Implementación | 60 h | 32 h | 18 h |
| Pruebas | 16 h | 8 h | 6 h *(los criterios de aceptación ya son los tests)* |
| Documentación | 8 h | 4 h | 3 h *(las specs ya son la documentación)* |
| **Subtotal** | **110 h** | **46 h** | **38 h** |
| Retrabajo por deriva | 22 h (20 %) | 30 h (65 %) | 4 h (10 %) |
| **Total** | **132 h** | **76 h** | **42 h** |
| **Costo** | **USD 1 584** | **USD 912** | **USD 504** |

**De dónde sale el retrabajo del prompting suelto.** Es la cifra clave de este
análisis y merece explicación. Sin una especificación escrita, cada prompt parte
de la interpretación que el modelo hace de una frase, y esa interpretación cambia
entre sesiones. El resultado típico: dos integrantes generan implementaciones
incompatibles del mismo concepto, nadie sabe cuál es la correcta porque no hay
fuente de verdad, y la conversación que produjo el código se pierde al cerrar la
ventana. El 65 % de retrabajo no es pesimismo: es lo que cuesta reconstruir una
decisión que nunca se escribió.

**De dónde sale el ahorro de SDD.** Tres mecanismos concretos, todos verificables
en este repositorio:

1. **Los criterios de aceptación se convierten en tests casi literalmente.**
   `spec.md` de la 003 dice *"Given el límite configurado en N peticiones por
   minuto, When se envía la petición N+1, Then se devuelve 429 con Retry-After"*.
   El test `test_rejection_tells_the_client_when_to_come_back` es esa frase en
   Python. Escribir el criterio ya fue escribir la prueba.

2. **El plan detecta el problema antes de que cueste caro.** La decisión D-01 de
   `specs/001` —poner el LLM detrás de una interfaz— se tomó al planear, no al
   desplegar. Cuando la 004 descubrió que Ollama no cabe en ninguna capa
   gratuita, cambiar de proveedor costó **una variable de entorno**. En un
   proyecto sin esa decisión previa, ese mismo hallazgo a tres días de la entrega
   significa reescribir la capa de IA completa.

3. **El trabajo en paralelo no colisiona.** `tasks.md` marca con `[P]` las tareas
   que tocan archivos disjuntos. Seis personas trabajan a la vez sin resolver
   conflictos de merge, porque el reparto se decidió antes de escribir código.

### 3.3 Retorno de la inversión

```
Ahorro frente a tradicional  = USD 1 584 − USD 504 = USD 1 080
Inversión en adoptar SDD     = 6 h  (instalar Spec Kit + escribir la constitución)
                             = 6 h × USD 12 = USD 72

ROI = (1 080 − 72) / 72 = 1 400 %
```

El ROI es alto porque el costo de adoptar la metodología es prácticamente fijo
(una constitución, una vez) mientras que el ahorro escala con cada historia. El
punto de equilibrio se alcanza en **la primera historia de usuario**.

---

## 4. OPEX — costo de operar

### 4.1 Configuración elegida: USD 0.00 / mes

| Componente | Proveedor | Plan | Costo | Límite relevante |
|---|---|---|---|---|
| Backend + frontend | Railway | Free / trial | USD 0 con USD 5 de crédito inicial | Suficiente para una réplica de demostración |
| Base de datos | Railway PostgreSQL | Incluida en el mismo proyecto | USD 0 (consume del crédito) | — |
| Modelo de lenguaje | Groq | Capa gratuita | USD 0 | 30 req/min · 6 000 tokens/min · 1 000 req/día |
| Asistente de código | GitHub Copilot Pro | Student Developer Pack | USD 0 | Gratuito mientras dure la verificación de estudiante |
| Repositorio y CI | GitHub Actions | Público | USD 0 | Minutos ilimitados en repositorios públicos |
| Modelo local (desarrollo) | Ollama | Autoalojado | USD 0 | Consume RAM de la máquina del integrante |
| **Total mensual** | | | **USD 0.00** | |

**El cuello de botella real es Groq: 1 000 peticiones al día.** Cada generación de
proyecto consume 2 llamadas (una para seleccionar el candidato, otra para
describirlo), así que el techo es de **~500 generaciones diarias**. Para una
demostración académica sobra; para un producto con usuarios reales, no.

### 4.2 Qué costaría si creciera

Proyección para el caso en que el proyecto dejara de ser académico:

| Escenario | Infraestructura | IA | Total mensual |
|---|---|---|---|
| Demostración (actual) | USD 0 | USD 0 | **USD 0** |
| ~100 usuarios/día | Railway Hobby USD 5 | Groq gratuito (dentro del límite) | **USD 5** |
| ~1 000 usuarios/día | Railway Hobby USD 5 + uso extra ≈ USD 7 | Groq de pago ≈ USD 3 | **≈ USD 15** |
| ~10 000 usuarios/día | Railway Pro USD 20 + uso extra ≈ USD 30 | Groq ≈ USD 25 | **≈ USD 75** |

*Las cifras de los dos últimos escenarios son extrapolaciones, no mediciones.*

### 4.3 Decisiones que bajaron el OPEX

| Decisión | Alternativa descartada | Ahorro mensual |
|---|---|---|
| Frontend servido por el backend | Vercel como segundo servicio | USD 0 hoy, pero elimina un segundo pipeline y su mantenimiento |
| Groq en lugar de Ollama alojado | Instancia con GPU o con 8 GB de RAM | **USD 25 – 60** |
| Límite de tasa en memoria | Redis gestionado | **USD 5 – 10** |
| Groq en lugar de OpenAI/Anthropic | API de pago por token | **USD 10 – 40** según volumen |
| Límite de tasa por cliente | Sin control de abuso | Evita agotar la cuota gratuita y caer al plan de pago |

Nótese que el propio límite de tasa es una **medida de control de costos**, no
solo de seguridad: sin él, un bucle de `curl` consume la cuota diaria en minutos
y obliga a pagar o a quedarse sin servicio.

---

## 5. Costos no monetarios

Un análisis que solo mira dinero se pierde lo que de verdad diferencia a las tres
metodologías.

| Dimensión | Tradicional | Prompting suelto | SDD |
|---|---|---|---|
| Incorporar a alguien nuevo | Días leyendo código | Imposible: el contexto murió con la conversación | Minutos leyendo la spec |
| Reconstruir por qué se decidió algo | Arqueología en Git | No existe registro | Está escrito en `plan.md` |
| Confianza para refactorizar | Media | Baja | Alta: la suite es el contrato |
| Trabajo real en paralelo | Requiere coordinación constante | Colisiones frecuentes | Tareas `[P]` con archivos disjuntos |
| Auditoría de seguridad | Manual | Inexistente | `docs/security.md` + tests + CI |
| Predecibilidad de la estimación | Media | Nula | Alta: los tickets están descompuestos antes de codificar |

---

## 6. Riesgos del enfoque (y qué hacemos con ellos)

Ser honestos también sobre lo que SDD **no** resuelve:

| Riesgo | Mitigación aplicada |
|---|---|
| Escribir specs para cambios triviales es burocracia | La constitución exige spec para funcionalidades, no para correcciones de una línea |
| Las specs se desactualizan y mienten | Puerta de calidad: el PR no se fusiona si la spec no refleja lo implementado |
| Dependencia de la capa gratuita de un tercero | El modo degradado mantiene la aplicación viva sin proveedor de IA; cambiar de proveedor es una variable de entorno |
| El equipo no adopta la metodología | La constitución es explícita y `AGENTS.md` la impone también a los asistentes de IA |
| Se acaba la verificación de estudiante de Copilot | El motor SDD (Spec Kit) es independiente del asistente: funciona igual con Claude Code, Cursor o Copilot |

---

## 7. Conclusión

Para este alcance, SDD entrega el mismo producto por **USD 504 en lugar de
USD 1 584**, con costo de operación cero y una suite de 204 pruebas que respalda
cada afirmación de este documento.

El argumento más fuerte, sin embargo, no es el ahorro: es que la decisión de
aislar el modelo de lenguaje detrás de una interfaz —tomada en un `plan.md`
mucho antes de pensar en desplegar— convirtió el descubrimiento tardío de que
"Ollama no cabe en ninguna capa gratuita" en un cambio de una línea de
configuración, en lugar de en una reescritura a tres días de la entrega.
Eso es exactamente lo que se compra al escribir la especificación primero.

---

## Fuentes

- [Railway — Pricing](https://railway.com/pricing)
- [Railway — Pricing Plans (Docs)](https://docs.railway.com/pricing/plans)
- [Groq Free Tier Limits 2026](https://tokenmix.ai/blog/groq-free-tier-limits-2026)
- [Groq API Pricing & Free Tier Rate Limits 2026](https://klymentiev.com/blog/groq-pricing)
- [GitHub Student Developer Pack — Copilot para estudiantes (GitHub Community)](https://github.com/orgs/community/discussions/111352)
