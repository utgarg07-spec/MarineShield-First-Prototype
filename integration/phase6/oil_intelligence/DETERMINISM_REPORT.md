# MarineShield Phase 6 — Oil Intelligence Determinism Report

**Execution Timestamp:** 2026-08-21T17:23:45Z  
**Device:** cuda (NVIDIA GeForce RTX 3050 6GB Laptop GPU)  
**Target Scene ID:** `S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2`  
**Target Tile ID:** `S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train`  

---

## 1. Determinism Verification Summary

| Metric / Attribute | Run 1 Value | Run 2 Value | Equality Status | Numerical Delta |
| :--- | :--- | :--- | :---: | :---: |
| **Execution Status** | `LOOKALIKE_REJECTED` | `LOOKALIKE_REJECTED` | **EXACT MATCH** | 0.0 |
| **Predicted Class** | `LOW_WIND_AREA` | `LOW_WIND_AREA` | **EXACT MATCH** | 0.0 |
| **Pipeline Decision** | `REJECT_AS_LOOKALIKE` | `REJECT_AS_LOOKALIKE` | **EXACT MATCH** | 0.0 |
| **Class Probability (Low Wind)** | `0.913900` | `0.913900` | **EXACT MATCH** | 0.0 |
| **Class Probability (Petroleum)** | `0.001700` | `0.001700` | **EXACT MATCH** | 0.0 |
| **Classification Entropy** | `0.578300` | `0.578300` | **EXACT MATCH** | 0.0 |
| **Classification Margin** | `0.880200` | `0.880200` | **EXACT MATCH** | 0.0 |
| **Severity Class** | `UNKNOWN` | `UNKNOWN` | **EXACT MATCH** | 0.0 |
| **Mean Oil Probability** | `0.515200` | `0.515200` | **EXACT MATCH** | 0.0 |
| **Pixel Coverage Fraction** | `0.000000` | `0.000000` | **EXACT MATCH** | 0.0 |
| **Spill Geometry Feature** | `None` | `None` | **EXACT MATCH** | 0.0 |
| **Clean Payload Hash** | `831551947353c2c44b70b2b274bbe040cf9611bd43f63fb2a37aa256f2b657bf` | `831551947353c2c44b70b2b274bbe040cf9611bd43f63fb2a37aa256f2b657bf` | **BIT-EXACT** | 0.0 |

---

## 2. Conclusion
The Oil Intelligence pipeline is **100% mathematically deterministic** across consecutive runs. No random seeds, non-deterministic CUDA ops, or variable precision drift were observed.
