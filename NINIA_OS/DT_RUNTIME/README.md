# NINIA DT Runtime

Memoria operativa estructurada y agentes internos para evitar repetición y reproceso.

## Agentes internos

- **Memory Curator:** carga la fuente de verdad estructurada.
- **Context Builder:** reconstruye el contexto actual.
- **DT Guardian:** bloquea propuestas repetidas o afectadas por conflictos abiertos.
- **QA Architect:** valida consistencia y existencia de módulos.
- **Learning Advisor:** limita y adapta las acciones manuales al nivel principiante.

No son GPTs separados. Son componentes Python coordinados por `DTRuntimeOrchestrator`.

## Uso

```bash
python3 scripts/ninia_dt.py refresh
python3 scripts/ninia_dt.py status
python3 scripts/ninia_dt.py review "texto de una propuesta"
```

`current_context.json` se regenera con información verificable del repositorio.
