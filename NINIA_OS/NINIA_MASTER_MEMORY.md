# NINIA_MASTER_MEMORY.md

**Versión:** 2.2  
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
