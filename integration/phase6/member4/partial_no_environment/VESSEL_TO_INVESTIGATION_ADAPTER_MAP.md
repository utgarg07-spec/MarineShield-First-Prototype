# MarineShield — Vessel-to-Investigation Adapter Mapping Specification

**Document Version:** `1.0.0`  
**Author:** MarineShield Integration Auditor / Member 4 Workstream  
**Target Subsystems:** Person 2 Member 3 Vessel Intelligence $\to$ Person 1 Member 4 Investigation Engine  

---

## 1. Executive Purpose

This specification establishes the explicit schema mapping and temporal slicing rules required to transform Person 2's Member 3 vessel handoff deliverables (`VESSEL_DATA_CONTRACT.md` and `vessel_demonstration_results.json`) into Person 1's Member 4 input dataclass (`marineshield.investigation.schemas.VesselObservation`).

---

## 2. Temporal Slicing & No-Hindsight Rule

Per `.agents/rules/testing_rules.md` (Historical Replay & No-Hindsight Rule):
> *Evaluation scripts and investigation pipelines must strictly enforce temporal slicing ($t \le t_{\text{investigation}}$). No future AIS data, weather data, or satellite observations may leak into historic investigation pipelines.*

### Temporal Filter Criterion:
For an investigation conducted at timestamp $t_{\text{obs}}$ (e.g. `2024-01-20T00:55:41.203509Z`):
1. **Accepted Track Points:** Any AIS observation with $t \le t_{\text{obs}}$.
2. **Excluded Track Points:** Any AIS observation with $t > t_{\text{obs}}$.

### Audit Result on Demonstration Data (`vessel_demonstration_results.json`):
- `36959fc2...` (MMSI `413123456`, `2024-01-20T00:55:12Z`) $\to$ **ACCEPTED** ($t \le t_{obs}$)
- `be449c93...` (MMSI `413123456`, `2024-01-19T22:55:00Z`) $\to$ **ACCEPTED** ($t \le t_{obs}$)
- `af3fff3b...` (MMSI `413987654`, `2024-01-19T19:55:00Z`) $\to$ **ACCEPTED** ($t \le t_{obs}$)
- `240cdb8f...` (MMSI `413987654`, `2024-01-20T01:55:00Z`) $\to$ **EXCLUDED (FUTURE OBSERVATION)** ($+59\text{ min}$)
- `f5e5f969...` (MMSI `413555888`, `2024-01-20T01:00:00Z`) $\to$ **EXCLUDED (FUTURE OBSERVATION)** ($+4\text{ min}$)

---

## 3. Entity-by-Entity Transformation Field Mapping Table

```
Member 3 Output (vessel_demonstration_results.json)
  ├── matches: List[VesselMatch]
  ├── unmatched_detections: List[UnmatchedVessel]
  ├── behavior_features.anomalies_detected: List[AnomalyEvent]
  └── ais_candidates: List[AISObservation]
            │
            ▼ (VESSEL_TO_INVESTIGATION_ADAPTER)
Member 4 Input (marineshield.investigation.schemas)
  └── vessel_observations: List[VesselObservation]
```

### 3.1 Matched Cooperative Vessels (`matches` + `ais_candidates`)

| Member 3 Source Field | Member 4 Target Field | Transformation Rule |
| :--- | :--- | :--- |
| `matches[i].matched_mmsi` | `vessel_id`, `vessel_mmsi` | Formats 9-digit MMSI string. |
| `matches[i].match_status` | `source_type` | Set to `"AIS_TRACK"`. |
| `ais_candidates` (filtered $t \le t_{obs}$) | `track_points` | Group by MMSI, sort chronologically, format as `[{"lon", "lat", "timestamp_utc", "speed_knots"}]`. |
| `matches[i].dimension_match_score` | `estimated_length_m` | Derived from vessel registry or estimated length. |
| `anomalies_detected` (`AIS_TRANSMISSION_GAP`) | `has_ais_gap` | `True` if `mmsi` has active gap anomaly ending near release window; else `False`. |
| `anomalies_detected` (`ABNORMAL_SPEED_DROP`) | `speed_drop_knots` | Extract speed drop in knots (`initial_speed - final_speed`); default `0.0`. |
| `ais_candidates[i].navigational_status` | `is_moored_at_berth` | `True` if status is `"MOORED"` or `"AT_ANCHOR"`; else `False`. |

---

### 3.2 Unmatched Dark Vessels (`unmatched_detections`)

| Member 3 Source Field | Member 4 Target Field | Transformation Rule |
| :--- | :--- | :--- |
| `unmatched_detections[j].sar_detection_id` | `vessel_id`, `sar_vessel_detection_id` | Set `vessel_id = sar_detection_id`. |
| `unmatched_detections[j]` | `source_type` | Set strictly to `"SAR_DETECTION"`. |
| `unmatched_detections[j].estimated_length_meters` | `estimated_length_m` | Direct numeric float assignment. |
| `unmatched_detections[j].centroid_lat/lon` | `track_points` | Construct single spatial point array `[{"lon", "lat", "timestamp_utc", "speed_knots": 0.0}]`. |
| Constant | `has_ais_gap` | Set to `True` (Uncooperative / dark target). |
| Constant | `vessel_name` | Set to `"SAR-Detected Dark Target (Unmatched)"`. |

---

## 4. Responsible-AI & Non-Accusation Mandate

1. **Dark Vessels:** All unmatched SAR targets are processed as `VESSEL_UNTRACKED_DARK` candidates. They carry an analytical investigation flag and **must not be labeled as illegal, criminal, or proven guilty**.
2. **Deterministic Processing:** Field mappings are 100% deterministic and mathematical.
