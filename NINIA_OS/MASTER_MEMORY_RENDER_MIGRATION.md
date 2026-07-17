# MASTER MEMORY — MIGRACIÓN BACKEND A RENDER

## Estado
PREPARADO_PARA_GITHUB_DESKTOP

## Decisión del DT
El backend de NINIA migra de Vercel a Render debido a despliegues repetidos detenidos en `Queued` e `Initializing` sin generación de Build Logs.

## Arquitectura resultante
- Frontend: Vercel.
- Backend principal: Render.
- Backend de respaldo: Vercel, si vuelve a estar disponible.
- Repositorios: GitHub.
- Banco oficial de pruebas: Google Colab.

## Configuración Render
- Servicio: `ninia-ai`.
- Runtime: Python.
- Build: `pip install -r requirements.txt`.
- Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`.
- Health check: `/health`.
- Auto-deploy: cada commit en `main`.

## Frontend
`config.js` prueba primero `https://ninia-ai.onrender.com` y mantiene `https://ninia-ai.vercel.app` como respaldo.

## Gobierno
- No se ejecutan pruebas locales.
- No se hace push desde Terminal.
- GitHub Desktop sigue siendo la interfaz oficial.
- Los siguientes despliegues serán automáticos después de la vinculación inicial de Render con GitHub.

## Siguiente paso
Aplicar el instalador, publicar ambos repositorios desde GitHub Desktop y crear el Blueprint en Render.
