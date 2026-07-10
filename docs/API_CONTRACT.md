# NINIA-AI API Contract

## Base local

```text
http://localhost:8000
```

## Endpoints

### GET /health

Verifica que la API está activa.

### GET /knowledge?status=proposed

Lista objetos de conocimiento por estado.

### POST /documents/process

Procesa PDF, DOCX o TXT.

Campos:

- `file`
- `title`
- `source_entity`
- `source_url_or_doi`

Todo documento entra en estado `PROPUESTO`.
