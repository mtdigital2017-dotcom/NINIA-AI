# NINIA-AI

Motor inteligente de NINIA v1.0.

## Propósito

Procesar documentos, construir objetos de conocimiento, exponerlos vía API y preparar la integración con NINIA-FRONTEND.

## Estructura

```text
NINIA-AI/
├── api/
├── engine/
├── knowledge/
├── pipelines/
├── tests/
├── docs/
├── scripts/
├── data/
└── requirements.txt
```

## Ejecutar API

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

## Endpoints iniciales

- `GET /health`
- `GET /knowledge?status=proposed`
- `POST /documents/process`
