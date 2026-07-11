# Checklists

## Antes del commit

1. Ejecutar `git status`.
2. Confirmar que no aparezcan credenciales, `.env`, `__pycache__`, `.pyc` ni datos de usuarios.
3. Ejecutar `python -m pytest -q`.
4. Actualizar documentación si cambió el comportamiento.
5. Crear el commit.

## Antes del push a main

1. Confirmar que el commit corresponde a una propuesta final.
2. Ejecutar `git status` y comprobar que no quedan cambios accidentales.
3. Ejecutar `git push origin main`.
4. Abrir GitHub → pestaña **Actions**.
5. Verificar que `NINIA verified backup` termine en verde.
6. Confirmar que el archivo aparece en Drive.

## Si el workflow aparece rojo

No volver a subir cambios a ciegas. Abrir el workflow, entrar al paso fallido y conservar el mensaje de error para diagnóstico.
