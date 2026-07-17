# MASTER MEMORY — SPRINT 3.4.3.1 — CORRECCIÓN DE RUTAS VERCEL

## Estado
LISTO_PARA_GITHUB_DESKTOP

## Diagnóstico confirmado
- `https://ninia-ai.vercel.app/` responde desde FastAPI.
- `https://ninia-ai.vercel.app/docs` devuelve `404: NOT_FOUND` de Vercel.
- `https://ninia-ai.vercel.app/health` devuelve `404: NOT_FOUND` de Vercel.
- La aplicación FastAPI sí contiene `/docs`, `/health` y `/knowledge`.

## Causa
El archivo `vercel.json` establecía una configuración explícita innecesaria que interfería con la detección y el enrutamiento automático del preset FastAPI.

## Corrección
- Eliminar `vercel.json`.
- Conservar `index.py` raíz exportando `app`.
- Permitir que Vercel detecte FastAPI y enrute todas sus subrutas automáticamente.
- No modificar código funcional del backend.

## Validación posterior requerida
- `/`
- `/docs`
- `/health`
- `/knowledge`

## Gobierno
- Respaldo automático antes de modificar.
- No se ejecuta push desde Terminal.
- Publicación mediante GitHub Desktop.
- Vercel redesplegará automáticamente después del push.
