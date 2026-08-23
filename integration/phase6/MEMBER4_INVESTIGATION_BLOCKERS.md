# MarineShield Phase 6 — Member 4 Investigation Blockers Report

**Date (UTC):** 2026-08-21T17:35:00Z  
**Workstream:** Member 4 (Release Reconstruction & Source Attribution)  
**Status:** **RUN BLOCKED**  

---

## 1. Summary of Identified Blockers

The Member 4 Release Reconstruction and Source-Investigation Engine cannot be executed on the 2024 demonstration incident due to **3 hard blockers** and **1 data hygiene requirement**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               IDENTIFIED BLOCKERS                                      │
├───────────────────┬─────────────────────────────────────────────────┬──────────────────┤
│ BLOCKER 1         │ Historical MetOcean Environmental Data Missing  │ HARD BLOCKER     │
├───────────────────┼─────────────────────────────────────────────────┼──────────────────┤
│ BLOCKER 2         │ Vessel-to-Investigation Adapter Bridge Missing  │ INTEGRATION GAP  │
├───────────────────┼─────────────────────────────────────────────────┼──────────────────┤
│ BLOCKER 3         │ Demonstration SAR Tile Contains Zero Oil Pixels │ DATA STATE       │
├───────────────────┼─────────────────────────────────────────────────┼──────────────────┤
│ REQUIREMENT 4     │ Temporal Slicing Needed for Future AIS Track    │ NO-HINDSIGHT     │
└───────────────────┴─────────────────────────────────────────────────┴──────────────────┘
```

---

## 2. Detailed Blocker Analysis

---

### Blocker 1: Historical MetOcean Environmental Data Missing (Member 5)
- **Severity:** **`HARD BLOCKER`**
- **Description:** The Member 4 Lagrangian backward drift reconstruction engine requires historical meteorological (ERA5 10m wind speed and direction) and oceanographic (HYCOM/CMEMS surface current $u, v$ vectors) forcing data over the lookback window $[t_{obs} - 6\text{h}, t_{obs}]$ (`2024-01-19T18:55:00Z` to `2024-01-20T00:55:41Z`).
- **Audit Finding:** No environmental dataset, NetCDF file, or JSON fixture exists in `data/handoff_samples/forecast/` or `response_of_person2_member3/` for `2024-01-20`.
- **Governing Directives:**
  - *Do NOT invent environmental history.*
  - *Do NOT substitute current weather for historical environmental data.*
- **Action Required to Resolve:** Person 3 (Member 5) must supply the verified ERA5/HYCOM historical MetOcean forcing parameters for the Arabian Sea coordinate bounding box on `2024-01-20`.

---

### Blocker 2: Vessel-to-Investigation Adapter Bridge Missing
- **Severity:** **`INTEGRATION GAP`**
- **Description:** Member 3's output deliverable (`response_of_person2_member3/vessel_demonstration_results.json`) uses a dictionary hierarchy (`matches`, `unmatched_detections`, `behavior_features.anomalies_detected`), while Member 4's `SourceInvestigationEngine` consumes `VesselObservation` dataclass instances.
- **Audit Finding:** No adapter module (`marineshield/adapters/vessel_adapter.py`) currently exists to transform Member 3's schema into Member 4's schema.
- **Action Required to Resolve:** Author the `vessel_to_investigation_adapter` module after Person 1 approves the interface mapping.

---

### Blocker 3: Demonstration SAR Tile Contains Look-Alike / Zero Oil Pixels
- **Severity:** **`DATA STATE`**
- **Description:** The approved demonstration SAR tile (`r000_c000_train` from `S1A_IW_GRDH_1SDV_20240120...`) was processed by the Oil Intelligence Service and correctly classified as `LOW_WIND_AREA` (`LOOKALIKE_REJECTED`), producing `spill_geometry: null`.
- **Audit Finding:** Without a detected oil slick centroid $[lon, lat]$, backward drift integration cannot calculate an origin release envelope for this specific tile.
- **Action Required to Resolve:** To demonstrate release reconstruction, either a tile containing a confirmed oil detection must be supplied, or the run must be executed against a controlled synthetic fixture (e.g. `tests/fixtures/investigation/01_single_dominant_candidate.json`).

---

### Requirement 4: Temporal Slicing of Future AIS Track Points (No-Hindsight Rule)
- **Severity:** **`DATA HYGIENE / RULE ENFORCEMENT`**
- **Description:** In `response_of_person2_member3/vessel_demonstration_results.json`, observation `240cdb8f-9884-4852-9d71-4ee53d5efe63` (MMSI `413987654`) has timestamp `2024-01-20T01:55:00.000Z`, which occurred **59 minutes AFTER** the satellite observation timestamp (`2024-01-20T00:55:41Z`).
- **Rule:** In accordance with `.agents/rules/testing_rules.md` (No-Hindsight Rule), future observations must not leak into historic incident evaluation pipelines.
- **Action Required:** The vessel adapter must strictly filter out all track points with $t > t_{obs}$.

---

## 3. Final Preflight Determination

**PREFLIGHT STATUS:** **`BLOCKED — ENVIRONMENTAL HISTORY MISSING`**

The release reconstruction and source-investigation engine will **NOT** be executed until calibrated MetOcean environmental data is supplied by Member 5 and the adapter bridge is approved by Person 1.
