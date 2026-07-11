# NINIA-AI v1.0.3 — Evidence Admission

Se conservan los endpoints existentes:

- `GET /health`
- `GET /knowledge`
- `POST /documents/process`

Se agregan:

- `GET /researcher/specialties`
- `POST /evidence/requests`
- `GET /evidence/requests`
- `GET /evidence/requests/{id}`
- `PATCH /evidence/requests/{id}/status`

Todo documento nuevo inicia en `CUARENTENA`.
La aprobación directa desde `CUARENTENA` está bloqueada.
