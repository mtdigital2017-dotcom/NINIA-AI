# QA local — Runtime Guardian v1

- Fecha: Sat Jul 11 19:31:16 -05 2026
- Repositorio: /Users/mendozza/Documents/GitHub/NINIA-AI
- Respaldo preventivo: /Users/mendozza/Downloads/NINIA_BACKUPS/NINIA-AI_ANTES_RUNTIME_GUARDIAN_20260711_193112
- Resultado pytest: 0

## Salida
```text
................................                                         [100%]
=============================== warnings summary ===============================
api/main.py:56
  /Users/mendozza/Documents/GitHub/NINIA-AI/api/main.py:56: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

.venv/lib/python3.9/site-packages/fastapi/applications.py:4579
  /Users/mendozza/Documents/GitHub/NINIA-AI/.venv/lib/python3.9/site-packages/fastapi/applications.py:4579: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    return self.router.on_event(event_type)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
32 passed, 2 warnings in 1.41s
```
