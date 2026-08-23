# Person 4 Frontend API Adapter Preflight Audit

**Target System:** Main MarineShield Project (`D:\MarineShield\MarineShield\frontend\`)  
**Audit Purpose:** Field-by-field preflight mapping of imported Person 4 frontend against Person 1 canonical API contracts.  
**Audit Timestamp:** 2026-08-23 (UTC)  
**Status:** COMPLETE — Strictly Read-Only (Zero adapter code modified during preflight).

---

## 1. Executive Summary & Canonical Endpoints

The Person 4 frontend API client (`FastApiClient.ts`, `ApiClient.ts`, `MockApiClient.ts`) was originally designed against Person 4's prototype backend. This preflight identifies all field mismatches, geometry assumptions, and client interface gaps to prepare for adapting the frontend to Person 1's authoritative REST endpoints:

1. `POST /api/v1/oil-intelligence/detect` (`SpillDetectionResponse`)
2. `POST /api/v1/investigation/reconstruct` (`InvestigationResult`)
3. `POST /api/v1/investigation/counterfactual` (`CounterfactualResult`)

---

## 2. API Method & Type Analysis

### Existing Client Methods (`frontend/src/api/clients/ApiClient.ts`):
- `getIncidents(query?)`
- `getIncident(id)`
- `getForecast(incidentId, forecastId)`
- `getThreatAssessment(incidentId, threatId)`
- `getSARScenes(incidentId)`
- `getSARTiles(incidentId)`
- `getSARDetections(incidentId)`
- `getVessels(incidentId)`
- `getVesselMatches(incidentId)`
- `getUnmatchedVessels(incidentId)`
- `getAnomalies(incidentId)`

### Missing Methods to Add:
- `detectSpill(payload: SpillDetectionRequest): Promise<DetailResponse<SpillDetectionResponse>>`
- `reconstructRelease(payload: InvestigationRequest): Promise<DetailResponse<InvestigationResult>>`
- `evaluateCounterfactual(payload: CounterfactualRequest): Promise<DetailResponse<CounterfactualResult>>`

---

## 3. Field-by-Field Contract Comparison

### A. Oil Intelligence Detection Contract (`SpillDetectionResponse`)
- **Canonical Endpoint:** `POST /api/v1/oil-intelligence/detect`
- **Canonical Schema (`docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md`):**
  - `incident_id`: String (UUID)
  - `tile_id`: String
  - `sar_granule_id`: String
  - `status`: `'OIL_DETECTED' | 'LOOKALIKE_REJECTED' | 'UNCERTAIN_ANALYSIS' | 'ABSTAINED' | 'NO_CANDIDATE_FOUND'`
  - `is_abstained`: Boolean
  - `spill_geometry`: GeoJSON Feature / null (`EPSG:4326` `[lon, lat]`)
  - `lookalike_verification`: `{ predicted_class, pipeline_decision, class_probabilities, model_confidence }`
  - `severity`: `{ severity_class, severity_basis, explicit_non_claims }`
  - `data_quality`: `{ data_quality_index, quality_flags }`
  - `provenance`: `{ sar_scene, preprocessing, model, training_dataset }`
- **Frontend Mismatch:** Person 4's frontend types (`sar.ts`) only covered raw `SARSceneMetadata` and `SARTile`. The `SpillDetectionResponse` type was missing in `src/api/types/`.

### B. Source Investigation Contract (`InvestigationResult`)
- **Canonical Endpoint:** `POST /api/v1/investigation/reconstruct`
- **Canonical Schema (`docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md`):**
  - `incident_id`: String (UUID)
  - `mode`: `'MODE_A_PARTIAL_INTEGRATION_NO_ENVIRONMENT' | 'MODE_B_FULL_INTEGRATION_WITH_ENVIRONMENT'`
  - `attribution_status`: `'ATTRIBUTED_CANDIDATES_EVALUATED' | 'SOURCE_UNKNOWN' | 'ABSTAINED'`
  - `unknown_trigger_reason`: String / null
  - `release_reconstruction`: `{ release_region_status, release_time_window_status, reconstruction_polygon_geojson }`
  - `vessel_input_summary`: `{ total_ais_candidates_ingested, accepted_observations_count, excluded_future_observations_count, excluded_observation_ids, vessel_matches_count, unmatched_dark_vessels_count }`
  - `evaluated_candidates`: Array of `{ candidate_id, hypothesis_label, source_category, candidate_entity, component_scores, supporting_evidence, contradictory_evidence }`
  - `non_guilt_clause`: Constant legal disclaimer string
  - `data_provenance`: `{ vessel_data_mode, vessel_provenance_hash, environmental_data_mode }`
- **Frontend Mismatch:** Person 4's pages had placeholder text `"AWAITING CONTRACT"` for evidence and investigation views.

### C. Counterfactual Attribution Contract (`CounterfactualResult`)
- **Canonical Endpoint:** `POST /api/v1/investigation/counterfactual`
- **Canonical Schema (`docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md`):**
  - `incident_id`: String (UUID)
  - `status`: `'SUCCESS' | 'NOT_APPLICABLE' | 'BLOCKED_TIE_POLICY_REQUIRED'`
  - `reason`: String
  - `original_candidate_count`: Number
  - `counterfactual_candidate_count`: Number
  - `removed_candidate_id`: String / null
  - `removed_candidate_label`: String / null
  - `is_top_hypothesis_dominant`: Boolean
  - `is_result_weak_or_tied`: Boolean
  - `rank_changes`: Array of `{ hypothesis_label, candidate_id, original_rank, original_score, counterfactual_rank, counterfactual_score, rank_change, score_change }`
  - `non_guilt_clause`: Constant legal disclaimer string
  - `data_mode`: String

---

## 4. Geometry, CRS, and Timezone Assumptions

- **Coordinate Reference System (CRS):** Both Person 4 and Main Project enforce `EPSG:4326` WGS 84 coordinate order `[longitude, latitude]`.
- **Validation Requirement:** `MapContainer.tsx` must validate that GeoJSON features are non-empty, use `EPSG:4326`, and have valid coordinate pairs before passing to MapLibre GL.
- **Timestamps:** ISO 8601 UTC strings (`YYYY-MM-DDTHH:MM:SSZ`).
- **Unknown & Contradiction Handling:** Explicit support for `SOURCE_UNKNOWN` attribution status, `is_abstained` flag, contradictory evidence lists, and legal non-guilt disclaimers.

---

## 5. File Modification Plan

### Exact Files to Modify:
1. `frontend/src/api/types/oil_intelligence.ts` [NEW] — Add canonical `SpillDetectionResponse` types.
2. `frontend/src/api/types/investigation.ts` [NEW] — Add canonical `InvestigationResult` & `CounterfactualResult` types.
3. `frontend/src/api/types/index.ts` [MODIFY] — Export new Person 1 contract types.
4. `frontend/src/api/clients/ApiClient.ts` [MODIFY] — Declare Person 1 API client methods.
5. `frontend/src/api/clients/FastApiClient.ts` [MODIFY] — Implement live fetch calls to Person 1 REST routes (`/api/v1/oil-intelligence/detect`, etc.).
6. `frontend/src/api/clients/MockApiClient.ts` [MODIFY] — Implement deterministic mock responses using Phase 6/8 synthetic fixtures.
7. `frontend/src/map/MapContainer.tsx` [MODIFY] — Bind `spill_geometry` and `reconstruction_polygon_geojson` MapLibre GL GeoJSON layers with strict coordinate validation.
8. `frontend/src/pages/IncidentDetailPage.tsx` [MODIFY] — Wire Person 1 detection, investigation, and counterfactual data to existing inspector panels without altering layout or styling.

### Exact Files That Must NOT Change:
- All Person 1 backend Python modules (`marineshield/oil_intelligence/`, `marineshield/investigation/`)
- All Person 2 SAR / Vessel handoff code (`response_of_person2_member1/`, `response_of_person2_member3/`)
- All Person 3 backend code (`response_of_person3/`)
- Person 4 source repository (`D:\Person4-MarineShield\`)
- Layout components (`AppShell.tsx`, `Sidebar.tsx`, `TopBar.tsx`, `RightInspector.tsx`, `BottomTimeline.tsx`)
