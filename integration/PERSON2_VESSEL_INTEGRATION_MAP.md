# MarineShield — Person 2 Member 3 Vessel Integration Map

**Document Generation Date:** 2026-08-21  
**Author:** MarineShield Integration Auditor  
**Domain:** Maritime Vessel & AIS Intelligence $\to$ Person 1 Source Attribution Engine  

---

## 1. End-to-End Pipeline Overview

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     MEMBER 3 (PERSON 2)                                          │
│                                                                                                  │
│   Raw GFW / AIS Feed ──► VesselParser ──► Normalized Observations ──► Spatio-Temporal Filter     │
│                                                                                │                 │
│   SAR Ship Detections (M2) ───────────────────────────────────────────────────►│                 │
│                                                                                ▼                 │
│   Behavior Anomaly Engine ◄── AIS-SAR Reconciliation Matcher ◄─────────────────┘                 │
│              │                               │                                                   │
│              ▼                               ▼                                                   │
│      AnomalyEvent List             VesselMatch & UnmatchedVessel                                 │
└──────────────┬───────────────────────────────┬───────────────────────────────────────────────────┘
               │                               │
               ▼                               ▼ (Handoff Boundary)
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     MEMBER 4 (PERSON 1)                                          │
│                                                                                                  │
│   Candidate Vessel Filter ──► Deterministic Evidence Scoring ──► Source Hypothesis Ranking       │
│                                                                                │                 │
│   Canonical InvestigationResult Payload ◄── Counterfactual Margin & Unknown Gating ◄─────────────┘│
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Step-by-Step Integration Mapping

---

### Step 1: Raw GFW/AIS Feed & SAR Ship Detections $\to$ Normalized Observations

```
[Raw GFW/AIS API & SAR Radar Detections] ────► [VesselParser (vessel_parser.py)]
```

- **Producer:**
  1. Global Fishing Watch API v3 / MarineTraffic AIS feed (`response_of_person2_member3/gfw_client.py`).
  2. SAR Vessel Detection Engine from Member 2 (`SARVesselDetection` contract).
- **Consumer:** Vessel Parser & Contract Transformer (`response_of_person2_member3/vessel_parser.py`).
- **Input Format:** Raw API response JSON / dictionary dictionaries.
- **Output Format:** Canonical `Vessel`, `AISObservation`, and `SARVesselDetection` dictionaries conforming to `VESSEL_DATA_CONTRACT.md`.
- **Exact Fields Produced:**
  - `Vessel`: `vessel_id` (UUID), `mmsi` (9-digit string), `imo`, `vessel_name`, `ship_type`, `length_meters`, `beam_meters`, `flag_country`.
  - `AISObservation`: `observation_id`, `mmsi`, `timestamp` (ISO 8601 UTC), `latitude` $[-90.0, 90.0]$, `longitude` $[-180.0, 180.0]$, `speed_over_ground_knots`, `course_over_ground_deg`, `heading_deg`, `navigational_status`, `source_provider`.
  - `SARVesselDetection`: `detection_id`, `source_granule_id`, `detection_timestamp`, `centroid_lat`, `centroid_lon`, `estimated_length_meters`, `detection_confidence`, `geometry_geojson` (Point `[lon, lat]`).
- **Transformations Required:**
  1. MMSI sanitization (strip whitespace, ensure exactly 9 numeric digits).
  2. Timestamp normalization to strict ISO 8601 UTC string (`YYYY-MM-DDTHH:MM:SS.sssZ`).
  3. Ship type taxonomy mapping into 12 canonical enum values (`TANKER_CRUDE_OIL`, `CARGO_CONTAINER`, etc.).
- **Validation Required:**
  - Coordinate bounds checking: $-180.0 \le \text{lon} \le 180.0$, $-90.0 \le \text{lat} \le 90.0$.
  - MMSI format verification.
- **Test Proving Compatibility:** `response_of_person2_member3/test_vessel_data_contract.py`.
- **Unresolved Issue:** None.

---

### Step 2: Normalized Observations $\to$ Spatio-Temporal Filtering

```
[Normalized Observations] ────► [Spatio-Temporal Filter (intelligence_service.py)]
```

- **Producer:** `VesselParser`.
- **Consumer:** `VesselIntelligenceService.filter_observations_by_window` (`intelligence_service.py`).
- **Input Format:** List of `AISObservation` and `SARVesselDetection` entities, bounding box / polygon GeoJSON, start time $t_{start}$, end time $t_{end}$.
- **Output Format:** Pruned candidate subset containing only observations intersecting the spatial region within temporal lookback window $[t_{start}, t_{end}]$.
- **Exact Fields Processed:**
  - `timestamp`, `latitude`, `longitude`, `geojson_polygon`.
- **Transformations Required:**
  1. Temporal window intersection check ($t_{start} \le t_{obs} \le t_{end}$).
  2. Spatial bounding box containment filter.
- **Validation Required:** Ensure no observations outside temporal lookback window are passed downstream.
- **Test Proving Compatibility:** `response_of_person2_member3/test_vessel_intelligence.py`.
- **Unresolved Issue:** Complex polygon containment: Current implementation uses bounding-box approximation. Full ray-casting or PostGIS `ST_Contains` should be used when complex concave release polygons are supplied.

---

### Step 3: Candidate Observations $\to$ Deterministic AIS-SAR Reconciliation Matcher

```
[Filtered AIS & SAR Detections] ────► [Reconciliation Matcher (intelligence_service.py)]
```

- **Producer:** Spatio-temporal filter.
- **Consumer:** `VesselIntelligenceService.run_reconciliation` (`intelligence_service.py`).
- **Input Format:** Filtered `SARVesselDetection` list, `AISObservation` list, and `Vessel` metadata list.
- **Output Format:**
  1. `matches`: List of `VesselMatch` entities.
  2. `unmatched_detections`: List of `UnmatchedVessel` dark vessel entities.
- **Exact Fields in Output:**
  - `VesselMatch`: `match_id`, `sar_detection_id`, `matched_mmsi`, `match_status` (`MATCHED`), `match_confidence` ($0.0-1.0$), `distance_offset_meters`, `timestamp_offset_seconds`, `heading_delta_deg`, `speed_delta_knots`, `dimension_match_score`, `reconciliation_algorithm` (`DETERMINISTIC_SPATIO_TEMPORAL_HEURISTIC_V1`).
  - `UnmatchedVessel`: `unmatched_id`, `sar_detection_id`, `centroid_lat`, `centroid_lon`, `estimated_length_meters`, `detection_confidence`, `ais_search_radius_km`, `ais_time_window_minutes`, `dark_vessel_confidence`, `description`.
- **Transformations Required:**
  1. Geodesic distance computation via Haversine formula ($\Delta d \le 5000\text{ m}$).
  2. Temporal interpolation / offset check ($\Delta t \le 1800\text{ s}$).
  3. Kinematic scoring:
     $$S_{match} = 0.40 \cdot S_{distance} + 0.20 \cdot S_{time} + 0.20 \cdot S_{heading} + 0.20 \cdot S_{dimension}$$
  4. Matching threshold gating ($S_{match} \ge 0.70 \implies \text{MATCHED}$, else $\text{UNMATCHED}$).
- **Validation Required:**
  - Assert that any physically detected SAR target without a matching AIS track within search radius is classified as `UnmatchedVessel`.
  - Enforce responsible-AI non-accusation description text.
- **Test Proving Compatibility:** `response_of_person2_member3/test_vessel_intelligence.py::test_run_reconciliation_matched_and_unmatched`.
- **Unresolved Issue:** None. Matching heuristic is 100% deterministic.

---

### Step 4: AIS Trajectories $\to$ Behavior Anomaly Engine

```
[AIS Trajectories] ────► [Anomaly Detector (intelligence_service.py)]
```

- **Producer:** AIS Observation historical stream.
- **Consumer:** `VesselIntelligenceService.detect_behavioral_anomalies` (`intelligence_service.py`).
- **Input Format:** Grouped AIS observations sorted chronologically per MMSI.
- **Output Format:** List of `AnomalyEvent` entities.
- **Exact Fields Produced:**
  - `anomaly_id`, `mmsi`, `anomaly_type` (`AIS_TRANSMISSION_GAP`, `ABNORMAL_SPEED_DROP`, `LOITERING_IN_ZONE`, `ERRATIC_COURSE_CHANGE`), `severity_level` (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), `time_start`, `time_end`, `duration_seconds`, `geometry_geojson`, `anomaly_score`, `context_indicators`, `description`.
- **Transformations Required:**
  1. Transmission gap check: Consecutive points with $\Delta t \ge 1.0\text{ hour}$ flagged as `AIS_TRANSMISSION_GAP`.
  2. Speed reduction check: Speed drop $\ge 4.0\text{ knots}$ in proximity to maritime zones flagged as `ABNORMAL_SPEED_DROP`.
- **Validation Required:** Verify anomaly severity tiers are mathematically calibrated ($0.0-1.0$).
- **Test Proving Compatibility:** `response_of_person2_member3/test_vessel_intelligence.py::test_detect_behavioral_anomalies`.
- **Unresolved Issue:** None.

---

### Step 5: Vessel Matches & Anomalies $\to$ Person 1 Source Attribution Engine

```
[VesselMatch + UnmatchedVessel + AnomalyEvent] ────► [CandidateFilterAndEvaluator (marineshield.investigation)]
```

- **Producer:** Member 3 Vessel Intelligence Service (`intelligence_service.py`).
- **Consumer:** Person 1 Candidate Filter & Evaluator (`marineshield/investigation/candidate_filter.py`).
- **Input Format:** Ingested into `marineshield.investigation.schemas.VesselObservation` objects.
- **Output Format:** Candidate evaluation payload containing:
  - `source_category`: `VESSEL_IDENTIFIED` | `VESSEL_UNTRACKED_DARK` | `NON_VESSEL_SOURCE`.
  - `component_scores`: $S_{spatial}, S_{temporal}, S_{trajectory}, S_{drift}, S_{vessel}, S_{behavior}, C_{contradiction}$.
  - `supporting_evidence`: Atomic evidence items.
  - `contradictory_evidence`: Atomic contradiction items.
- **Transformations Required:**
  1. Map `VesselMatch` MMSI into `VESSEL_IDENTIFIED` candidate entity.
  2. Map `UnmatchedVessel` SAR detection into `VESSEL_UNTRACKED_DARK` candidate entity with `unmatched_sar_target = True`.
  3. Ingest `AnomalyEvent` (AIS gap or speed drop) as behavioral bonus ($S_{behavior} + 30.0$ to $+45.0$).
  4. Ingest moored at berth status as active contradiction penalty ($C_{contradiction} = 80.0$).
- **Validation Required:**
  - Verify that dark vessels without AIS are fully evaluated as valid candidate hypotheses.
  - Verify that contradiction penalties are properly deducted ($E(H) = \sum w_i S_i - w_c C$).
- **Test Proving Compatibility:** `tests/unit/test_source_investigation_engine.py::test_unmatched_sar_dark_vessel`.
- **Unresolved Issue:** Adapter bridge: A dedicated adapter function is required to convert Member 3's output dictionaries (`vessel_demonstration_results.json`) directly into Member 4's `VesselObservation` dataclass instances.

---

### Step 6: Evidence Scoring $\to$ Canonical InvestigationResult

```
[Candidate Hypotheses] ────► [SourceInvestigationEngine (marineshield.investigation)]
```

- **Producer:** Person 1 `EvidenceContradictionEngine` (`marineshield/investigation/evidence_engine.py`).
- **Consumer:** Downstream FastAPI Endpoints (`/api/v1/attribution`), Decision Support Dossiers, and WebGIS Frontend (Person 4).
- **Input Format:** Scored candidate hypotheses, data quality index, and AIS coverage percentage.
- **Output Format:** Canonical `InvestigationResult` payload conforming to `docs/api/INVESTIGATION_CONTRACTS.md`.
- **Exact Fields in Payload:**
  - `incident_id`, `status` (`ATTRIBUTED_CANDIDATES_EVALUATED` / `SOURCE_UNKNOWN` / `ABSTAINED`).
  - `release_hypothesis`: `ReleaseHypothesisContract` (§1).
  - `candidate_hypotheses`: Ranked list of `SourceHypothesisContract` (§2).
  - `top_hypothesis_id`, `top_hypothesis_category`, `top_evidence_score`, `top_evidence_strength`.
  - `ranking_stability` (`ROBUST_DOMINANT_HYPOTHESIS`, `AMBIGUOUS_CLOSE_ALTERNATIVES`, `FRAGILE_RANKING`, `MARGINAL`).
  - `score_margin_over_second`: Floating point $\Delta$.
  - `non_guilt_clause`: Mandatory legal disclaimer string.
- **Transformations Required:** Output serialization to standard ISO 8601 UTC JSON.
- **Validation Required:** All 8 synthetic investigation fixtures must pass verification.
- **Test Proving Compatibility:** `tests/integration/test_investigation_integration.py`.
- **Unresolved Issue:** None.
