# Backup Manager v1.1

Estado: VALIDADO EN ENTORNO AISLADO.

## Garantías
- Excluye `.git`, `.venv`, cachés y archivos `.pyc`.
- Rechaza el backup si detecta archivos prohibidos.
- Verifica SHA-256.
- Compara el manifiesto contra el contenido real del ZIP.
- Valida restauración antes de aprobación.
