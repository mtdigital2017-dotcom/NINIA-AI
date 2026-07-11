# QA local — Memory Manager v1

- Fecha: Sat Jul 11 17:07:24 -05 2026
- Repositorio: /Users/mendozza/Documents/GitHub/NINIA-AI
- Entorno virtual: .venv
- Respaldo: /Users/mendozza/Downloads/NINIA_BACKUPS/NINIA-AI_ANTES_MEMORY_MANAGER_20260711_170706
- Resultado pytest: 2

## Salida
```text

==================================== ERRORS ====================================
____________________ ERROR collecting tests/test_engine.py _____________________
tests/test_engine.py:2: in <module>
    from engine.ninia_engine import NiniaEngine
engine/ninia_engine.py:8: in <module>
    class NiniaEngine:
engine/ninia_engine.py:56: in NiniaEngine
    def __init__(self, base_dir: Path | str | None = None):
E   TypeError: unsupported operand type(s) for |: 'type' and 'type'
_________ ERROR collecting tests/test_existing_document_processing.py __________
tests/test_existing_document_processing.py:3: in <module>
    from engine.ninia_engine import NiniaEngine
engine/ninia_engine.py:8: in <module>
    class NiniaEngine:
engine/ninia_engine.py:56: in NiniaEngine
    def __init__(self, base_dir: Path | str | None = None):
E   TypeError: unsupported operand type(s) for |: 'type' and 'type'
=========================== short test summary info ============================
ERROR tests/test_engine.py - TypeError: unsupported operand type(s) for |: 't...
ERROR tests/test_existing_document_processing.py - TypeError: unsupported ope...
!!!!!!!!!!!!!!!!!!! Interrupted: 2 errors during collection !!!!!!!!!!!!!!!!!!!!
2 errors in 0.16s
```
