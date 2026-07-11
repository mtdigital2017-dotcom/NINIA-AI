# DT Runtime v1 — Plan de integración

## Alcance
Este paquete añade memoria operativa, reconstrucción de contexto, control de duplicidad,
validación de consistencia y adaptación de instrucciones para una persona principiante.

## No modifica
- `api/`
- `engine/`
- `knowledge/`
- pruebas funcionales existentes
- historial `.git`

## Orden
1. Crear respaldo local automático.
2. Copiar `.gitignore`, `NINIA_OS`, `dt_runtime`, `scripts/ninia_dt.py` y la prueba del Runtime.
3. Eliminar únicamente cachés locales.
4. Ejecutar todas las pruebas.
5. Generar reporte de instalación.
6. Dejar los cambios listos para revisión; no hacer commit automáticamente.
