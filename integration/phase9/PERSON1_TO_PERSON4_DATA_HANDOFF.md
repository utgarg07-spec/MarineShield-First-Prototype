# MarineShield Phase 9 — Person 1 to Person 4 Data Handoff Document

**Handoff Date (UTC):** 2026-08-22T01:30:00Z  
**From:** Person 1 (Member 2 Oil Intelligence & Member 4 Source Investigation)  
**To:** Person 4 (Member 6 Frontend / WebGIS Command Center UI & WebGIS Handoff)  
**Handoff Status:** **`PERSON 1 DATA HANDOFF READY FOR PERSON 4`**  

---

## 1. Data Handoff Compatibility Matrix

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     PERSON 1 TO PERSON 4 DATA COMPATIBILITY MATRIX                     │
├──────────────────────────────────┬──────────────────────────┬──────────────────────────┤
│ Data Layer / Subsystem           │ API Contract Endpoint    │ Person 4 Handoff Status  │
├──────────────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 1. Oil & Look-Alike Intelligence │ /api/v1/oil-intelligence │ ✔️ FULLY COMPATIBLE      │
├──────────────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 2. Release Reconstruction        │ /api/v1/investigation    │ ⚠️ MODE A (NO METOCEAN)  │
├──────────────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 3. Source Attribution & Ranking  │ /api/v1/investigation    │ ✔️ COMPATIBLE (UNKNOWN)  │
├──────────────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 4. Counterfactual Attribution    │ /api/v1/counterfactual   │ ✔️ FULLY COMPATIBLE      │
├──────────────────────────────────┼──────────────────────────┼──────────────────────────┤
│ 5. Historical Replay Mechanism   │ /api/v1/replay           │ ✔️ LEAK_FREE_VERIFIED    │
└──────────────────────────────────┴──────────────────────────┴──────────────────────────┘
```

---

## 2. Detailed Compatibility Breakdown

### 2.1 Fields Already Fully Compatible
1. **Oil Intelligence Payload:** `incident_id`, `tile_id`, `sar_granule_id`, `status` (`OIL_DETECTED | LOOKALIKE_REJECTED | UNCERTAIN_ANALYSIS`), `lookalike_verification` class probabilities (`LOW_WIND_AREA`, `BIOGENIC_SLICK`, etc.), Shannon entropy, confidence margin, `spill_geometry` GeoJSON in `EPSG:4326`, `severity` tier (`UNKNOWN`, `MINOR`, etc.), `data_quality_index`, and `provenance` block.
2. **Investigation & Ranking Payload:** `incident_id`, `mode`, `investigation_timestamp_utc`, `attribution_status` (`ATTRIBUTED_CANDIDATES_EVALUATED`, `SOURCE_UNKNOWN`), `evaluated_candidates` (component scores $0-100$, supporting/contradictory evidence lists), and `non_guilt_clause`.
3. **Counterfactual Sensitivity Payload:** `status` (`SUCCESS`, `NOT_APPLICABLE`, `BLOCKED_TIE_POLICY_REQUIRED`), `removed_candidate_id`, `is_top_hypothesis_dominant`, `rank_changes` before/after table.

---

### 2.2 Fields Missing from the API (Pending Downstream Member Workstreams)
- **Person 3 MetOcean ERA5 Wind & HYCOM Current Vectors:** Currently represented as `UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY` and `UnavailableEnvironmentalHistoryProvider` in Mode A. Full advection drift display will activate in Mode B when Member 5 delivers the MetOcean provider.

---

### 2.3 Fields Expected by Frontend But Explicitly NOT Provided (Non-Claims)
1. **Estimated Oil Volume in Tonnes / Litres:** Person 1 explicitly does **NOT** compute or expose oil volume from SAR backscatter intensity alone.
2. **Legal Guilt Declarations or MARPOL Fine Calculations:** Person 1 explicitly outputs empirical evidence compatibility scores ($0-100$), **NOT** legal guilt declarations.

---

### 2.4 Fields That MUST NOT Be Exposed to Frontend
- Raw PyTorch tensor arrays, model weights (`.pth` bytes), internal CUDA memory pointers, or uncalibrated float matrices.

---

### 2.5 Coordinate, Timestamp, and Provenance Rules
- **Coordinate Reference System:** `EPSG:4326` (WGS84 2D Geographic).
- **Coordinate Order:** `[longitude, latitude]` (Standard GeoJSON format).
- **Timestamp Standard:** ISO 8601 UTC string (`YYYY-MM-DDTHH:MM:SSZ`).
- **Provenance Standard:** All response objects include `provenance` metadata.

---

## 3. Handoff Conclusion

Person 1's backend services and data contracts are 100% ready for Person 4 to connect WebGIS map layers, candidate inspection drawers, and counterfactual sensitivity cards.
