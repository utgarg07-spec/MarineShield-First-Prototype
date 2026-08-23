# MarineShield Phase 6 — Partial Investigation Determinism Report

**Execution Timestamp:** 2026-08-21T19:25:23Z  
**Operating Mode:** `MODE A — PARTIAL_INTEGRATION_NO_ENVIRONMENT`  
**Target Incident ID:** `phase6-val-inc-20260821-001`  

---

## 1. Determinism Verification Table

| Attribute / Component | Run 1 Value | Run 2 Value | Match Status | Numerical Delta |
| :--- | :--- | :--- | :---: | :---: |
| **Attribution Status** | `SOURCE_UNKNOWN` | `SOURCE_UNKNOWN` | **EXACT MATCH** | 0.0 |
| **Unknown Trigger Reason** | `PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED` | `PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED` | **EXACT MATCH** | 0.0 |
| **Accepted AIS Obs Count** | `3` | `3` | **EXACT MATCH** | 0.0 |
| **Excluded Future Obs Count**| `2` | `2` | **EXACT MATCH** | 0.0 |
| **Vessel Matches Count** | `1` | `1` | **EXACT MATCH** | 0.0 |
| **Unmatched Dark Vessels** | `1` | `1` | **EXACT MATCH** | 0.0 |
| **Release Region Status** | `UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY` | `UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY` | **EXACT MATCH** | 0.0 |
| **Source Ranking Status** | `NOT_COMPUTED` | `NOT_COMPUTED` | **EXACT MATCH** | 0.0 |
| **Payload JSON SHA-256** | `5bad6701bc5c8800c1b956ac92d4616ce5b0c5eaaff91bda46ba4a373d5372f8` | `5bad6701bc5c8800c1b956ac92d4616ce5b0c5eaaff91bda46ba4a373d5372f8` | **BIT-EXACT** | 0.0 |

---

## 2. Determinism Conclusion
The partial investigation pipeline is **100% mathematically deterministic** across consecutive executions.
