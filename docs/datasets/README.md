# MarineShield Datasets Manifest & Data Governance

This directory contains authoritative specifications, registries, manifests, and partitioning guidelines for raw, preprocessed, and evaluation datasets used across MarineShield subsystems.

## Approved Baseline Datasets Catalog

| Dataset ID | Name | Role / Subsystem | Size / Scope | Status | Specification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DARTIS-2019-v1.0` | **DARTIS 2019** (PANGAEA.980773) | Primary Baseline for Oil Segmentation (Module B) & Look-Alike Classifier (Module C) | 3,655 Sentinel-1 $512\times 512$ patches (1,365 Oil, 2,290 Look-Alikes) | `APPROVED BASELINE` | [`DARTIS_DATASET_SPECIFICATION.md`](file:///d:/MarineShield/MarineShield/docs/datasets/DARTIS_DATASET_SPECIFICATION.md) |
| `HRSID-v1.0` | **HRSID** (High-Resolution SAR Images) | SAR Ship Detection Benchmark (Module E) for AIS-SAR Reconciliation | 5,604 images (14,598 ships) | `APPROVED CANDIDATE` | *In Registry* |
| `HIST-BENCH-v1.0` | **MarineShield Historical Benchmark Incidents** | Historical Incident Time Machine Replay & No-Hindsight Evaluation | Mauritius (*Wakashio* 2020), Ennore (2017), Mumbai (2010) | `APPROVED BENCHMARK` | *In Registry* |

## Machine-Readable Registries
- [`DATASET_REGISTRY.json`](file:///d:/MarineShield/MarineShield/docs/datasets/DATASET_REGISTRY.json) — Formal catalog conforming to [`docs/ml/OIL_INTELLIGENCE_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/ml/OIL_INTELLIGENCE_CONTRACTS.md) §4 (`DatasetVersion` schema).

## Data Governance & Leakage Prevention Rules
1. **Zero Raw Dataset Mutation**: Raw download archives in `data/raw/` are held strictly read-only.
2. **Scene-Level Disjoint Splitting**: To eliminate spatial and oceanographic autocorrelation leakage, all $512\times 512$ tiles cropped from the same Parent Sentinel-1 SAR Scene ID are assigned exclusively to a single split (`train`, `val`, or `test`).
3. **No-Hindsight Temporal Slicing**: Replay and validation sets strictly enforce $t \le t_{obs}$ in accordance with [`docs/testing/DEFINITION_OF_DONE.md`](file:///d:/MarineShield/MarineShield/docs/testing/DEFINITION_OF_DONE.md).

