# MarineShield — Person 1 Presentation Data Contract

**Contract Version:** `1.0.0`  
**Author:** Person 1 (Member 2 Oil Intelligence & Member 4 Source Investigation Workstreams)  
**Target Consumers:** Person 4 WebGIS Command Center UI & FastAPI Presentation Gateway  

---

## 1. Executive Overview & Data Delivery Architecture

This document specifies the exact JSON response structures produced by Person 1's backend subsystems for consumption by Person 4's WebGIS frontend interfaces.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Person 1 Presentation API Architecture                         │
├───────────────────────────────────┬────────────────────────────────────────────────────┤
│ Member 2 Oil Intelligence Service │ /api/v1/oil-intelligence/detect                   │
├───────────────────────────────────┼────────────────────────────────────────────────────┤
│ Member 4 Source Investigation     │ /api/v1/investigation/reconstruct                 │
├───────────────────────────────────┼────────────────────────────────────────────────────┤
│ Member 4 Counterfactual Engine    │ /api/v1/investigation/counterfactual              │
└───────────────────────────────────┴────────────────────────────────────────────────────┘
```

---

## 2. API Section A: Oil Intelligence Response Contract (`SpillDetectionResponse`)

### Canonical JSON Response Structure
```json
{
  "incident_id": "phase6-val-inc-20260821-001",
  "tile_id": "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train",
  "sar_granule_id": "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
  "status": "LOOKALIKE_REJECTED",
  "is_abstained": false,
  "abstention_details": null,
  "spill_mask": null,
  "spill_geometry": null,
  "lookalike_verification": {
    "predicted_class": "LOW_WIND_AREA",
    "pipeline_decision": "REJECT_AS_LOOKALIKE",
    "class_probabilities": {
      "LOW_WIND_AREA": 0.9139,
      "BIOGENIC_SLICK": 0.0337,
      "SHIP_WAKE": 0.0124,
      "NATURAL_FILM": 0.0337,
      "PETROLEUM_OIL": 0.0017,
      "UNCERTAIN": 0.0046
    },
    "model_confidence": {
      "entropy": 0.5783,
      "margin": 0.8802
    }
  },
  "severity": {
    "severity_class": "UNKNOWN",
    "severity_basis": {
      "mean_backscatter_db": 0.56,
      "backscatter_suppression_db": 0.30,
      "estimated_area_km2": 0.0,
      "texture_features_used": false
    },
    "explicit_non_claims": [
      "This classification does not represent estimated oil volume in tonnes or litres.",
      "This classification does not constitute ecological damage assessment.",
      "This classification does not imply legal severity of a MARPOL violation."
    ]
  },
  "data_quality": {
    "data_quality_index": 0.95,
    "quality_flags": []
  },
  "metrics_metadata_ref": "METRICS-SAR-SAM-ADAPT-v1.0",
  "provenance": {
    "sar_scene": {
      "granule_id": "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
      "polarization": "VV_VH",
      "source_api": "Copernicus Sentinel-1 SAR"
    },
    "preprocessing": {
      "pipeline_version": "sar-preprocess-v1.0.0",
      "processing_steps_applied": [
        "RADIOMETRIC_CALIBRATION_SIGMA0",
        "DB_CONVERSION",
        "SPECKLE_FILTERING_REFINED_LEE",
        "DETERMINISTIC_TILING_AND_NORMALIZATION"
      ]
    },
    "model": {
      "model_version_id": "sam-vit-b-sar-adapter-v1.0.0",
      "module": "OIL_INTELLIGENCE_DUAL_STAGE",
      "inference_device": "cuda (PyTorch)"
    },
    "training_dataset": {
      "dataset_version_id": "DARTIS-2019-v1.0",
      "dataset_name": "DARTIS-2019"
    }
  }
}
```

### Detailed Field Specification Table (Oil Intelligence)

| Field Name | Type | Required / Optional | Allowed Values / Range | Units | Null / Unknown Behavior |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `incident_id` | String (UUID) | Required | Any valid UUID string | N/A | Must not be null |
| `tile_id` | String | Required | Sub-tile identifier string | N/A | Must not be null |
| `sar_granule_id` | String | Required | Official Sentinel-1 Granule ID | N/A | Must not be null |
| `status` | String | Required | `OIL_DETECTED`, `LOOKALIKE_REJECTED`, `UNCERTAIN_ANALYSIS`, `ABSTAINED`, `NO_CANDIDATE_FOUND` | N/A | Must not be null |
| `is_abstained` | Boolean | Required | `true`, `false` | N/A | Must not be null |
| `spill_mask` | Object | Optional | Mask object or `null` | Base64 / Px | Returns `null` if status is `LOOKALIKE_REJECTED` |
| `spill_geometry` | Object | Optional | GeoJSON Feature or `null` | `EPSG:4326` `[lon, lat]` | Returns `null` if zero positive oil pixels |
| `lookalike_verification` | Object | Required | Classifier probability dictionary | Percent ($0.0-1.0$) | Must be fully populated |
| `severity` | Object | Required | `MINOR`, `MODERATE`, `MAJOR`, `SEVERE`, `UNKNOWN` | km², dB | Returns `UNKNOWN` tier if look-alike rejected |
| `metrics_metadata_ref` | String | Required | `"METRICS-SAR-SAM-ADAPT-v1.0"` | N/A | Constant version string |
| `provenance` | Object | Required | Granule, Preprocessing, Model, Dataset versions | N/A | Preserves full audit trail |

---

## 3. API Section B: Source Investigation Response Contract (`InvestigationResult`)

### Canonical JSON Response Structure
```json
{
  "incident_id": "phase6-val-inc-20260821-001",
  "mode": "MODE_A_PARTIAL_INTEGRATION_NO_ENVIRONMENT",
  "investigation_timestamp_utc": "2024-01-20T00:55:41.203509Z",
  "attribution_status": "SOURCE_UNKNOWN",
  "unknown_trigger_reason": "PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED",
  "release_reconstruction": {
    "release_region_status": "UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY",
    "release_time_window_status": "UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY",
    "reconstruction_polygon_geojson": null
  },
  "vessel_input_summary": {
    "total_ais_candidates_ingested": 5,
    "accepted_observations_count": 3,
    "excluded_future_observations_count": 2,
    "excluded_observation_ids": [
      "240cdb8f-9884-4852-9d71-4ee53d5efe63",
      "f5e5f969-7bd8-476d-b820-14ec20b4736b"
    ],
    "vessel_matches_count": 1,
    "unmatched_dark_vessels_count": 1
  },
  "environmental_evidence_status": {
    "status": "BLOCKED",
    "reason_code": "PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED",
    "provenance_status": "NOT_AVAILABLE"
  },
  "source_ranking_status": "NOT_COMPUTED",
  "evaluated_candidates": [
    {
      "candidate_id": "cand-vsl-mmsi-413123456",
      "hypothesis_label": "H_1",
      "source_category": "VESSEL_IDENTIFIED",
      "candidate_entity": {
        "vessel_mmsi": "413123456",
        "vessel_name": "Cooperative Vessel MMSI-413123456",
        "vessel_type": "CARGO"
      },
      "component_scores": {
        "spatial": 90.0,
        "temporal": 85.0,
        "trajectory": 80.0,
        "drift": "UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY",
        "vessel": 75.0,
        "behavior": 45.0
      },
      "supporting_evidence": [
        {
          "evidence_type": "SPATIAL_PROXIMITY",
          "polarity": "SUPPORTING",
          "summary": "Vessel transit points recorded near target region"
        }
      ],
      "contradictory_evidence": []
    }
  ],
  "non_guilt_clause": "This partial evaluation reflects maritime observations only. Absence of environmental drift history suppresses definitive source ranking. Unmatched dark targets carry analytical investigation flags only and do not constitute proof of responsibility.",
  "data_provenance": {
    "vessel_data_mode": "MOCK_HYBRID",
    "vessel_provenance_hash": "demo_run_dff3e36e4f111353",
    "environmental_data_mode": "NOT_AVAILABLE"
  }
}
```

### Detailed Field Specification Table (Source Investigation)

| Field Name | Type | Required / Optional | Allowed Values / Range | Units | Null / Unknown Behavior |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `incident_id` | String (UUID) | Required | Any valid UUID string | N/A | Must not be null |
| `mode` | String | Required | `MODE_A_PARTIAL_INTEGRATION_NO_ENVIRONMENT`, `MODE_B_FULL_INTEGRATION_WITH_ENVIRONMENT` | N/A | Must not be null |
| `investigation_timestamp_utc` | String | Required | ISO 8601 UTC timestamp | N/A | Must not be null |
| `attribution_status` | String | Required | `ATTRIBUTED_CANDIDATES_EVALUATED`, `SOURCE_UNKNOWN`, `ABSTAINED` | N/A | Emits `SOURCE_UNKNOWN` when evidence insufficient |
| `unknown_trigger_reason` | String | Optional | `PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED`, `LOW_DATA_QUALITY`, `WEAK_EVIDENCE_MARGIN` | N/A | Returns explicit reason string |
| `release_reconstruction` | Object | Required | Release status and GeoJSON polygon | `EPSG:4326` | Status set to `UNAVAILABLE_PENDING...` in Mode A |
| `source_ranking_status` | String | Required | `COMPUTED`, `NOT_COMPUTED` | N/A | Returns `NOT_COMPUTED` in Mode A |
| `evaluated_candidates` | Array | Required | List of candidate objects | Score ($0-100$) | Preserves supporting/contradictory lists |

---

## 4. API Section C: Counterfactual Attribution Response Contract (`CounterfactualResult`)

### Canonical JSON Response Structure
```json
{
  "incident_id": "phase6-val-inc-20260821-001",
  "status": "SUCCESS",
  "reason": "COUNTERFACTUAL_EVALUATION_COMPLETED",
  "replay_timestamp_utc": "2024-01-20T00:55:41.203509Z",
  "original_candidate_count": 2,
  "counterfactual_candidate_count": 1,
  "removed_candidate_id": "413111111",
  "removed_candidate_label": "H_1",
  "original_top_hypothesis_label": "H_1",
  "original_top_hypothesis_score": 74.69,
  "original_attribution_status": "ATTRIBUTED_CANDIDATES_EVALUATED",
  "counterfactual_attribution_status": "ATTRIBUTED_CANDIDATES_EVALUATED",
  "is_top_hypothesis_dominant": true,
  "is_result_weak_or_tied": false,
  "rank_changes": [
    {
      "hypothesis_label": "H_2",
      "candidate_id": "413222222",
      "original_rank": 2,
      "original_score": 25.80,
      "counterfactual_rank": 1,
      "counterfactual_score": 25.80,
      "rank_change": 1,
      "score_change": 0.0
    }
  ],
  "non_guilt_clause": "Counterfactual attribution is a deterministic sensitivity analysis of the source-ranking engine. It does not establish legal causality, responsibility, or illegal behavior.",
  "data_mode": "MOCK_HYBRID"
}
```

### Detailed Field Specification Table (Counterfactual Attribution)

| Field Name | Type | Required / Optional | Allowed Values / Range | Units | Null / Unknown Behavior |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `status` | String | Required | `SUCCESS`, `NOT_APPLICABLE`, `BLOCKED_TIE_POLICY_REQUIRED` | N/A | Must not be null |
| `reason` | String | Required | Reason description string | N/A | Must not be null |
| `removed_candidate_id` | String | Optional | Removed top candidate ID or `null` | N/A | Returns `null` if status is `NOT_APPLICABLE` |
| `is_top_hypothesis_dominant` | Boolean | Required | `true`, `false` | N/A | Evaluates margin $\ge 0.15$ threshold |
| `is_result_weak_or_tied` | Boolean | Required | `true`, `false` | N/A | Evaluates weak margin or score tie |
| `rank_changes` | Array | Required | List of remaining candidate rank deltas | Integer / Float | Populated with before/after position deltas |
