---
trigger: always_on
---

# MarineShield Testing & Evaluation Rules

## 1. Test Suite Organization
Tests must be organized under `tests/` or module-specific `tests/` directories:
- `tests/unit/`: Unit tests for individual functions, geometric metrics, API schema validations, evidence score calculations.
- `tests/integration/`: End-to-end flow tests verifying API endpoints, PostGIS spatial queries, drift model wrapper calls.
- `tests/evaluation/`: Pipeline benchmarks evaluated on historical incident datasets.

## 2. Quantitative Evaluation Criteria
Subsystems must be evaluated using standard metrics defined in [`docs/testing/DEFINITION_OF_DONE.md`](file:///d:/MarineShield/MarineShield/docs/testing/DEFINITION_OF_DONE.md):
- **Oil Segmentation**: Intersection over Union (IoU), F1/Dice Score, False Positive Rate (FPR).
- **Vessel Detection**: Precision, Recall, Mean Average Precision (mAP).
- **Source Attribution**: Top-1 Accuracy, Top-3 Accuracy, Mean Reciprocal Rank (MRR) where ground truth exists.
- **Drift Forecasting**: Spatial trajectory displacement error (km), polygon overlap percentage.

## 3. Historical Replay Validation (No-Hindsight Rule)
- Evaluation scripts for the **Historical Incident Time Machine** must strictly enforce temporal slicing (`t <= t_observation`).
- Tests must verify that no future AIS data, weather data, or satellite scenes leak into historic incident evaluation pipelines.
