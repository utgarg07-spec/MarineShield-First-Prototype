# MarineShield — Canonical Investigation & Attribution Domain Contracts
## Release Reconstruction & Source Attribution Subsystem (Member 4 / Person 1)

**Owner**: Person 1 / Member 4  
**Modules Covered**: Release Time & Location Estimation (Layer 5), Candidate Hypothesis Generation (Section 6), Evidence + Contradiction Engine (Module F), Counterfactual Attribution & Unknown Engine (Section 6)  
**Status**: `CANONICAL — DO NOT MODIFY WITHOUT RECORDED ARCHITECTURAL DECISION`  
**Document Version**: `1.0.0`  
**Created**: `2026-08-20T17:50:00Z`  
**Governed By**: [`docs/architecture/ARCHITECTURE.md`](file:///d:/MarineShield/MarineShield/docs/architecture/ARCHITECTURE.md), [`docs/architecture/WORKSTREAMS.md`](file:///d:/MarineShield/MarineShield/docs/architecture/WORKSTREAMS.md), [`.agents/rules/agent_core.md`](file:///d:/MarineShield/MarineShield/.agents/rules/agent_core.md), [`.agents/rules/api_contracts.md`](file:///d:/MarineShield/MarineShield/.agents/rules/api_contracts.md), [`docs/ml/OIL_INTELLIGENCE_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/ml/OIL_INTELLIGENCE_CONTRACTS.md)

---

## CRITICAL CONTRACT PREAMBLE & RESPONSIBLE-AI DIRECTIVES

This document defines the **authoritative data contracts and schema definitions** for the MarineShield Investigation and Source Attribution domain (Member 4 / Person 1).

### 1. Mandatory Separation of Uncertainty and Quality Types
Per [`docs/ml/OIL_INTELLIGENCE_CONTRACTS.md`](file:///d:/MarineShield/MarineShield/docs/ml/OIL_INTELLIGENCE_CONTRACTS.md) Preamble, no schema field, calculation, or API payload may conflate the four distinct concepts:

| Concept | Definition | Subsystem Owner | Schema Field Prefix |
| :--- | :--- | :--- | :--- |
| **Model Confidence** | Statistical certainty of ML detection models (e.g. U-Net segmentation sigmoid / look-alike softmax probability). | Member 2 (ML) | `model_confidence.*` |
| **Data Quality Index** | Empirical measurement of observation completeness, sensor noise, and coverage flags. | Member 1 & 2 (Prep/SAR) | `data_quality.*` |
| **Evidence Score & Strength** | Spatio-temporal and behavioral compatibility score `E(H)` evaluated via deterministic algorithms against a specific hypothesis. | Member 4 (Investigation) | `evidence_score`, `evidence_strength` |
| **Forecast Uncertainty** | Spatial spread and probability density of forward drift particle ensembles (e.g. PyGNOME cones). | Member 5 (Drift) | `forecast_uncertainty.*` |

### 2. Evidence Compatibility is NOT Legal Guilt
- **Analytical Decision-Support Only**: MarineShield outputs represent spatial-temporal and behavioral **compatibility rankings** between candidate hypotheses and observed maritime data.
- **Strict Prohibition of Legal Terminology**: Contracts, API payloads, and UI schemas MUST NOT use terms such as `culprit`, `guilty_vessel`, `perpetrator`, `illegal_discharger`, or `convicted_source`.
- **Neutral Analytical Taxonomy**: Schemas MUST use `candidate_hypothesis`, `compatibility_score`, `supporting_indicators`, `contradictory_indicators`, `unmatched_vessel`, and `unknown_source`.

### 3. Prohibition of Black-Box / LLM Evidence Calculation
- All evidence scores, compatibility metrics, and contradiction penalties MUST be computed using **transparent, deterministic mathematical formulas**.
- Large Language Models (LLMs) MUST NOT act as scoring authorities, hypothesis rankers, or operational evidence calculators.

---

## §1 — Release Hypothesis Contract

### 1.1 Definition
A **Release Hypothesis** ($H_{rel}$) models an estimated oil release event reconstructed by combining backward drift particle simulations (from Person 3 / Member 5) with ocean current and wind forcing history. It defines the temporal release window $[t_{start}, t_{end}]$ and the geographic uncertainty polygon within which oil was plausibly discharged.

### 1.2 Schema

```json
{
  "release_hypothesis_id": "string (UUID v4) — unique identifier for this release hypothesis",
  "incident_id": "string (UUID v4) — parent incident identifier",
  "spill_geometry_id": "string (UUID v4) — references Member 2 verified SpillGeometry (§7)",
  "hypothesis_state": "CANDIDATE | EVALUATED | UNRESOLVED | ABSTAINED | REJECTED",
  "discharge_modality": "SINGLE_DISCHARGE | MULTIPLE_DISCHARGE | CONTINUOUS_DISCHARGE | UNCERTAIN_ORIGIN",
  "temporal_scope": {
    "t_observation_utc": "string (ISO 8601 UTC) — timestamp of SAR satellite acquisition",
    "t_earliest_utc": "string (ISO 8601 UTC) — earliest plausible release timestamp",
    "t_most_likely_utc": "string (ISO 8601 UTC) — central estimated release timestamp",
    "t_latest_utc": "string (ISO 8601 UTC) — latest plausible release timestamp",
    "window_duration_hours": "float >= 0.0 — total uncertainty window duration in hours"
  },
  "spatial_scope": {
    "release_polygon_geojson": {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[lon, lat], "..."]]
      },
      "properties": {
        "uncertainty_area_km2": "float > 0.0 — geographic uncertainty area",
        "centroid_lon": "float — centroid longitude (EPSG:4326)",
        "centroid_lat": "float — centroid latitude (EPSG:4326)",
        "bounding_box": {
          "lon_min": "float",
          "lat_min": "float",
          "lon_max": "float",
          "lat_max": "float"
        }
      }
    },
    "crs": "EPSG:4326"
  },
  "reconstruction_method": {
    "engine": "PYGNOME_BACKWARD_DRIFT_INTEGRATION | ANALYTICAL_VORTICITY_BACKTRACKING",
    "engine_version": "string (e.g. 'pygnome-1.1.8-m4-adapter-v1.0')",
    "backward_simulation_hours": "float > 0.0",
    "forcing_datasets": {
      "wind_dataset_id": "string (e.g. 'ERA5-Reanalysis-2026-08')",
      "current_dataset_id": "string (e.g. 'HYCOM-Global-Analysis-2026-08')"
    }
  },
  "supporting_evidence_ids": ["string (UUID v4) — references §3 EvidenceItem records"],
  "contradictory_evidence_ids": ["string (UUID v4) — references §3 EvidenceItem records"],
  "provenance": {"$ref": "#section-10-provenance"},
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

---

## §2 — Source Hypothesis Contract

### 2.1 Definition
A **Source Hypothesis** ($H_{src}$) represents a candidate source formulated to explain the reconstructed release event. The hypothesis set MUST explicitly support competing candidates across four distinct categories.

### 2.2 Valid Source Hypothesis Categories

| Category Code | Operational Meaning | Analytical Representation |
| :--- | :--- | :--- |
| `VESSEL_IDENTIFIED` | Specific AIS-tracked vessel present in the spatio-temporal release envelope | Candidate identified by MMSI, IMO, vessel name, and track segment |
| `VESSEL_UNTRACKED_DARK` | SAR-detected vessel lacking correlated AIS transmission during release window | Candidate identified by SAR detection ID, estimated length, and radar backscatter |
| `NON_VESSEL_SOURCE` | Offshore oil platform, subsea pipeline, natural seabed seep, or coastal terminal | Candidate identified by GIS asset registry ID, facility name, and fixed coordinates |
| `UNKNOWN_SOURCE` | Source origin cannot be reliably resolved from available observations | Default state when no candidate crosses threshold or data quality is insufficient |

### 2.3 Schema

```json
{
  "source_hypothesis_id": "string (UUID v4) — unique identifier for this source hypothesis",
  "incident_id": "string (UUID v4) — parent incident identifier",
  "release_hypothesis_id": "string (UUID v4) — references §1 ReleaseHypothesis",
  "hypothesis_label": "string (e.g. 'H_1', 'H_2', 'H_dark_vessel', 'H_non_vessel', 'H_unknown')",
  "source_category": "VESSEL_IDENTIFIED | VESSEL_UNTRACKED_DARK | NON_VESSEL_SOURCE | UNKNOWN_SOURCE",
  
  "candidate_entity": {
    "vessel_mmsi": "string | null — MMSI for VESSEL_IDENTIFIED, null otherwise",
    "vessel_imo": "string | null — IMO number if available",
    "vessel_name": "string | null — Reported vessel name",
    "vessel_type": "string | null (e.g. 'TANKER', 'CARGO', 'FISHING', 'UNKNOWN')",
    "vessel_flag": "string | null — Flag state ISO 3166-1 alpha-2 code",
    "sar_vessel_detection_id": "string | null — references Member 2 SAR vessel detection if dark/matched",
    "non_vessel_facility_id": "string | null — GIS asset ID for offshore platform or pipeline",
    "description": "string — human-readable neutral analytical description"
  },

  "evidence_evaluation": {
    "evidence_score": "float [0.0, 100.0] — deterministic compatibility score (see §5)",
    "evidence_strength": "STRONG_COMPATIBILITY | MODERATE_COMPATIBILITY | WEAK_COMPATIBILITY | INSUFFICIENT_EVIDENCE",
    "ranking_position": "int >= 1 — ordinal rank among evaluated hypotheses (1 = highest compatibility)",
    "counterfactual_analysis": {
      "delta_score_without_this_candidate": "float >= 0.0 — delta in top ranking score if this candidate is removed",
      "ranking_stability": "STABLE_DOMINANT | COMPETITIVE_AMBIGUOUS | MARGINAL",
      "eval_notes": "string | null"
    }
  },

  "supporting_evidence_ids": ["string (UUID v4) — references §3 EvidenceItem records"],
  "contradictory_evidence_ids": ["string (UUID v4) — references §3 EvidenceItem records"],
  
  "analytical_status": "UNDER_INVESTIGATION | HIGH_COMPATIBILITY_CANDIDATE | PLAUSIBLE_CANDIDATE | UNLIKELY | RULED_OUT | UNRESOLVED_UNKNOWN",
  "explicit_non_guilt_clause": "This hypothesis evaluation reflects spatio-temporal compatibility with observed data and does not constitute legal proof of responsibility or regulatory violation.",
  
  "provenance": {"$ref": "#section-10-provenance"},
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

---

## §3 — Evidence Item Contract

### 3.1 Definition
An **Evidence Item** ($E_i$) represents an atomic, verifiable analytical observation evaluating the relationship between a physical data observation (AIS point, SAR vessel detection, drift trajectory, environmental sensor) and a candidate hypothesis.

### 3.2 Evidence Types & Polarity

| Evidence Type Code | Modality Evaluated | Polarity Options |
| :--- | :--- | :--- |
| `SPATIAL_PROXIMITY` | Distance from candidate position to reconstructed release polygon | `SUPPORTING` (within buffer) / `CONTRADICTORY` (distant) |
| `TEMPORAL_INTERSECTION` | Timestamp alignment with estimated release window $[t_{start}, t_{end}]$ | `SUPPORTING` (within window) / `CONTRADICTORY` (outside window) |
| `TRAJECTORY_INTERSECTION` | Vessel track segment geometric intersection with release polygon | `SUPPORTING` (direct transit) / `CONTRADICTORY` (divergent path) |
| `DRIFT_COMPATIBILITY` | Backward drift particle convergence with vessel trajectory | `SUPPORTING` (high particle density) / `CONTRADICTORY` (zero convergence) |
| `VESSEL_CHARACTERISTICS` | Vessel type, deadweight, and ballast/cargo capability compatibility | `SUPPORTING` (tanker/bilge capacity) / `CONTRADICTORY` (unpowered barge) |
| `BEHAVIOR_ANOMALY` | AIS transmission gaps, speed drops, abrupt turns, or loitering near release zone | `SUPPORTING` (anomalous maneuver) / `NEUTRAL_CONTEXT` |
| `CONTRADICTORY_PHYSICS` | Speed/acceleration required to reach slick violates vessel physical limits | `CONTRADICTORY` |

### 3.3 Schema

```json
{
  "evidence_id": "string (UUID v4) — unique identifier for this evidence item",
  "incident_id": "string (UUID v4)",
  "target_hypothesis_id": "string (UUID v4) — references §2 SourceHypothesis or §1 ReleaseHypothesis",
  "evidence_type": "SPATIAL_PROXIMITY | TEMPORAL_INTERSECTION | TRAJECTORY_INTERSECTION | DRIFT_COMPATIBILITY | VESSEL_CHARACTERISTICS | BEHAVIOR_ANOMALY | CONTRADICTORY_PHYSICS",
  "polarity": "SUPPORTING | CONTRADICTORY | NEUTRAL_CONTEXT",
  
  "assertion": {
    "summary_text": "string — concise human-readable explanation (e.g. 'Vessel trajectory intersects release polygon with 1.2 km minimum distance')",
    "numeric_value": "float | null — measured metric value",
    "unit": "string | null (e.g. 'km', 'minutes', 'degrees', 'knots')",
    "threshold_reference": "string | null (e.g. 'Spatial buffer tolerance <= 5.0 km')"
  },

  "observation_source": {
    "source_channel": "AIS_TRAJECTORY | SAR_IMAGERY | SAR_SHIP_DETECTION | PYGNOME_DRIFT | NOAA_WIND | HYCOM_CURRENT | GIS_ASSET_REGISTRY",
    "dataset_version_id": "string | null — references DatasetVersion",
    "granule_or_feed_id": "string | null (e.g. 'S1A_IW_GRDH_...' or 'GFW_AIS_STREAM_V2')",
    "observation_timestamp_utc": "string (ISO 8601 UTC) | null",
    "observation_coordinates": {
      "type": "Point | LineString | Polygon | null",
      "coordinates": "array | null"
    }
  },

  "data_quality": {
    "index": "float [0.0, 1.0] — quality score of source observation",
    "quality_flags": ["string (e.g. 'INTERPOLATED_AIS_POSITION', 'COARSE_WIND_GRID', 'LOW_SAR_DQI')"]
  },

  "weight_assigned": "float [0.0, 1.0] — weight factor used in scoring formula",
  "normalized_score_contribution": "float [-100.0, 100.0] — signed contribution to final evidence score",

  "reproducibility": {
    "calculation_method": "string (e.g. 'geodesic_point_to_polygon_distance_v1')",
    "random_seed": "int | null",
    "parameters_used": {"key": "value"}
  },

  "provenance": {"$ref": "#section-10-provenance"},
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

---

## §4 — Contradiction Contract

### 4.1 Definition
A **Contradiction** ($C$) is an explicit structural record identifying a physical, temporal, or spatial impossibility that invalidates or heavily penalizes a candidate hypothesis. Contradictions MUST NOT be silently resolved, averaged out, or suppressed.

### 4.2 Schema

```json
{
  "contradiction_id": "string (UUID v4) — unique identifier for this contradiction",
  "incident_id": "string (UUID v4)",
  "target_hypothesis_id": "string (UUID v4) — references §2 SourceHypothesis",
  "contradiction_type": "TEMPORAL_IMPOSSIBILITY | TRAJECTORY_DIVERGENCE | PHYSICAL_SPEED_VIOLATION | OPPOSING_DRIFT_VECTOR | SATELLITE_OCCLUSION_CONFLICT",
  
  "conflict_description": {
    "assertion_text": "string — detailed explanation of the physical inconsistency",
    "evidence_item_a_id": "string (UUID v4) — first conflicting evidence item",
    "evidence_item_b_id": "string (UUID v4) — second conflicting evidence item or baseline constraint",
    "severity_penalty_weight": "float [0.0, 1.0] — deduction weight applied to evidence score"
  },

  "non_suppression_status": "ACTIVE_UNRESOLVED | ANALYST_ACKNOWLEDGED | EXPLAINED_BY_SENSOR_ERROR",
  "analyst_override_notes": "string | null",
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

---

## §5 — Evidence Score Contract

### 5.1 Deterministic Scoring Formula
The evidence compatibility score $E(H)$ for hypothesis $H$ is computed strictly deterministically:

$$E(H) = \max\left(0.0, \min\left(100.0, w_s S_{spatial} + w_t S_{temporal} + w_r S_{trajectory} + w_d S_{drift} + w_v S_{vessel} + w_b S_{behavior} - w_c C_{contradiction}\right)\right)$$

Where:
- $S_{spatial} \in [0, 100]$: Spatial proximity of candidate to reconstructed release polygon
- $S_{temporal} \in [0, 100]$: Temporal overlap of candidate with release window $[t_{start}, t_{end}]$
- $S_{trajectory} \in [0, 100]$: Trajectory heading, track intersection, and route alignment
- $S_{drift} \in [0, 100]$: Backward particle drift convergence density
- $S_{vessel} \in [0, 100]$: Vessel type, cargo/bunker volume, and discharge feasibility
- $S_{behavior} \in [0, 100]$: AIS gap anomaly, speed drops, loitering, and route deviations
- $C_{contradiction} \in [0, 100]$: Aggregate contradiction penalty score
- $(w_s, w_t, w_r, w_d, w_v, w_b, w_c)$: Validated weight vector summing to 1.0 (excluding penalty weight)

### 5.2 Schema

```json
{
  "evidence_score_id": "string (UUID v4)",
  "source_hypothesis_id": "string (UUID v4) — references §2 SourceHypothesis",
  "total_score": "float [0.0, 100.0] — composite evidence compatibility score",
  
  "component_breakdown": {
    "spatial_score": {"raw_score": "float [0.0, 100.0]", "weight": "float", "weighted_contribution": "float"},
    "temporal_score": {"raw_score": "float [0.0, 100.0]", "weight": "float", "weighted_contribution": "float"},
    "trajectory_score": {"raw_score": "float [0.0, 100.0]", "weight": "float", "weighted_contribution": "float"},
    "drift_score": {"raw_score": "float [0.0, 100.0]", "weight": "float", "weighted_contribution": "float"},
    "vessel_score": {"raw_score": "float [0.0, 100.0]", "weight": "float", "weighted_contribution": "float"},
    "behavior_score": {"raw_score": "float [0.0, 100.0]", "weight": "float", "weighted_contribution": "float"},
    "contradiction_penalty": {"raw_penalty": "float [0.0, 100.0]", "weight": "float", "weighted_deduction": "float"}
  },

  "weights_configuration": {
    "weights_version_id": "string (e.g. 'm4-weights-v1.0-heuristic')",
    "calibration_source": "HEURISTIC_BASELINE | HISTORICAL_TIME_MACHINE_CALIBRATED",
    "weights": {
      "w_spatial": 0.20,
      "w_temporal": 0.15,
      "w_trajectory": 0.15,
      "w_drift": 0.20,
      "w_vessel": 0.15,
      "w_behavior": 0.15,
      "w_contradiction": 0.20
    }
  },

  "scoring_algorithm_version": "string (e.g. 'deterministic-evidence-v1.0.0')",
  "provenance": {"$ref": "#section-10-provenance"},
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

---

## §6 — Evidence Strength Contract

### 6.1 Definition
**Evidence Strength** is an ordinal categorization of the overall analytical robustness and reliability of an evidence evaluation. It distinguishes well-supported conclusions from weak or ambiguous rankings.

### 6.2 Schema & Classification Matrix

| Strength Level | Minimum Evidence Score | Contradiction State | Data Quality Requirement |
| :--- | :--- | :--- | :--- |
| `STRONG_COMPATIBILITY` | $\ge 75.0$ | Zero severe active contradictions | Average DQI $\ge 0.70$ across modalities |
| `MODERATE_COMPATIBILITY` | $[50.0, 75.0)$ | Contradiction penalty $< 20.0$ | Average DQI $\ge 0.50$ |
| `WEAK_COMPATIBILITY` | $[30.0, 50.0)$ | Any | Any |
| `INSUFFICIENT_EVIDENCE` | $< 30.0$ | High contradiction or severe data blackout | Triggers mandatory `UNKNOWN` status (§7) |

```json
{
  "evidence_strength": "STRONG_COMPATIBILITY | MODERATE_COMPATIBILITY | WEAK_COMPATIBILITY | INSUFFICIENT_EVIDENCE",
  "strength_rationale": "string — concise explanation of factors determining this strength classification",
  "calibrated_thresholds_applied": {
    "strong_min_score": 75.0,
    "moderate_min_score": 50.0,
    "weak_min_score": 30.0,
    "max_contradiction_for_strong": 0.0
  }
}
```

---

## §7 — Unknown-Source State Contract

### 7.1 Definition
The **Unknown-Source State** (`UNKNOWN` / `INSUFFICIENT_EVIDENCE`) is a **mandatory first-class analytical conclusion**. When no candidate hypothesis achieves sufficient evidence strength, the system MUST explicitly output an `UNKNOWN` status rather than forcing attribution to the nearest vessel.

### 7.2 Mandatory Unknown Trigger Conditions

1. **No Candidate Over Threshold**: All evaluated candidate hypotheses have $E(H) < 30.0$.
2. **High Hypothesis Ambiguity**: Difference between top-1 and top-2 candidate scores is $< 5.0$ with both scores $< 60.0$.
3. **Severe AIS Data Blackout**: AIS coverage gap exceeds $80\%$ of the temporal release window in the release zone.
4. **Active SAR Dark Vessel Detected**: Unmatched SAR vessel detected in release zone but lacking track history to establish identity.

### 7.3 Schema

```json
{
  "unknown_state_id": "string (UUID v4)",
  "incident_id": "string (UUID v4)",
  "release_hypothesis_id": "string (UUID v4)",
  "status": "SOURCE_UNKNOWN",
  "trigger_condition": "ALL_CANDIDATES_BELOW_THRESHOLD | HIGH_HYPOTHESIS_AMBIGUITY | AIS_DATA_BLACKOUT | UNRESOLVED_DARK_VESSEL_PRESENT",
  
  "diagnostic_summary": {
    "total_candidates_evaluated": "int",
    "highest_candidate_score": "float [0.0, 100.0]",
    "ais_coverage_percentage": "float [0.0, 100.0]",
    "sar_dark_vessels_detected_count": "int"
  },

  "recommended_investigation_actions": [
    "EXPAND_AIS_TEMPORAL_SEARCH_WINDOW",
    "QUERY_COASTAL_RADAR_AND_VTS_ARCHIVES",
    "SEARCH_HISTORICAL_SAR_SCENES_FOR_EARLIER_PASSES",
    "REQUEST_ANALYST_MANUAL_TRACK_RECONSTRUCTION",
    "FLAG_FOR_NEXT_BEST_OBSERVATION_SATELLITE_PASS"
  ],

  "provenance": {"$ref": "#section-10-provenance"},
  "created_at_utc": "string (ISO 8601 UTC)"
}
```

---

## §8 — Supporting & Contradictory Evidence Panels Contract

### 8.1 Definition
For frontend WebGIS display (Person 4 / Member 6) and PDF Incident Reports (Person 3 / Member 6), evidence MUST be formatted into structured **Supporting** and **Contradictory** panels for direct human-in-the-loop inspection.

### 8.2 Schema

```json
{
  "explainability_payload": {
    "source_hypothesis_id": "string (UUID v4)",
    "hypothesis_label": "string",
    "candidate_name": "string",
    "overall_score": "float [0.0, 100.0]",
    "overall_strength": "STRONG_COMPATIBILITY | MODERATE_COMPATIBILITY | WEAK_COMPATIBILITY | INSUFFICIENT_EVIDENCE",
    
    "supporting_evidence_panel": [
      {
        "icon": "CHECK_CIRCLE | LOCATION_PIN | CLOCK | COMPASS | SHIP",
        "title": "string (e.g. 'Spatial Release Coincidence')",
        "detail": "string (e.g. 'Vessel trajectory within 1.8 km of reconstructed release polygon centroid')",
        "metric": "1.8 km",
        "data_source": "AIS Stream + Sentinel-1 SAR",
        "provenance_ref": "string (UUID v4)"
      }
    ],

    "contradictory_evidence_panel": [
      {
        "icon": "ALERT_TRIANGLE | X_CIRCLE | CLOCK_ALERT",
        "title": "string (e.g. 'AIS Transmission Gap')",
        "detail": "string (e.g. '42-minute AIS transmission gap during peak estimated release time window')",
        "metric": "42 min gap",
        "data_source": "AIS Receiver Station IN-GOA-01",
        "provenance_ref": "string (UUID v4)"
      }
    ],

    "data_limitations_panel": [
      {
        "title": "string (e.g. 'Coarse Wind Grid Resolution')",
        "detail": "string (e.g. 'ERA5 0.25° wind vectors utilized; local coastal micro-currents unrepresented')",
        "impact_level": "LOW | MEDIUM | HIGH"
      }
    ]
  }
}
```

---

## §9 — Counterfactual Attribution Analysis Contract

### 9.1 Definition
**Counterfactual Attribution Analysis** evaluates the sensitivity and stability of hypothesis rankings by testing what happens to score distributions when the top-ranked candidate hypothesis $H_{top}$ is removed ($H \setminus \{H_{top}\}$).

### 9.2 Schema

```json
{
  "counterfactual_analysis_id": "string (UUID v4)",
  "incident_id": "string (UUID v4)",
  "baseline_top_hypothesis_id": "string (UUID v4)",
  "baseline_top_score": "float [0.0, 100.0]",
  "second_ranked_hypothesis_id": "string (UUID v4)",
  "second_ranked_baseline_score": "float [0.0, 100.0]",
  
  "delta_score_margin": "float >= 0.0 — difference between rank 1 and rank 2 scores",
  
  "counterfactual_evaluation": {
    "score_distribution_without_top_candidate": {
      "new_rank_1_hypothesis_id": "string (UUID v4)",
      "new_rank_1_score": "float [0.0, 100.0]",
      "unknown_score_delta": "float"
    },
    "ranking_stability": "ROBUST_DOMINANT_HYPOTHESIS | AMBIGUOUS_CLOSE_ALTERNATIVES | FRAGILE_RANKING",
    "explanation": "string — e.g. 'Top candidate exhibits a 28.5 point margin over second candidate; removal leaves no remaining hypothesis above threshold.'"
  },

  "created_at_utc": "string (ISO 8601 UTC)"
}
```

---

## §10 — Investigation Provenance & Reproducibility Contract

### 10.1 Definition
Every investigation conclusion, hypothesis score, and release polygon MUST carry a `provenance` block enabling exact re-execution and auditability.

### 10.2 Schema

```json
{
  "provenance": {
    "investigation_execution_id": "string (UUID v4) — Celery task or job run ID",
    "incident_id": "string (UUID v4)",
    "execution_timestamp_utc": "string (ISO 8601 UTC)",
    "executing_subsystem_version": "string (e.g. 'marineshield-attribution-v1.0.0')",
    
    "upstream_ml_provenance": {
      "spill_geometry_id": "string (UUID v4) — references Member 2 SpillGeometry",
      "sar_granule_id": "string — Copernicus Sentinel-1 granule ID",
      "segmentation_model_version_id": "string — references Member 2 ModelVersion",
      "sar_vessel_model_version_id": "string | null"
    },

    "upstream_drift_provenance": {
      "backward_drift_simulation_id": "string (UUID v4) — references Member 5 drift run",
      "pygnome_version": "string (e.g. 'pygnome-1.1.8')",
      "particle_count": 1000,
      "ocean_current_dataset_id": "string",
      "wind_dataset_id": "string"
    },

    "ais_data_provenance": {
      "provider": "GLOBAL_FISHING_WATCH | INCOIS | DG_SHIPPING | COMBINED_FEED",
      "query_bounding_box": {
        "lon_min": "float", "lat_min": "float", "lon_max": "float", "lat_max": "float"
      },
      "query_time_range_utc": {
        "start": "string (ISO 8601 UTC)", "end": "string (ISO 8601 UTC)"
      },
      "total_vessel_tracks_evaluated": "int",
      "total_ais_positions_indexed": "int"
    },

    "scoring_configuration_provenance": {
      "weights_version_id": "string",
      "scoring_algorithm_version": "string"
    }
  }
}
```

---

## §11 — API Payload Schemas (`/api/v1/attribution`)

### 11.1 Attribution Incident Response Payload Standard
Per [`.agents/rules/api_contracts.md`](file:///d:/MarineShield/MarineShield/.agents/rules/api_contracts.md), all endpoints returning attribution data MUST wrap data inside the standard response envelope:

```json
{
  "status": "success",
  "data": {
    "incident_id": "string (UUID v4)",
    "release_hypothesis": {"$ref": "#section-1-release-hypothesis"},
    "candidate_hypotheses": [
      {"$ref": "#section-2-source-hypothesis"}
    ],
    "counterfactual_analysis": {"$ref": "#section-9-counterfactual-attribution-analysis"},
    "explainability_panels": [
      {"$ref": "#section-8-supporting--contradictory-evidence-panels"}
    ]
  },
  "metadata": {
    "timestamp": "string (ISO 8601 UTC)",
    "request_id": "string (UUID v4)",
    "execution_time_ms": 142
  },
  "error": null
}
```

---

## §12 — Inter-Workstream Integration Map

```
Upstream Inputs                      Member 4 Investigation Subsystem           Downstream Consumers
────────────────────────────────────────────────────────────────────────────────────────────────────────
Member 2: SpillGeometry (§7)    ──►  [Release Reconstruction]              ──►  Member 3: AIS-SAR
Member 5: PyGNOME Backward Drift──►  • Estimates Release Window [t1, t2]        Candidate Spatial Filter
                                     • Estimates Release Polygon
                                                │
                                                ▼
Member 3: AIS Tracks & Matches  ──►  [Candidate Hypothesis Generator]
Member 2: SAR Vessel Detections ──►  • H1..Hn (Vessels), H_dark, H_non, H_unk
                                                │
                                                ▼
                                     [Evidence + Contradiction Engine]     ──►  Member 6 Backend:
                                     • Formula E(H) deterministic scoring       FastAPI /api/v1/attribution
                                     • Evidence Items & Contradictions          PDF Incident Reports
                                                │
                                                ▼
                                     [Attribution & Unknown Engine]        ──►  Member 5 & 6:
                                     • Counterfactual stability analysis        Response Priority Score
                                     • Mandatory UNKNOWN output state           WebGIS Explainability UI
```

---

## §13 — Unresolved Questions & Open Decisions

| # | Item | Architectural Scope | Status |
| :-: | :--- | :--- | :-: |
| **Q-1** | **Calibrated Evidence Weights Vector** | Weight vector $(w_s, w_t, w_r, w_d, w_v, w_b, w_c)$ requires empirical calibration on historical incident datasets via Historical Incident Time Machine. | **PENDING CALIBRATION** |
| **Q-2** | **AIS Interpolation Method** | Trajectory intersection between AIS points: Linear interpolation vs Great Circle (Rhumb line / Geodesic) for long-duration transmission gaps. | **PENDING REVIEW** |
| **Q-3** | **Dark Vessel Bounding Uncertainty** | SAR-detected dark vessels lack velocity history; spatial buffer threshold must be calibrated against radar resolution. | **PENDING REVIEW** |
| **Q-4** | **Counterfactual Removal Threshold** | Minimum delta score required to declare a ranking `ROBUST_DOMINANT` vs `AMBIGUOUS_CLOSE_ALTERNATIVES`. | **PENDING BENCHMARK** |

---

## §14 — Assumptions

1. **WGS 84 (`EPSG:4326`) Standard**: All geographic coordinates and GeoJSON geometries use `[longitude, latitude]` format.
2. **Strict ISO 8601 UTC Standard**: All timestamp strings throughout evidence calculation MUST be formatted as `YYYY-MM-DDTHH:MM:SSZ`.
3. **No-Hindsight Temporal Slicing**: Evidence calculation for historical replays at timestamp $T$ strictly enforces $t_{observation} \le T$, preventing future AIS or environmental data from leaking into past evaluations.
4. **Member 5 Drift Availability**: Backward drift particle vectors are computed by Member 5 (Person 3 / PyGNOME) and ingested by Member 4.
5. **Deterministic Output**: For identical input geometries, AIS tracks, and weight configurations, the evidence engine produces identical floating-point scores.

---

## §15 — Schema Validation (Executable Test Suite)

```python
# Runnable validation via active virtual environment
import json, uuid, datetime

release_hyp = {
    "release_hypothesis_id": str(uuid.uuid4()),
    "incident_id": str(uuid.uuid4()),
    "spill_geometry_id": str(uuid.uuid4()),
    "hypothesis_state": "EVALUATED",
    "discharge_modality": "SINGLE_DISCHARGE",
    "temporal_scope": {
        "t_observation_utc": "2026-08-20T10:00:00Z",
        "t_earliest_utc": "2026-08-20T04:00:00Z",
        "t_most_likely_utc": "2026-08-20T06:30:00Z",
        "t_latest_utc": "2026-08-20T09:00:00Z",
        "window_duration_hours": 5.0
    },
    "spatial_scope": {
        "release_polygon_geojson": {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[72.5, 18.5], [72.6, 18.5], [72.6, 18.6], [72.5, 18.6], [72.5, 18.5]]]
            },
            "properties": {"uncertainty_area_km2": 11.2, "centroid_lon": 72.55, "centroid_lat": 18.55}
        },
        "crs": "EPSG:4326"
    },
    "created_at_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

encoded = json.dumps(release_hyp, indent=2)
decoded = json.loads(encoded)
assert decoded["hypothesis_state"] in ("CANDIDATE", "EVALUATED", "UNRESOLVED", "ABSTAINED", "REJECTED")
assert decoded["temporal_scope"]["window_duration_hours"] == 5.0
print("ReleaseHypothesis Schema Validation: PASS")
```

---

## Document Change Log

| Version | Date (UTC) | Author | Change Description |
| :--- | :--- | :--- | :--- |
| `1.0.0` | `2026-08-20T17:50:00Z` | Member 4 / Person 1 | Initial canonical investigation domain contracts definition covering §1–§15. |

> **Any modification to this document requires recorded approval in [`docs/decisions/DECISION_LOG.md`](file:///d:/MarineShield/MarineShield/docs/decisions/DECISION_LOG.md).**
