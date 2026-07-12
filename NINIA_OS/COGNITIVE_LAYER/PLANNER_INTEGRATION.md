# Integración automática del Planner v1

## Flujo

`Memory Manager → Decision Engine → Planner → traza → API`

## Comportamiento

`ExecutiveController.process()` genera automáticamente:

1. un plan de decisión;
2. un plan de ejecución estructurado;
3. una traza con ambos resultados.

El endpoint `POST /dt/plan` devuelve ambos planes.

## Límite

El Planner organiza tareas, pero no las ejecuta. La ejecución autónoma
queda fuera de este segmento.
