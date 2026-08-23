# MarineShield Phase 7 — Segmentation Evaluation Determinism Report

**Execution Timestamp:** 2026-08-21T19:34:17Z  
**Hardware Environment:** NVIDIA GeForce RTX 3050 6GB Laptop GPU (cuda)  
**Determinism Status:** **`PASS — 100% BIT-EXACT MATCH`**  

---

## 1. Determinism Verification Summary

| Model Evaluated | Run 1 Macro IoU | Run 2 Macro IoU | Run 1 Macro Dice | Run 2 Macro Dice | Prediction Hash Status | Pass / Fail |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Production SAR-Adapted SAM** | `0.652041` | `0.652041` | `0.707753` | `0.707753` | **BIT-EXACT MATCH** | **PASS** |
| **Vanilla SAM ViT-B Baseline** | `0.493091` | `0.493091` | `0.496516` | `0.496516` | **BIT-EXACT MATCH** | **PASS** |

---

## 2. Conclusion
Both evaluation runs produced bit-exact prediction masks and identical floating-point metric tables. Zero precision drift was detected.
