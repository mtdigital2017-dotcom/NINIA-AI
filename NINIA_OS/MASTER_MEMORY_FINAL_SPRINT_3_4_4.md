# MASTER MEMORY FINAL — SPRINT 3.4.4

## Estado
LISTO_PARA_INSTALACIÓN_GIT_LOCAL Y DESPLIEGUE EN RENDER

## Objetivo
Cerrar la integración entre NINIA-FRONTEND y NINIA-AI sin más reprocesos, manteniendo GitHub como repositorio oficial y usando una plataforma backend adecuada para FastAPI.

## Diagnóstico consolidado
1. El frontend desplegado en Vercel funciona.
2. El backend FastAPI pasa 81 pruebas.
3. La aplicación responde correctamente en local y bajo simulación `VERCEL=1`.
4. En Vercel se observaron:
   - despliegues detenidos en `Queued` e `Initializing`;
   - rutas secundarias con `404: NOT_FOUND`;
   - posteriormente `FUNCTION_INVOCATION_FAILED`.
5. El código backend no presenta fallos funcionales en las pruebas disponibles.
6. La causa operativa más sólida es la incompatibilidad práctica entre la carga de NINIA y el modelo serverless de Vercel.

## Decisión del DT
- Mantener el frontend en Vercel.
- Migrar el backend a Render como servicio web persistente.
- Mantener GitHub y GitHub Desktop como flujo oficial de repositorio y publicación.
- No seguir parcheando Vercel para el backend.

## Arquitectura final
- Frontend: `NINIA-FRONTEND` → GitHub → Vercel.
- Backend: `NINIA-AI` → GitHub → Render.
- Backend URL prevista: `https://ninia-ai-mtdigital2017.onrender.com`.
- Health check: `/health`.
- Build: `pip install -r requirements.txt`.
- Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`.
- Auto-deploy: cada commit en `main`.

## Cambios finales
### Backend
- `render.yaml` actualizado.
- `.python-version` fijado en Python 3.12.8.
- Se conserva el código FastAPI validado.
- No se modifica la lógica funcional.

### Frontend
- `config.js` usa Render como backend principal.
- Vercel queda como respaldo.
- La URL se valida automáticamente mediante `/health`.
- No se exige al usuario introducir URLs.

## QA
- Backend: 81 pruebas aprobadas.
- Importación de `app`: aprobada.
- `/`: 200.
- `/health`: 200.
- `/docs`: 200.
- `/openapi.json`: 200.
- `/knowledge`: 200.
- Sintaxis `config.js`: validada.

## Incidentes documentados
- Reprocesos por instaladores temporales.
- Dependencia local de Node.
- Autenticación HTTPS de Git.
- Conflictos de merge en memoria y estado.
- Bloqueo de despliegues Vercel.
- Fallo de rutas y función serverless.
- Decisión final de separar frontend y backend por plataforma.

## Regla permanente
Cada sprint debe cerrar con:
1. QA en Colab.
2. ZIP para revisión DT.
3. Master Memory.
4. Instalador local.
5. Publicación con GitHub Desktop.
6. Validación en producción.

## Siguiente paso
Aplicar el instalador final, publicar backend y frontend desde GitHub Desktop y crear el servicio de Render desde `render.yaml`.
