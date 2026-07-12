# Automatización integral del DT Runtime

## Estado
VALIDADO EN ENTORNO AISLADO.

## Comportamiento automático

1. Al iniciar FastAPI:
   - reconstruye memoria;
   - valida QA;
   - genera `PROJECT_MANIFEST.json`;
   - actualiza `AUTOMATION_STATUS.json`.

2. Antes de cada solicitud:
   - vuelve a ejecutar el bootstrap;
   - bloquea la solicitud si la memoria falla.

3. En `/dt/plan`:
   - ejecuta Executive Controller;
   - consulta Decision Engine;
   - selecciona especialista principal y apoyos;
   - registra traza;
   - actualiza el contexto.

## Endpoints
- `GET /dt/health`
- `POST /dt/plan`
