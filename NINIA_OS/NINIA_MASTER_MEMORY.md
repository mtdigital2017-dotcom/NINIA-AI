# NINIA_MASTER_MEMORY.md

**Versión:** 2.4  
**Estado:** DOCUMENTO RECTOR VIVO  
**Responsable:** Director Técnico (DT)  
**Ubicación oficial:** `NINIA_OS/NINIA_MASTER_MEMORY.md`  
**Última actualización:** 2026-07-12

> **Regla de oro:** este es el único documento oficial de memoria del proyecto NINIA.  
> Git conserva el historial. No se crearán memorias maestras paralelas.

---

# 0. PROPÓSITO Y GOBERNANZA DE LA MEMORIA

Este documento conserva la identidad, las decisiones, la arquitectura, el estado real y las reglas permanentes de NINIA.

Toda sesión que produzca una decisión estratégica, científica, funcional o técnica deberá:

1. revisar esta memoria;
2. auditar el repositorio;
3. registrar la decisión;
4. desarrollar o integrar;
5. ejecutar QA;
6. actualizar esta memoria;
7. hacer commit y push.

Una decisión no se considera **INTEGRADA** hasta que exista evidencia técnica en el repositorio y pruebas aprobadas.

Estados válidos:

- `PROPUESTA`
- `APROBADA_PARA_EVALUACION`
- `VALIDADA`
- `INTEGRADA`
- `REEMPLAZADA`
- `RETIRADA`

---

# 1. IDENTIDAD

NINIA es una **Plataforma Mundial de Inteligencia Científica para la Protección Integral de Niñas, Niños y Adolescentes en Entornos Digitales**.

NINIA no es:

- un chatbot;
- un portal de noticias;
- un repositorio pasivo de documentos;
- un dashboard aislado;
- una colección de módulos inconexos.

NINIA transforma evidencia verificable en:

- conocimiento estructurado;
- inteligencia comparada;
- investigación;
- recomendaciones;
- políticas públicas;
- cooperación internacional;
- financiación;
- dashboards;
- estadísticas;
- contenidos editoriales;
- productos multimedia;
- acciones adaptables a distintos países.

---

# 2. MISIÓN

Integrar evidencia científica, regulación, programas, campañas, cooperación internacional, financiación, datos y experiencias comparadas para apoyar mejores decisiones en la protección digital de NNA.

---

# 3. VISIÓN

Convertirse en la principal infraestructura mundial de inteligencia científica, benchmarking y acción pública sobre protección de NNA en entornos digitales.

---

# 4. ADN Y PRINCIPIOS PERMANENTES

- Plataforma mundial.
- Multilingüe desde el diseño.
- Evidencia antes que opinión.
- Documento original siempre preservado.
- Traducciones vinculadas al original.
- Citas y bibliografía obligatorias.
- Trazabilidad completa.
- Una única fuente de verdad.
- Un único Knowledge Object alimenta todos los productos derivados.
- No duplicar componentes.
- Auditar antes de desarrollar.
- Reutilizar antes de crear.
- Integrar antes de reemplazar.
- Validación humana obligatoria para conocimiento oficial.
- Diferenciar hechos, inferencias, síntesis y recomendaciones.
- AMI es transversal.
- No confundir diseño con implementación.
- Cada capacidad debe producir valor visible, no solo código.

---

# 5. ARQUITECTURA POR PRODUCTOS

NINIA crecerá por productos científicos integrados, no por archivos aislados.

Productos oficiales:

1. Knowledge
2. Observatory
3. Benchmark
4. Research
5. Policy Lab
6. Cooperation
7. Editorial
8. Media Lab
9. Academy
10. Connect

Cada producto debe tener:

- propósito;
- capacidades;
- fuentes;
- contratos;
- API;
- frontend;
- pruebas;
- estado real;
- documentación;
- productos derivados.

---

# 6. TRES CEREBROS TRANSVERSALES

## Knowledge Brain

Convierte documentos en conocimiento estructurado.

Responsabilidades:

- ingestión;
- normalización;
- extracción;
- entidades;
- taxonomías;
- embeddings;
- búsqueda;
- preservación de originales;
- trazabilidad.

## Reasoning Brain

Integra evidencia, compara experiencias, identifica patrones, explica resultados y genera respuestas o propuestas sustentadas.

## Learning Brain

Recibe retroalimentación controlada de investigadores, expertos y usuarios.

Nunca incorpora conocimiento oficial sin validación humana.

---

# 7. MODELO DE CONOCIMIENTO

Flujo rector:

```text
Documento original
→ Knowledge Object
→ Evidence Assessment
→ Knowledge Graph
→ Índice / Embeddings
→ Búsqueda
→ Benchmark
→ Dashboard
→ Policy Lab
→ Cooperation
→ Editorial
→ Media Lab
```

Todos los productos derivados deben conservar vínculo con:

- documento original;
- idioma original;
- cita;
- bibliografía;
- página o sección;
- estado de validación;
- SHA-256;
- fecha de consulta;
- DOI o URL cuando exista.

---

# 8. INVESTIGACIÓN Y EVIDENCIA

Toda información deberá:

- priorizar fuentes primarias;
- conservar bibliografía;
- indicar nivel de evidencia;
- documentar limitaciones;
- registrar metodología;
- mantener trazabilidad;
- conservar versiones;
- distinguir evidencia observada de recomendación.

Fuentes prioritarias:

- regulación y jurisprudencia oficiales;
- organismos internacionales;
- reguladores;
- revistas científicas;
- universidades;
- datasets oficiales;
- evaluaciones de programas;
- documentos técnicos primarios.

---

# 9. BENCHMARK INTELLIGENCE

El benchmark de NINIA no será descriptivo. Debe responder:

- ¿Quién lo hace?
- ¿Dónde?
- ¿Desde cuándo?
- ¿Qué problema aborda?
- ¿Qué estrategia usa?
- ¿Qué canales utiliza?
- ¿Qué herramientas utiliza?
- ¿Qué población atiende?
- ¿Qué evidencia existe?
- ¿Qué resultados obtuvo?
- ¿Qué funcionó?
- ¿Qué no funcionó?
- ¿Por qué?
- ¿Qué lecciones deja?
- ¿Puede adaptarse?
- ¿Qué recursos requiere?
- ¿Quién financia?
- ¿Qué leyes existen?
- ¿Qué vacíos regulatorios persisten?
- ¿Cómo se implementa frente a la reglamentación vigente?
- ¿Qué opciones de política pública existen?
- ¿Qué recomienda NINIA?

Salidas obligatorias:

- Decision Canvas;
- Knowledge Package;
- Action Portfolio;
- Legal Gap Analysis;
- Implementation Matrix;
- Funding Map;
- Cooperation Map;
- Policy Proposal;
- Action Plan;
- Dashboard;
- estadísticas;
- indicadores;
- bibliografía;
- policy brief;
- artículo;
- podcast;
- infografía;
- boletín;
- contenidos para redes.

El caso Cullen es una **referencia metodológica inicial**, no el estándar definitivo.

Debe ampliarse con:

- llamado a la acción;
- opciones múltiples;
- transferibilidad;
- recursos;
- financiación;
- propuestas de política pública;
- planes de implementación;
- indicadores;
- riesgos y limitaciones.

---

# 10. DECISION CANVAS

Campos mínimos:

- quién lo hace;
- dónde;
- desde cuándo;
- problema;
- estrategia;
- canales;
- herramientas;
- población;
- evidencia;
- resultados;
- qué funcionó;
- qué no funcionó;
- causas;
- lecciones;
- transferibilidad;
- adaptación a Colombia u otro país;
- recursos;
- financiación;
- legislación;
- plan de acción;
- recomendaciones.

---

# 11. OBSERVATORY

Será mundial y continuo.

Cobertura:

- reguladores;
- organismos multilaterales;
- universidades;
- centros de investigación;
- gobiernos;
- industria;
- sociedad civil;
- legislación;
- investigación;
- tecnologías;
- tendencias;
- campañas;
- programas;
- cooperación;
- financiación;
- eventos.

No será una colección de enlaces. Cada novedad deberá convertirse en conocimiento trazable.

---

# 12. POLICY LAB

NINIA asistirá a gobiernos, especialmente países con capacidades técnicas limitadas.

Puede generar borradores de:

- diagnósticos;
- opciones regulatorias;
- propuestas de política pública;
- hojas de ruta;
- matrices de implementación;
- planes de acción;
- indicadores;
- escenarios;
- análisis de impacto;
- recomendaciones.

Siempre deberá diferenciar:

- evidencia observada;
- interpretación de NINIA;
- recomendación;
- supuestos;
- limitaciones;
- revisión humana requerida.

---

# 13. COOPERATION INTELLIGENCE

Debe integrar:

- cooperación científica;
- cooperación técnica;
- cooperación financiera;
- convocatorias;
- donantes;
- organismos multilaterales;
- bancos de desarrollo;
- fundaciones;
- alianzas;
- proyectos;
- países elegibles;
- requisitos;
- fechas;
- montos verificados;
- experiencias financiadas.

Nunca se afirmará que un organismo financiará un proyecto sin fuente oficial.

---

# 14. EDITORIAL Y MEDIA LAB

Todo contenido deriva exclusivamente de conocimiento validado.

Productos:

- artículos;
- policy briefs;
- white papers;
- informes técnicos;
- resúmenes ejecutivos;
- newsletters;
- podcast;
- videopodcast;
- entrevistas;
- infografías;
- presentaciones;
- carruseles;
- publicaciones para redes.

La pestaña de información y noticias es un producto derivado, no el centro de NINIA.

---

# 15. ACADEMY Y CONNECT

## Academy

Formación, transferencia de conocimiento y desarrollo de capacidades.

## Connect

Red internacional de:

- investigadores;
- reguladores;
- organismos multilaterales;
- universidades;
- gobiernos;
- sociedad civil;
- expertos;
- cooperación.

---

# 16. MULTILENGUAJE

Toda la plataforma será multilingüe.

Reglas:

- conservar siempre el documento original;
- conservar texto y citas originales;
- vincular cada traducción con el original;
- mantener glosarios especializados;
- validar traducciones jurídicas, regulatorias y científicas;
- permitir búsqueda semántica multilingüe;
- no duplicar el conocimiento por idioma.

Estados de traducción:

- `BORRADOR_AUTOMATICO`
- `EN_REVISION`
- `VALIDADA`
- `RECHAZADA`

---

# 17. NLP

Decisión vigente: evaluar spaCy como base del reconocimiento general.

Nivel general:

- personas;
- organizaciones;
- países;
- ciudades;
- fechas;
- instituciones.

Nivel especializado NINIA:

- Grooming;
- Sextorsión;
- AMI;
- Salud mental;
- Violencia digital;
- Desinformación;
- IA;
- Plataformas digitales.

Estado actual:

- Diseño: `APROBADO_PARA_EVALUACION`
- Instalación: `PENDIENTE`
- Integración: `NO_VALIDADA`

No se asumirá que spaCy reconoce automáticamente leyes, regulación o conceptos especializados.

---

# 18. BÚSQUEDA E INTELIGENCIA

Pendientes estratégicos:

- pipeline completo;
- índice vectorial;
- RAG;
- búsqueda federada;
- Knowledge Graph;
- NINIA Confidence Index;
- explicabilidad;
- evaluación continua;
- retroalimentación de expertos;
- reentrenamiento controlado.

NINIA no dependerá de un único proveedor de LLM.

---

# 19. FRONTEND

Frontend oficial:

- HTML;
- CSS;
- JavaScript;
- Vercel.

Reglas:

- moderno;
- rápido;
- responsive;
- internacional;
- multilingüe;
- sin lógica de IA;
- consume exclusivamente la API.

Experiencia tipo museo:

```text
Inspira
→ Descubre
→ Explora
→ Investiga
→ Compara
→ Crea
```

---

# 20. BACKEND

Backend oficial: FastAPI.

Responsabilidades:

- autenticación;
- APIs;
- acceso a motores;
- acceso a conocimiento;
- comunicación con frontend;
- trazabilidad;
- gobernanza.

No debe existir lógica duplicada entre frontend y backend.

---


# 20A. GOOGLE COLAB COMO CENTRO DE ENTRENAMIENTO

## Decisión DT-021

**Estado:** VALIDADA PARA INTEGRACIÓN DOCUMENTAL

Google Colab será el **centro de entrenamiento, experimentación y validación de modelos de NINIA** durante la etapa de desarrollo.

Funciones autorizadas de Colab:

- entrenamiento y ajuste de modelos;
- experimentación con NLP;
- pruebas con spaCy y modelos multilingües;
- evaluación de embeddings;
- construcción y prueba de índices vectoriales;
- experimentación con RAG;
- preparación y limpieza de datasets;
- evaluación comparativa de modelos;
- notebooks reproducibles de investigación;
- validación científica y técnica;
- generación de artefactos de modelo;
- pruebas de desempeño antes de promoción.

Colab no será:

- entorno de producción;
- repositorio oficial;
- backend público;
- frontend público;
- fuente de verdad del proyecto;
- almacenamiento definitivo de conocimiento;
- sustituto de GitHub.

Arquitectura de entornos:

```text
Google Colab
→ entrenamiento y experimentación
→ artefactos validados
→ revisión QA
→ integración en GitHub
→ backend FastAPI
→ frontend Vercel
```

Reglas de promoción desde Colab:

1. El notebook debe ser reproducible.
2. Los datos usados deben estar documentados.
3. Deben registrarse versión, parámetros y métricas.
4. Debe existir evidencia de validación.
5. El artefacto debe pasar QA.
6. No se integra ningún modelo sin revisión humana.
7. Todo artefacto aprobado se versiona en Git o en almacenamiento autorizado.
8. Colab nunca modifica directamente producción.

Separación oficial:

- **Colab:** entrenamiento, experimentación y validación.
- **GitHub:** código, memoria, decisiones y versionado.
- **FastAPI:** servicios y lógica de backend.
- **Vercel:** experiencia pública y frontend.
- **Knowledge Hub:** conocimiento validado y trazable.

Esta decisión recupera y formaliza la propuesta histórica de usar Colab como centro de entrenamiento, evitando que se confunda con el entorno operativo de NINIA.

---

# 21. DESARROLLO Y ENSAMBLAJE

Regla permanente:

```text
Auditar
→ Validar
→ Decidir
→ Actualizar Memory
→ Diseñar
→ Implementar
→ Probar
→ Integrar
→ Commit
→ Push
```

No se desarrollan módulos nuevos si la funcionalidad ya existe.

Cada sprint debe producir una capacidad visible.

---

# 22. QA Y ESTADO REAL

Una capacidad solo puede considerarse terminada cuando tiene:

- código;
- pruebas;
- integración;
- documentación;
- evidencia;
- API cuando aplica;
- frontend cuando aplica;
- actualización de memoria;
- commit y push.

El estado real se clasifica como:

- `FUNCIONA`
- `PARCIAL`
- `DISEÑADO`
- `NO_EXISTE`
- `DESCARTADO`

---

# 23. DECISIONES CONGELADAS

- Arquitectura por productos.
- Frontend Vercel.
- Backend FastAPI.
- Reutilización del código existente.
- No duplicar módulos.
- Plataforma multilingüe.
- AMI transversal.
- Desarrollo por sprints.
- Trazabilidad obligatoria.
- Evidencia obligatoria.
- No depender de un solo LLM.
- No usar Streamlit como frontend público.
- No reescribir el Core desde cero.

---

# 24. PENDIENTES ESTRATÉGICOS

## Técnico

- Integración completa del pipeline.
- Índice vectorial.
- RAG.
- FastAPI conectada al Core.
- Conexión real con frontend.
- Aprendizaje continuo.
- Versionado del conocimiento.
- Métricas automáticas.

## Productos

- Benchmark Engine.
- Policy Lab.
- Cooperation Engine.
- Research Engine.
- Editorial Engine.
- Media Lab.
- Academy.
- Connect.

## Inteligencia

- NINIA Confidence Index.
- Explicabilidad.
- Evaluación continua.
- Retroalimentación de expertos.
- Reentrenamiento controlado.

---

# 25. REGISTRO DE DECISIONES DT

## DT-001
Se adopta un único documento maestro.

## DT-002
Se prohíbe la duplicación arquitectónica.

## DT-003
Toda decisión relevante deberá incorporarse a esta memoria.

## DT-004
Se adopta el ensamblaje por líneas y capacidades completas.

## DT-005
El Director Técnico produce artefactos; el usuario revisa y aprueba.

## DT-006
Todo benchmark debe incluir capa de acción y propuestas múltiples.

## DT-007
Toda la plataforma debe ser multilingüe preservando el original.

## DT-008
Todo producto debe tener citas, bibliografía y fuentes especializadas.

## DT-009
Noticias y redes son productos derivados.

## DT-010
Se adopta registro diario obligatorio.

## DT-011
Se auditan chats históricos antes de incorporar decisiones.

## DT-012
Se adopta arquitectura por productos y tres cerebros transversales.

## DT-013
Toda propuesta técnica se valida contra la memoria oficial.

## DT-014
No se crean componentes antes de auditar el repositorio.

## DT-015
Se prioriza auditoría integral y matriz de ensamblaje.

## DT-016
`NINIA_MASTER_MEMORY.md` es la única fuente oficial de verdad.

## DT-017
La memoria será un documento vivo versionado por Git.

## DT-018
Cada sesión debe actualizar la memoria cuando corresponda.

## DT-020
Se consolida el documento ya versionado con el resumen histórico recuperado.

## DT-021
Google Colab se establece como centro de entrenamiento, experimentación y validación; no como entorno de producción.

---

## DT-024
El adaptador de Biblioteca validado en Colab se integra como archivo independiente en el frontend. No se modifica el backend ni se crea otro motor Knowledge. El intento local anterior no aprobado se restaura antes de aplicar el candidato oficial.

---

## DT-025
Los estados operativos, planes automáticos, trazas y manifiestos regenerables del Runtime se conservan localmente y quedan fuera de Git. Git versiona código, reglas estables, decisiones aprobadas, documentación y memoria oficial.

---

# 26. BITÁCORA VIVA

## Plantilla obligatoria por sesión

```text
Fecha:
Objetivo:
Decisiones:
Estado:
Evidencia revisada:
Archivos afectados:
Pruebas:
Riesgos:
Pendientes:
Siguiente paso:
Commit:
```

---

# 27. SESIÓN 2026-07-12

**Objetivo:** consolidar la memoria oficial y fusionar el contenido ya versionado con el resumen histórico.

**Decisiones:**

- establecer Google Colab como centro de entrenamiento y experimentación;
- separar Colab de producción, GitHub, FastAPI y Vercel;
- mantener un único `NINIA_MASTER_MEMORY.md`;
- fusionar, no reemplazar;
- preservar decisiones ya versionadas;
- incorporar arquitectura por productos;
- incorporar tres cerebros;
- incorporar productos, pendientes, multilenguaje, NLP, policy y cooperation;
- no declarar implementado lo que sigue pendiente.

**Estado:**

- Consolidación documental: `VALIDADA`
- Integración en repositorio: `PENDIENTE`
- Commit: `PENDIENTE`

**Siguiente paso:**

Integrar este archivo en `NINIA_OS/NINIA_MASTER_MEMORY.md`, ejecutar validación y hacer commit.

---



---

# 29. SPRINT 1 — ADAPTADOR DE BIBLIOTECA KNOWLEDGE

**Fecha:** 2026-07-12  
**Producto:** Knowledge  
**Estado:** VALIDADO_EN_COLAB — PENDIENTE_DE_INTEGRACIÓN_LOCAL

## Objetivo

Cerrar el primer flujo visible reutilizando el backend aprobado:

```text
Documento
→ POST /documents/process
→ Knowledge Object PROPUESTO
→ GET /knowledge
→ Adaptador de Biblioteca
→ Frontend
```

## Resultado validado en Colab

- El Knowledge Contract v1 es compatible con el frontend.
- La Biblioteca consume `GET /knowledge`.
- Se reutiliza `POST /documents/process`.
- El backend no requiere cambios.
- Los documentos nuevos permanecen en estado `PROPUESTO`.
- No existe aprobación automática.
- Se preservan fuente, idioma original, nivel de evidencia, estado y procedencia.
- El adaptador incluye búsqueda, manejo de errores y estado vacío verificable.
- La sintaxis JavaScript fue aprobada en Colab.

## Archivos candidatos aprobados

### NINIA-FRONTEND

- `index.html`
- `styles.css`
- `ninia-knowledge-adapter.js`
- `app.js` se restaura a la base auditada para retirar el intento local anterior no aprobado.

### NINIA-AI

- `NINIA_OS/NINIA_MASTER_MEMORY.md`

El backend se reutiliza sin modificaciones.

## Brechas no bloqueantes

- detección automática del idioma original;
- extracción de autores;
- entidades NLP con spaCy;
- citas y páginas;
- URL HTTPS pública de FastAPI para Vercel;
- búsqueda semántica y RAG.

## Criterio de cierre

El Sprint solo cambiará a `INTEGRADO` cuando:

1. los archivos aprobados se apliquen a los repositorios locales;
2. la validación local del paquete sea aprobada;
3. se revisen los cambios en GitHub Desktop;
4. se realicen commits separados en frontend y memoria;
5. se haga push;
6. se compruebe la Biblioteca contra un backend accesible.

## Siguiente paso

Aplicar el paquete oficial de integración, revisar `Changes` en ambos repositorios y realizar commits limpios separados.


# 30. POLÍTICA DEL RUNTIME FRENTE A GIT

**Fecha:** 2026-07-12  
**Estado:** VALIDADA_EN_COLAB — PENDIENTE_DE_COMMIT

## Regla permanente

Git conserva:

- código;
- reglas y configuraciones estables;
- decisiones aprobadas;
- documentación;
- pruebas;
- `NINIA_MASTER_MEMORY.md`.

El Runtime conserva localmente y fuera de Git:

- `NINIA_OS/DT_RUNTIME/executive_traces/*.json`;
- `NINIA_OS/PLANS/*.json`;
- `NINIA_OS/DT_RUNTIME/AUTOMATION_STATUS.json`;
- `NINIA_OS/DT_RUNTIME/current_context.json`;
- `NINIA_OS/DT_RUNTIME/GUARDIAN_REPORT.json`;
- `NINIA_OS/DT_RUNTIME/last_decision_plan.json`;
- `NINIA_OS/PROJECT_MANIFEST.json`;
- `NINIA_OS/MASTER_MEMORY_MERGE_AUDIT.md`.

## Justificación

Estos archivos cambian por ejecución, contienen timestamps o estados locales y pueden regenerarse. No representan decisiones institucionales ni capacidades aprobadas. Mantenerlos versionados genera ruido y dificulta distinguir avances reales.

## Implementación segura

- se crea respaldo completo antes del cambio;
- se actualiza `.gitignore`;
- los archivos se retiran del índice de Git;
- los archivos locales no se borran;
- no se ejecuta el Runtime;
- no se hace commit ni push automáticamente.

## Criterio de cierre

La política quedará `INTEGRADA` cuando se revise el diff, se haga un commit independiente y se complete el push.


# 28. REGLA FINAL

Antes de cualquier desarrollo:

1. leer esta memoria;
2. auditar el repositorio;
3. verificar no duplicidad;
4. actualizar la memoria si hay decisiones;
5. desarrollar;
6. ejecutar QA;
7. versionar en Git.

No existirán memorias maestras paralelas.

---

# SPRINT 2.1 — EVIDENCE CELL V1

**Estado:** VALIDADO_EN_COLAB — INTEGRACIÓN_LOCAL_APLICADA

## Resultado

- Se reutilizó `NiniaEngine`; no se creó otro `DocumentProcessor`.
- `NiniaEngine` evoluciona a v1.1.
- Se integró el `Knowledge Contract v1` en el flujo real.
- Se añadieron servicios reutilizables:
  - Language Detector;
  - Hash Service SHA-256;
  - DOI Extractor;
  - Metadata Extractor;
  - Knowledge Contract Adapter.
- Los objetos normalizados se guardan en `knowledge/proposed`.
- La validación humana continúa siendo obligatoria.
- No existe aprobación automática.
- QA en Colab: 48 pruebas aprobadas.

## Archivos funcionales integrados

- `engine/ninia_engine.py`
- `engine/services/__init__.py`
- `engine/services/language_detector.py`
- `engine/services/hash_service.py`
- `engine/services/doi_extractor.py`
- `engine/services/metadata_extractor.py`
- `engine/services/knowledge_adapter.py`
- `tests/test_evidence_cell_v1.py`

## Limitaciones aceptadas en v1

- detección de idioma heurística;
- extracción básica de autores, año y DOI;
- revisión humana obligatoria.

---

## Unified Evidence Intake v1

Se unificaron los flujos previamente paralelos:

```text
EvidenceAdmissionEngine
→ deduplicación
→ cuarentena
→ NiniaEngine
→ Knowledge Contract
→ Knowledge Object PROPUESTO
→ revisión
→ sincronización de estado
```

Reglas:

- no se creó otro DocumentProcessor;
- no se creó otro motor de admisión;
- no se creó otro corpus;
- CUARENTENA y PROPUESTO permanecen separados;
- la aprobación humana sincroniza el Knowledge Object;
- no existe aprobación automática.

QA: todas las pruebas aprobadas.

---

## Evidence Layer v1

Clasificación: `EXTENSIÓN`

Se amplió el Knowledge Object existente con:

- `evidence_fragments`;
- `typed_relations`;
- `source_locator`;
- `confidence`;
- `validation_status`.

Reglas:

- compatibilidad hacia atrás;
- `schema_version` permanece en `1.0`;
- objetos heredados reciben listas vacías;
- fragmentos y relaciones nacen en `PROPUESTO`;
- no existe aprobación automática;
- no se creó otra biblioteca, corpus o procesador.

QA: todas las pruebas aprobadas.

---

## Sprint 2.4 — Integración Operativa Backend ↔ Frontend

Estado: VALIDADO_EN_COLAB

Resultado:

- FastAPI reutilizado; no se creó otro backend.
- Frontend existente conectado a `/health`, `/knowledge`,
  `/researcher/specialties` y `/evidence/requests`.
- La admisión de investigadores reutiliza `admit_and_process`.
- Los documentos ingresan en `CUARENTENA`.
- El Knowledge Object se genera en `PROPUESTO`.
- La Biblioteca pública continúa mostrando conocimiento aprobado.
- El panel del investigador consulta sus solicitudes por correo institucional.
- Sin aprobación automática.
- QA backend: 57 pruebas aprobadas.
- QA frontend: JavaScript validado sin errores de sintaxis.

Limitación conocida:

- El filtro por correo institucional es una protección funcional del PMV,
  no sustituye autenticación robusta. La autenticación se implementará
  cuando corresponda en el roadmap aprobado.

---

## Sprint 2.5 — Corpus Oficial Piloto

Estado: VALIDADO_EN_COLAB

Se ejecutó el primer ciclo automático de adquisición de evidencia
oficial usando la arquitectura existente.

Resultados:

- documentos descargados: 13;
- documentos procesados: 13;
- Knowledge Objects en PROPUESTO;
- Evidence Layer generada;
- dominios oficiales verificados;
- SHA-256 y trazabilidad preservados;
- sin aprobación automática;
- QA completo aprobado.

---

## Sprint 2.6 — Global Evidence Acquisition Engine v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN

Se añadió una capa de adquisición que reutiliza el flujo existente:

Fuente oficial
→ descubrimiento
→ descarga controlada
→ EvidenceAdmissionEngine
→ CUARENTENA
→ NiniaEngine
→ Knowledge Object PROPUESTO
→ Evidence Layer

Capacidades:

- catálogo configurable de fuentes oficiales;
- validación estricta de dominios;
- descubrimiento desde páginas HTML y XML/sitemaps;
- descarga limitada a PDF, DOCX y TXT;
- SHA-256;
- manejo de duplicados;
- manifiestos de adquisición;
- sin aprobación automática.

No se creó otro DocumentProcessor, corpus, biblioteca ni motor de admisión.

QA: 59 pruebas aprobadas.

---

## Sprint 2.7.1 — Scientific Validation Engine v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN

Corrección aplicada:

- la auditoría valida capacidades y rutas reales;
- no depende de comentarios o cadenas documentales;
- se reutilizan EvidenceAdmissionEngine, Evidence Layer,
  Knowledge Contract y FastAPI;
- no se crea un flujo paralelo;
- no existe aprobación automática;
- toda decisión final requiere revisión humana.

QA: 61 pruebas aprobadas, 2 advertencias, 0 fallos.

---

## Sprint 2.8 — Knowledge Graph Foundation v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN

Se añadió una vista derivada del conocimiento aprobado:

Knowledge Object APROBADO
→ nodos
→ relaciones
→ trazabilidad
→ persistencia en knowledge/graph

Reglas:

- solo usa objetos con estado APROBADO;
- no modifica Knowledge Objects;
- no cambia estados;
- no aprueba evidencia;
- conserva knowledge_id, SHA-256 y fragmentos de evidencia;
- valida nodos huérfanos, aristas inválidas y duplicados;
- no crea una biblioteca paralela.

Archivos generados:

- knowledge_graph.json;
- graph_nodes.json;
- graph_edges.json;
- graph_index.json.

QA: 65 pruebas aprobadas, 2 advertencias, 0 fallos.

---

## Sprint 2.9 — Evidence Dataset Platform v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN

Se añadió una vista derivada que convierte exclusivamente
Knowledge Objects APROBADOS en datasets reproducibles y trazables.

Salidas:

- train.jsonl;
- validation.jsonl;
- test.jsonl;
- rag_chunks.jsonl;
- benchmark.jsonl;
- statistics.json;
- manifest.json.

Reglas:

- solo conocimiento APROBADO;
- no modifica Knowledge Objects;
- no cambia estados;
- no aprueba evidencia;
- división determinística con semilla registrada;
- trazabilidad hasta knowledge_id, fragment_id y SHA-256;
- misma entrada y semilla producen el mismo dataset;
- no habilita entrenamiento si el corpus no cumple mínimos.

Política permanente aplicada:

Todo sprint actualiza automáticamente memoria, estado,
roadmap, changelog, QA y reporte del sprint.

QA: 67 pruebas aprobadas, 2 advertencias, 0 fallos.

---

## Sprint 3.0 — AI Trainer MVP v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN

Se añadió el primer entrenador reproducible de NINIA.

Entrada única:

- datasets generados por EvidenceDatasetService;
- train.jsonl;
- validation.jsonl;
- test.jsonl;
- manifest.json.

Reglas:

- el entrenador no lee documentos originales;
- el entrenador no lee Knowledge Objects;
- solo consume datasets con política APPROVED_KNOWLEDGE_ONLY;
- se detiene si el dataset no está listo;
- entrenamiento reproducible;
- mismo dataset y configuración producen el mismo model_id;
- métricas de accuracy, macro precision, macro recall y macro F1;
- matriz de confusión;
- registro versionado del modelo;
- sin aprobación automática;
- sin pipeline paralelo.

Modelo MVP:

- clasificador Multinomial Naive Bayes;
- implementación con Python estándar;
- sin nuevas dependencias externas.

QA: 70 pruebas aprobadas, 2 advertencias, 0 fallos.

---

## Baseline real del modelo v0.1

Estado: INTEGRADO

Fecha: 2026-07-14T04:37:38.043744+00:00

Resultados:

- model_version: 0.1.0-real;
- dataset_version: 0.1.0-real;
- Knowledge Objects aprobados en la ejecución: 13;
- ejemplos del dataset: 520;
- etiquetas: 8;
- accuracy estándar de validación: 0.6154;
- macro-F1 estándar de validación: 0.6014;
- accuracy estricta por documento: 0.2731;
- macro-F1 estricta por documento: 0.1257.

Decisión DT:

La evaluación estricta por documento es la referencia principal.
El baseline v0.1 no es modelo de producción.
Se utilizará para medir mejoras futuras del corpus, etiquetas y algoritmo.

---

## Sprint 3.1 — Strict Corpus Audit & Batch Review v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN

Se añadió una auditoría estricta y reproducible del corpus.

Capacidades:

- prevalidación automática de Knowledge Objects PROPUESTOS;
- clasificación en:
  - READY_FOR_BATCH_REVIEW;
  - INDIVIDUAL_HUMAN_REVIEW;
  - REMAIN_IN_QUARANTINE;
- auditoría de duplicados por SHA-256, URL/DOI y título;
- balance por categoría;
- cobertura por fuente, idioma y año;
- Corpus Score transparente y recalculable;
- umbral mínimo de 80 objetos aprobados;
- mínimo 10 objetos aprobados por categoría;
- bloqueo del siguiente entrenamiento oficial cuando no se cumplen mínimos;
- ninguna aprobación automática;
- revisión humana obligatoria.

Regla científica:

El Corpus Score no representa accuracy del modelo.
Ninguna mejora de accuracy, precision, recall o F1 podrá registrarse
sin un entrenamiento reproducible y una evaluación estricta independiente.

QA: 75 pruebas aprobadas, 2 advertencias, 0 fallos.

---

## Sprint 3.2 — Operational Knowledge Factory v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN OPERATIVA

Se añadió una única orquestación sobre los componentes existentes:

Trusted official sources
→ GlobalEvidenceAcquisitionService
→ EvidenceAdmissionEngine
→ ScientificValidationService
→ CorpusAuditService
→ EvidenceDatasetService
→ AITrainerService

Capacidades:

- búsqueda y adquisición controlada desde el catálogo oficial existente;
- documentos nuevos permanecen en CUARENTENA;
- Knowledge Objects nuevos permanecen en PROPUESTO;
- preevaluación científica automática;
- auditoría estricta del corpus;
- generación de dataset únicamente si el corpus aprobado cumple mínimos;
- entrenamiento únicamente cuando el training gate está abierto;
- persistencia de manifiesto por ejecución;
- estado operativo consultable por API;
- endpoints:
  - GET /operations/status
  - POST /operations/run

Gobernanza:

- no existe aprobación automática;
- la revisión humana sigue siendo obligatoria;
- el entrenador no lee documentos ni Knowledge Objects;
- no se creó otro backend, corpus, dataset builder o trainer;
- el frontend puede consultar evolución mediante polling de /operations/status.

QA local previo: 73 pruebas aprobadas, 2 advertencias, 0 fallos.

---

## Sprint 3.3 — Operational Center & Adaptive Media Center v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN END-TO-END

Objetivo:

Hacer visible y utilizable desde el frontend el flujo operativo
implementado en Sprint 3.2, sin crear otro backend ni otro repositorio
de contenidos.

Capacidades frontend:

- Centro de Operaciones conectado a:
  - GET /operations/status
  - POST /operations/run
- actualización automática cada 5 segundos;
- visualización de:
  - estado del backend;
  - Knowledge Objects propuestos y aprobados;
  - Corpus Score;
  - adquisición;
  - Training Gate;
  - modelo oficial y métricas estrictas;
- ejecución de una misión controlada desde el frontend;
- Centro de Medios generado desde Knowledge Objects APROBADOS;
- adaptación por público:
  - familias;
  - docentes;
  - niñas, niños y adolescentes;
  - reguladores;
  - investigadores;
  - público general.

Gobernanza editorial adaptativa:

- fuente Nivel A + síntesis informativa fiel:
  publicación automática con auditoría posterior;
- contenido comparativo, interpretativo o de fuente no Nivel A:
  revisión editorial proporcional al riesgo;
- ninguna noticia se construye desde conocimiento PROPUESTO;
- cada producto conserva knowledge_id, fuente, año y trazabilidad;
- no existe un CMS ni una base de contenidos paralela.

Regla permanente:

Toda capacidad nueva debe quedar disponible de extremo a extremo:
backend + API + frontend + QA + Master Memory.

El Centro de Medios es una salida del conocimiento aprobado,
no un sistema independiente.

---

## Sprint 3.4 — Global Observatory & Mission-Centric Platform v1

Estado: VALIDADO_EN_COLAB

Clasificación: EXTENSIÓN VERTICAL END-TO-END

### Identidad oficial

NINIA es una Plataforma Mundial de Inteligencia Científica para la
Protección Integral de Niñas, Niños y Adolescentes en Entornos
Digitales. No es un sistema nacional ni un chatbot.

### Misión mundial

Monitorear, investigar, analizar y transformar evidencia mundial en:

- conocimiento científico estructurado;
- inteligencia pública y estratégica;
- productos del Media Center;
- formación y recursos AMI;
- propuestas de políticas, programas y planes de acción;
- indicadores, recomendaciones y aprendizaje organizacional.

### Arquitectura congelada

- Global Observatory: monitorea y organiza evidencia mundial.
- Knowledge Engine: transforma evidencia validada en conocimiento.
- Knowledge Graph: conecta entidades, dominios y relaciones.
- Media Center / Publishing Engine: comunica conocimiento.
- Centro AMI / Learning Engine: desarrolla capacidades.
- Action Lab: propone opciones fundamentadas en evidencia.
- Intelligence Hub: apoya análisis y toma de decisiones.
- Organizational Learning: registra resultados y lecciones.

No se crearán motores principales paralelos.

### Fuente única de verdad

Toda noticia, artículo, podcast, policy brief, white paper, informe,
recurso AMI, actividad, propuesta o plan deberá derivarse de Knowledge
Objects APROBADOS y conservar trazabilidad a la evidencia original.

### Publicación y revisión proporcional al riesgo

- Fuente oficial de alta confianza + síntesis informativa fiel:
  publicación automática con auditoría posterior.
- Contenido comparativo, interpretativo, normativo o de fuente con
  incertidumbre:
  revisión humana proporcional al riesgo.
- Ningún producto se genera desde conocimiento PROPUESTO.

### Centro de Medios

Toda investigación pertinente podrá producir, entre otros:

- noticias;
- artículos y artículos periodísticos;
- reportajes;
- guiones de podcast y video;
- boletines y newsletters;
- infografías;
- policy briefs;
- white papers;
- documentos para políticas públicas;
- informes técnicos y resúmenes ejecutivos.

### Centro AMI

El Observatorio y el Knowledge Engine alimentan obligatoriamente al
Centro AMI. El mismo conocimiento aprobado podrá producir:

- guías para familias;
- materiales para NNA;
- recursos y actividades para docentes;
- cursos, talleres, casos, simulaciones y evaluaciones;
- rutas de aprendizaje;
- materiales para investigadores y responsables de políticas.

AMI nunca utilizará evidencia bruta como vía habitual; consumirá
conocimiento estructurado y trazable.

### Del conocimiento a la acción

NINIA podrá proponer, sin sustituir la decisión humana:

- políticas públicas;
- estrategias;
- campañas;
- programas;
- planes de acción;
- hojas de ruta;
- matrices de riesgo;
- indicadores y mecanismos de seguimiento.

Toda propuesta deberá indicar evidencia, jurisdicciones, nivel de
confianza, alternativas y limitaciones.

### Living Knowledge

Se versionan:

- Knowledge Objects;
- corpus;
- datasets;
- modelos;
- productos editoriales y educativos;
- estrategias y recomendaciones.

Cuando cambie el conocimiento, los productos derivados deberán marcarse
para revisión o regeneración.

### Aprendizaje organizacional

NINIA aprenderá de evidencia externa y de sus propios resultados.
Registrará:

- qué funcionó;
- qué no funcionó;
- por qué;
- condiciones de éxito o fracaso;
- lecciones aprendidas;
- buenas prácticas;
- acciones futuras;
- evidencia de impacto.

Las propuestas futuras deberán apoyarse prioritariamente en lo que haya
demostrado funcionar bajo condiciones comparables.

### Arquitectura centrada en misiones

La misión es la unidad operativa principal. Reúne:

- objetivo;
- dominios;
- regiones y jurisdicciones;
- fuentes;
- evidencia;
- Knowledge Objects;
- productos Media;
- recursos AMI;
- propuestas del Action Lab;
- métricas;
- impacto;
- lecciones aprendidas.

### Misión piloto

`Regulatory Intelligence Cullen` organiza el primer lote temático
especializado sobre regulación, corregulación, autorregulación,
publicidad, servicios audiovisuales y protección de menores.

La creación de la misión no implica aprobación automática ni ingestión
silenciosa de los PDFs.

### Decisiones consolidadas

- DT-043: toda investigación puede alimentar el Media Center.
- DT-044: publicar una vez y reutilizar desde una fuente única.
- DT-045: NINIA Knowledge Ecosystem.
- DT-046/047: Media Center y Centro AMI como rutas públicas distintas.
- DT-048 corregida: alcance mundial, no nacional.
- DT-049: Living Knowledge System.
- DT-050: Global-by-Design.
- DT-051/052: Observatorio como proveedor de conocimiento para AMI,
  Media, Knowledge y Action Lab.
- DT-053/054: misión mundial y transformación del conocimiento en acción.
- DT-055/056: cadena de valor e investigación orientada por brechas.
- DT-057: Global Intelligence Architecture.
- DT-058/059: Organizational Learning y aprendizaje continuo.
- DT-060: Evidence-to-Impact Framework.
- DT-061: doble ciclo de conocimiento e impacto.
- DT-062: Capability First.
- DT-063: Architecture Freeze.
- DT-064: configuración y catálogos antes que hardcode.
- DT-065: Mission-Centric Architecture.
- DT-066: Global Observatory como capa sobre servicios existentes.

### Regla de cierre

Una capacidad solo se considera terminada cuando incluye:

backend + API + frontend + QA + documentación + Master Memory.

---

## Hotfix 3.4.1 — Frontend Navigation Stability

Estado: VALIDADO_EN_COLAB  
Clasificación: CORRECCIÓN VERTICAL CONTROLADA  
Fecha de validación: 2026-07-15T03:11:21.196618+00:00

### Incidente observado

En producción, el frontend podía bloquear el navegador al navegar desde
el Observatorio Mundial hacia Operaciones y otras vistas dinámicas.

### Causa raíz confirmada

Tres módulos utilizaban `MutationObserver` para volver a ejecutar
funciones de renderizado sobre el mismo árbol DOM que estaban
observando:

- `ninia-operations-media.js`
- `ninia-global-observatory.js`
- `ninia-api-bridge.js`

El render generaba nuevas mutaciones, el observador reaccionaba a ellas
y reiniciaba el render de forma indefinida.

### Cambio aprobado

La coordinación de navegación se trasladó a:

- evento `hashchange`;
- evento `DOMContentLoaded`;
- programación mediante `requestAnimationFrame`;
- cancelación de activaciones pendientes antes de programar una nueva.

No se modificaron contratos API, rutas backend ni estructura principal
del frontend.

### Qué funcionó

- Mantener `app.js` como router principal.
- Utilizar eventos de navegación explícitos.
- Programar una sola activación por cuadro.
- Conservar los endpoints existentes.
- Validar primero en Colab antes de generar instaladores.

### Qué no funcionó

Utilizar `MutationObserver` como mecanismo de navegación o de
reactivación del render sobre el mismo contenedor observado.

### Lección aprendida permanente

No utilizar `MutationObserver` para volver a renderizar el mismo árbol
DOM que el observador vigila. En NINIA, la navegación por hash debe
coordinarse mediante eventos explícitos e idempotentes.

### Regla metodológica confirmada

Todo cambio de frontend sigue esta ruta:

Desarrollo → Colab → QA → Aprobación DT → RESULTS.zip →
Installer Git → Commit → Vercel → Verificación de producción.

### Estado de producción

PENDIENTE_DE_INSTALLER_GIT_Y_VERIFICACION_EN_VERCEL

---

## Backend Final Local Path v2

Estado: VALIDADO_EN_COLAB

### Ruta oficial del backend en este equipo

`~/Library/Mobile Documents/com~apple~CloudDocs/Desktop/NINIA-AI 2`

### Fuente de entrada

El notebook acepta tanto `RESULTS.zip` como `FINAL_RESULTS.zip` y los
identifica por contenido, no por nombre de archivo.

### Regla permanente

- Detectar artefactos por estructura y contenido.
- No depender del nombre exacto del ZIP.
- Aplicar cambios únicamente sobre la ruta real usada por GitHub Desktop.
- Verificar `.git`, estructura y remoto `origin`.
- No ejecutar `commit` ni `push`.
- Mantener compatibilidad con Bash 3.2 de macOS.

