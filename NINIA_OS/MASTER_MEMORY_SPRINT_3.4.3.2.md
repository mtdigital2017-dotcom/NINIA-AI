# MASTER MEMORY — SPRINT 3.4.3.2

## Estado
PENDIENTE_REVISION_DT

## Objetivo
Corregir el error `FUNCTION_INVOCATION_FAILED` del backend FastAPI en Vercel.

## Diagnóstico
- La función llega a ejecutarse, pero falla con HTTP 500.
- El backend crea carpetas y archivos durante el arranque.
- En Vercel, el código desplegado es de solo lectura.
- Las escrituras operativas deben realizarse en `/tmp`.

## Corrección aplicada
- En Vercel, NINIA crea un workspace en `/tmp/ninia_runtime`.
- Se copian allí memoria, datos, conocimiento, operaciones y módulos requeridos.
- En local y Colab, el comportamiento anterior se conserva.

## Validación
- Suite completa de pytest.
- Importación local.
- Simulación con `VERCEL=1`.
- Pruebas de `/`, `/health` y `/openapi.json`.

## Gobierno
- No se modifica GitHub.
- No se hace commit ni push.
- El ZIP requiere revisión DT.

## Siguiente paso
Enviar `NINIA_RESULTADO_COLAB_SPRINT_3.4.3.2.zip` a NINIA CORE.
