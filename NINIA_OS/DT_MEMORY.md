# DT_MEMORY

## Identidad

- Proyecto: NINIA-AI
- Propósito: sistema inteligente para la protección integral de niñas, niños y adolescentes en entornos digitales.
- Estado técnico de referencia: plataforma avanzada en desarrollo; no tratar como PMV.
- Versión base recibida: v1.0.3 Evidence Admission API.
- Fecha de consolidación: 2026-07-11.

## Arquitectura confirmada

- `api/`: interfaz FastAPI.
- `engine/ninia_engine.py`: procesamiento documental y objetos de conocimiento.
- `engine/evidence_admission.py`: admisión, cuarentena, hash, duplicados y revisión humana.
- `knowledge/`: estados persistidos del conocimiento.
- `tests/`: pruebas automáticas.
- `docs/`: contratos y documentación técnica.
- `NINIA_OS/`: memoria operativa y gobierno técnico.
- `.github/workflows/`: automatización y respaldos.

## Reglas permanentes

1. GitHub es la fuente oficial del código y la documentación viva.
2. Cada `push` a `main` ejecuta pruebas y genera un respaldo verificado en Google Drive.
3. No se suben secretos, credenciales, datos procesados ni archivos temporales.
4. Todo conocimiento requiere validación humana antes de quedar aprobado.
5. AMI es transversal.
6. No se duplica un módulo sin revisar primero la arquitectura existente.
7. El usuario es principiante: explicar cada paso antes de ejecutarlo.
8. Toda propuesta final debe quedar respaldada en GitHub y Drive.

## Estado actual

- API de admisión de evidencia presente.
- Flujo de cuarentena y revisión humana presente.
- Pruebas existentes preservadas.
- Automatización GitHub → Google Drive incorporada en esta entrega.
- Pendiente humano: configurar credenciales y carpeta de Drive en GitHub Secrets.

## Próxima decisión

No iniciar nuevas funciones hasta ejecutar y comprobar el primer respaldo automático exitoso.
