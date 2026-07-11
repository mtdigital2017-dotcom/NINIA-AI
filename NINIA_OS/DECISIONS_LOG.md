# Registro de decisiones técnicas

## DT-001 — Memoria dentro del repositorio

- Fecha: 2026-07-11
- Estado: APROBADA
- Decisión: mantener `NINIA_OS` como memoria operativa versionada.
- Motivo: evitar dependencia de conversaciones o memoria temporal.

## DT-002 — Doble respaldo

- Fecha: 2026-07-11
- Estado: APROBADA
- Decisión: GitHub será la fuente oficial y Google Drive el respaldo automático verificado.
- Motivo: continuidad, trazabilidad y recuperación.

## DT-003 — Una acción humana

- Fecha: 2026-07-11
- Estado: APROBADA
- Decisión: la acción normal del usuario será `git push` a `main`; las pruebas, el empaquetado, la carga y la verificación serán automáticos.

## DT-004 — Cuenta de servicio y Unidad compartida

- Fecha: 2026-07-11
- Estado: APROBADA CON PRERREQUISITO
- Decisión: usar Google Drive API con cuenta de servicio y carpeta ubicada en una Unidad compartida.
- Motivo: autenticación no interactiva y respaldo estable desde GitHub Actions.
- Prerrequisito: acceso a Google Workspace con Unidad compartida. Para Drive personal se requerirá un flujo OAuth distinto.
