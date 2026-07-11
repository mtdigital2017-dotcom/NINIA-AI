# Arquitectura vigente

```text
Desarrollador principiante
        |
        | git push a main
        v
GitHub
  |-- pruebas automáticas
  |-- construcción de paquete
  |-- manifiesto + SHA-256
  v
Google Drive API
  |-- carga del ZIP
  |-- lectura de metadatos
  |-- comparación MD5 local/remoto
  v
Respaldo verificado o workflow fallido
```

## Fuentes de verdad

- Código y documentación viva: GitHub.
- Respaldo histórico de entregas: Google Drive.
- Continuidad técnica: `NINIA_OS/`.
- Evidencia aprobada: repositorio de conocimiento, siempre con validación humana.

## Seguridad

Las credenciales de Google nunca se guardan en el repositorio. Se almacenan como GitHub Secrets y solo se inyectan durante el workflow.
