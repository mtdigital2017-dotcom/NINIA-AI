# Estado actual de NINIA-AI

## Funciona

- Procesamiento de TXT, PDF y DOCX.
- Creación de objetos de conocimiento.
- Persistencia por estados.
- Admisión de evidencia en cuarentena.
- Detección de duplicados mediante SHA-256.
- Transiciones controladas de revisión.
- API y pruebas automatizadas.

## Incorporado en esta entrega

- Memoria operativa `NINIA_OS`.
- Política de respaldo automático.
- Script de empaquetado reproducible.
- Script de subida y verificación en Google Drive.
- GitHub Actions para pruebas y respaldo.
- Exclusión de cachés, secretos y datos operativos.

## Pendiente de configuración

- Crear o seleccionar una Unidad compartida de Google Drive.
- Crear una cuenta de servicio en Google Cloud.
- Compartir la carpeta de respaldo con la cuenta de servicio.
- Registrar secretos en GitHub.
- Ejecutar el workflow de prueba.
