# NINIA Sprint 3.0 — AI Trainer MVP v1

**Fecha:** 2026-07-14T03:37:23.027995+00:00
**Estado:** VALIDADO_EN_COLAB

## Objetivo

Entrenar el primer modelo reproducible de NINIA usando
exclusivamente datasets generados por EvidenceDatasetService.

## Implementación

- AITrainerService.
- Clasificador Multinomial Naive Bayes.
- Carga de train, validation y test.
- Validación obligatoria del dataset.
- Accuracy, macro precision, macro recall y macro F1.
- Matriz de confusión.
- Model Registry.
- Manifiesto de entrenamiento.
- Modelo persistido en JSON.

## Gobernanza

- No lee documentos originales.
- No lee Knowledge Objects.
- Solo acepta APPROVED_KNOWLEDGE_ONLY.
- No existe aprobación automática.
- No entrena cuando el dataset no está listo.
- Entrenamiento reproducible.

## Próximo sprint

Sprint 3.1 — Model Evaluation and Frontend Metrics.
