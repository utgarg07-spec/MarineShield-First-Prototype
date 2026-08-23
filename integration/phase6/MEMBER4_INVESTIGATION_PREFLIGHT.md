# MarineShield Phase 6 — Member 4 Investigation Preflight Validation Report

**Preflight Date (UTC):** 2026-08-21T17:35:00Z  
**Role:** MarineShield Integration Validator (Member 4 Investigation Workstream)  
**Execution Objective:** Preflight readiness and input compatibility audit for the Release Reconstruction and Source-Investigation Engine prior to Phase 6 live run.  

---

## 1. Executive Preflight Assessment

The preflight audit evaluated the availability, schema compatibility, temporal consistency, geodetic precision, and provenance of all four prerequisite inputs required for the Member 4 investigation run:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        PREFLIGHT INPUT PREREQUISITE AUDIT                              │
├────────────────────────────────┬──────────────────────────┬────────────────────────────┤
│ 1. Verified Spill Polygon      │ LOOKALIKE / NO SPILL     │ BLOCKED ON DEMO SCENE      │
├────────────────────────────────┼──────────────────────────┼────────────────────────────┤
│ 2. Spill Timestamp             │ 2024-01-20T00:55:41Z     │ VERIFIED                   │
├────────────────────────────────┼──────────────────────────┼────────────────────────────┤
│ 3. Person 2 Vessel Output      │ MOCK_HYBRID (2024-01-20) │ ADAPTER REQUIRED           │
├────────────────────────────────┼──────────────────────────┼────────────────────────────┤
│ 4. Historical MetOcean Data    │ NOT PROVIDED (MEMBER 5)  │ BLOCKED — MISSING DATA     │
└────────────────────────────────┴──────────────────────────┴────────────────────────────┘
```

**Preflight Status:** **`BLOCKED — ENVIRONMENTAL HISTORY MISSING`** (and missing vessel adapter bridge).

---

## 2. Inventory of Required Investigation Components & Exact Paths

| Item | Component Description | Exact Repository Path | Verified Status |
| :--- | :--- | :--- | :---: |
| **1. Verified Spill Polygon** | Spatial polygon geometry (`EPSG:4326` GeoJSON) | `integration/phase6/oil_intelligence/spill_detection_run1.json` | **NO SPILL GEOMETRY** (Tile was clean water / `LOOKALIKE_REJECTED`) |
| **2. Spill Timestamp** | Observation timestamp $t_{obs}$ | `response_of_person2_member1/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_metadata.json` | **VERIFIED** (`2024-01-20T00:55:41.203509Z`) |
| **3. Vessel Observations** | Candidate AIS tracks, SAR detections, anomalies | `response_of_person2_member3/vessel_demonstration_results.json` | **AVAILABLE (MOCK_HYBRID)** |
| **4. Vessel Adapter Bridge** | Schema transformer from Member 3 JSON $\to$ Member 4 `VesselObservation` | Expected at `marineshield/adapters/vessel_adapter.py` | **MISSING — NOT CREATED** |
| **5. Investigation Engine** | Central pipeline orchestrator | `marineshield/investigation/engine.py` (`SourceInvestigationEngine`) | **VERIFIED & OPERATIONAL** |
| **6. Investigation Contract** | Canonical domain contracts | `docs/api/INVESTIGATION_CONTRACTS.md` & `marineshield/investigation/schemas.py` | **VERIFIED (Complete)** |
| **7. Env History Contract** | Canonical MetOcean input schema | `marineshield/investigation/schemas.py` (`EnvironmentalHistory`) | **VERIFIED (Complete)** |
| **8. Env History Data/Fixture**| Historical ERA5 wind / HYCOM current for 2024-01-20 | Expected in `data/handoff_samples/forecast/` | **MISSING — NOT PROVIDED** |

---

## 3. Detailed Input-by-Input Evaluation

### 3.1 Input 1: Verified Spill Polygon
- **File Path:** `integration/phase6/oil_intelligence/spill_detection_run1.json`
- **Schema:** `SpillGeometryContract` (`docs/ml/OIL_INTELLIGENCE_CONTRACTS.md` §7)
- **Data Mode:** Real Sentinel-1 SAR acquisition (`S1A_IW_GRDH_1SDV_20240120...`)
- **Timestamp Format:** ISO 8601 UTC (`2024-01-20T00:55:41.203509Z`)
- **CRS & Coordinate Order:** `EPSG:4326` `[longitude, latitude]`
- **Audit Finding:** The approved demonstration SAR tile (`r000_c000_train`) was evaluated by the Member 2 Oil Intelligence service and classified as `LOW_WIND_AREA` (`LOOKALIKE_REJECTED`) with `spill_geometry: null`. Because the tile contains zero detected oil pixels, backward release reconstruction cannot be initiated on this specific tile without a verified slick polygon centroid $[lon, lat]$.

---

### 3.2 Input 2: Spill Observation Timestamp
- **File Path:** `response_of_person2_member1/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_metadata.json`
- **Schema:** `marineshield.sar.v1` (`acquisition_time.center_time`)
- **Data Mode:** Cached Real Sentinel-1 Scene
- **Timestamp Format:** ISO 8601 UTC (`2024-01-20T00:55:41.203509Z`)
- **Audit Finding:** Fully verified and compliant.

---

### 3.3 Input 3: Person 2 Vessel Observations
- **File Path:** `response_of_person2_member3/vessel_demonstration_results.json`
- **Schema:** `VESSEL_DATA_CONTRACT.md`
- **Data Mode:** **`MOCK_HYBRID`** (Simulated candidate transponders matching real SAR scene coordinates)
- **Timestamp Format:** ISO 8601 UTC (`2024-01-19T19:55:00.000Z` to `2024-01-20T01:55:00.000Z`)
- **CRS & Coordinate Order:** `EPSG:4326` `[longitude, latitude]`
- **Provenance:** `demo_run_dff3e36e4f111353`
- **Temporal Consistency Audit (No-Hindsight Rule):**
  - Observation `240cdb8f-9884-4852-9d71-4ee53d5efe63` (MMSI `413987654`) has timestamp `2024-01-20T01:55:00.000Z`, which is **59 minutes AFTER** the satellite observation timestamp (`00:55:41Z`).
  - **Constraint:** In accordance with `.agents/rules/testing_rules.md` (No-Hindsight Rule), any observations with $t > t_{obs}$ must be filtered out prior to release reconstruction and evidence scoring.

---

### 3.4 Input 4: Historical Environmental Conditions (MetOcean)
- **File Path:** Expected in `data/handoff_samples/forecast/` or `response_of_person2_member3/`
- **Schema:** `marineshield.investigation.schemas.EnvironmentalHistory`
- **Data Mode:** **NOT PROVIDED (MISSING)**
- **Audit Finding:** Person 3 (Member 5) has not yet delivered the historical ERA5 10m wind vector or HYCOM surface ocean current vector for the Arabian Sea on `2024-01-20`.
- **Constraint Enforcement:** Per task directives:
  - *Do NOT invent environmental history.*
  - *Do NOT substitute current weather for historical environmental data.*
  - The absence of calibrated historical MetOcean data is a **hard blocker** for running the release reconstruction engine on the 2024 demonstration incident.

---

## 4. Vessel-to-Investigation Schema Mapping Gap Analysis

Member 3's demonstration JSON (`vessel_demonstration_results.json`) uses a different structural hierarchy than Member 4's `SourceInvestigationEngine`:

```
Member 3 Output (vessel_demonstration_results.json)
  ├── matches: List[VesselMatch]
  ├── unmatched_detections: List[UnmatchedVessel]
  ├── behavior_features.anomalies_detected: List[AnomalyEvent]
  └── ais_candidates: List[AISObservation]
            │
            ▼ (MISSING ADAPTER BRIDGE)
Member 4 Input (marineshield.investigation.schemas)
  └── vessel_observations: List[VesselObservation]
        ├── vessel_id, vessel_name, vessel_mmsi, vessel_type
        ├── source_type: "AIS_TRACK" | "SAR_DETECTION"
        ├── track_points: [{"lon", "lat", "timestamp_utc", "speed_knots"}]
        ├── has_ais_gap: bool
        └── speed_drop_knots: float
```

### Required Transformation Logic (To be implemented when unblocked):
1. **Matched Vessels (`matches`):** Extract MMSI $\to$ match with `ais_candidates` $\to$ construct `VesselObservation(source_type="AIS_TRACK", vessel_mmsi=..., track_points=...)`.
2. **Unmatched Dark Vessels (`unmatched_detections`):** Construct `VesselObservation(source_type="SAR_DETECTION", sar_vessel_detection_id=..., estimated_length_m=...)`.
3. **Anomalies (`behavior_features`):** Correlate `AnomalyEvent` per MMSI:
   - If `AIS_TRANSMISSION_GAP` $\implies$ set `has_ais_gap = True`.
   - If `ABNORMAL_SPEED_DROP` $\implies$ calculate `speed_drop_knots = initial_speed - final_speed`.

---

## 5. Preflight Conclusion & Next Actions

- **Overall Preflight Status:** **`BLOCKED — ENVIRONMENTAL HISTORY MISSING`**
- **Action Required to Unblock:**
  1. Member 5 (Person 3) must provide the historical MetOcean dataset (ERA5 wind speed/direction and HYCOM current vectors $u, v$) for the Arabian Sea coordinate envelope on `2024-01-20`.
  2. Implement the `vessel_to_investigation_adapter` bridge.
  3. Provide a validated oil-slick centroid from Member 2 for the demonstration scene or execute under a controlled synthetic fixture.
