# MarineShield Canonical Vessel-Domain Data Contract Specification

**Document Version:** `1.0.0`  
**Status:** `AUTHORITATIVE / FROZEN`  
**Producers:**
- **Person 1** (Member 2: SAR Vessel Detection Engine)
- **Person 2** (Member 3: AIS Tracking, PostGIS Ingestion, AIS–SAR Reconciliation, Anomaly Intelligence)  
**Consumers:**
- **Person 1** (Member 4: Release Estimation, Evidence + Contradiction Engine, Candidate Hypotheses $H_1 \dots H_n, H_{untracked}$)
- **Person 3** (Member 5: PyGNOME Drift Intersections; Member 6: FastAPI Services, Priority Engine, Incident Reports)
- **Person 4** (Member 6: WebGIS Command Center UI, Evidence Inspector, Layer Controls)

---

## 1. Executive Summary & Domain Scope

The **Vessel Domain** represents the maritime traffic intelligence backbone of MarineShield. It bridges remote sensing satellite observations (SAR ship detections) with real-world vessel trajectories (AIS transponder feeds) and anomalous behavior detection.

This document establishes the **7 canonical data contracts** governing the vessel domain:
1. **`Vessel`**: Static vessel identity, registry, dimensions, and risk profile.
2. **`AISObservation`**: Instantaneous spatial-temporal transponder broadcast point.
3. **`AISTrack`**: Segmented spatial-temporal trajectory line string with kinematic metrics.
4. **`SARVesselDetection`**: Physical ship detection derived from SAR radar imagery (produced by Person 1 / Member 2).
5. **`VesselMatch`**: Deterministic spatio-temporal reconciliation between SAR detection and AIS track (produced by Person 2 / Member 3).
6. **`UnmatchedVessel`**: Dark vessel intelligence for SAR-detected ships lacking corresponding AIS broadcasts.
7. **`AnomalyEvent`**: Behavioral and transmission anomalies (transponder gaps, loitering, sudden speed drops, course deviations).

> **CRITICAL ARCHITECTURAL DIRECTIVE**:
> In accordance with project rules, this document defines the contract specification only. Vessel ingestion, matching algorithms, and anomaly pipelines are implemented in subsequent tasks.

---

## 2. Core Architectural & Geodetic Rules

1. **Spatial Reference & Precision**:
   - All coordinates MUST be encoded in **`EPSG:4326` (WGS84 2D Geographic)**: Longitude $[-180.0, +180.0]$, Latitude $[-90.0, +90.0]$.
   - Floating-point coordinate precision: Minimum 6 decimal places ($\approx 0.11\text{ m}$ precision).

2. **Temporal Standard**:
   - All timestamps MUST be formatted as **ISO 8601 UTC** (`YYYY-MM-DDTHH:MM:SS.sssZ`).

3. **Identifier Standards**:
   - **MMSI**: 9-digit Maritime Mobile Service Identity (formatted as string or 9-digit integer).
   - **IMO**: 7-digit International Maritime Organization number (strictly validated with check digit when present).
   - **Entity IDs**: UUIDv4 strings.

4. **Deterministic Reconciliation Standard (ADR-002)**:
   - AIS-to-SAR matching MUST follow deterministic spatial-temporal criteria evaluating distance offset ($\Delta d$), time offset ($\Delta t$), heading delta ($\Delta \theta$), speed consistency ($\Delta v$), and physical vessel dimensions ($\Delta L, \Delta W$). Black-box matching is prohibited.

---

## 3. The 7 Canonical Vessel Contracts (JSON Schema Specifications)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MarineShieldVesselDomainContracts",
  "description": "Unified JSON schema specifications for the 7 vessel-domain entities in MarineShield",
  "definitions": {
    
    "Vessel": {
      "type": "object",
      "required": [
        "vessel_id",
        "mmsi",
        "vessel_name",
        "ship_type",
        "length_meters",
        "beam_meters"
      ],
      "properties": {
        "vessel_id": { "type": "string", "format": "uuid" },
        "mmsi": { "type": "string", "pattern": "^[0-9]{9}$" },
        "imo": { "type": ["string", "null"], "pattern": "^[0-9]{7}$" },
        "callsign": { "type": ["string", "null"] },
        "vessel_name": { "type": "string" },
        "ship_type": {
          "type": "string",
          "enum": [
            "TANKER_CRUDE_OIL",
            "TANKER_PRODUCT",
            "TANKER_CHEMICAL",
            "CARGO_CONTAINER",
            "CARGO_BULK_CARRIER",
            "CARGO_GENERAL",
            "FISHING_VESSEL",
            "PASSENGER_FERRY",
            "TUG_SERVICE",
            "SPECIALIZED_OFFSHORE",
            "OTHER",
            "UNKNOWN"
          ]
        },
        "flag_country": { "type": ["string", "null"] },
        "flag_iso2": { "type": ["string", "null"], "pattern": "^[A-Z]{2}$" },
        "length_meters": { "type": "number", "minimum": 1.0, "maximum": 500.0 },
        "beam_meters": { "type": "number", "minimum": 1.0, "maximum": 100.0 },
        "draft_meters": { "type": ["number", "null"], "minimum": 0.0, "maximum": 35.0 },
        "gross_tonnage": { "type": ["integer", "null"], "minimum": 0 },
        "deadweight_tonnage": { "type": ["integer", "null"], "minimum": 0 },
        "risk_profile": {
          "type": "string",
          "enum": ["HIGH_RISK_CARRIER", "MODERATE_RISK", "STANDARD_COMMERCIAL", "LOW_RISK", "UNASSESSED"]
        }
      }
    },

    "AISObservation": {
      "type": "object",
      "required": [
        "observation_id",
        "mmsi",
        "timestamp",
        "latitude",
        "longitude",
        "speed_over_ground_knots",
        "course_over_ground_deg",
        "navigational_status",
        "source_provider"
      ],
      "properties": {
        "observation_id": { "type": "string", "format": "uuid" },
        "mmsi": { "type": "string", "pattern": "^[0-9]{9}$" },
        "timestamp": { "type": "string", "format": "date-time" },
        "latitude": { "type": "number", "minimum": -90.0, "maximum": 90.0 },
        "longitude": { "type": "number", "minimum": -180.0, "maximum": 180.0 },
        "speed_over_ground_knots": { "type": "number", "minimum": 0.0, "maximum": 102.2 },
        "course_over_ground_deg": { "type": "number", "minimum": 0.0, "maximum": 360.0 },
        "heading_deg": { "type": ["number", "null"], "minimum": 0.0, "maximum": 360.0 },
        "navigational_status": {
          "type": "string",
          "enum": [
            "UNDER_WAY_USING_ENGINE",
            "AT_ANCHOR",
            "NOT_UNDER_COMMAND",
            "RESTRICTED_MANOEUVRABILITY",
            "CONSTRAINED_BY_DRAUGHT",
            "MOORED",
            "AGROUND",
            "ENGAGED_IN_FISHING",
            "UNDER_WAY_SAILING",
            "RESERVED_HSC",
            "RESERVED_WIG",
            "AIS_SART_ACTIVE",
            "UNDEFINED"
          ]
        },
        "rate_of_turn_deg_per_min": { "type": ["number", "null"] },
        "source_provider": {
          "type": "string",
          "enum": ["GLOBAL_FISHING_WATCH", "INCOIS", "DG_SHIPPING", "TERRESTRIAL_AIS", "SATELLITE_AIS", "MOCK_SIMULATOR"]
        }
      }
    },

    "AISTrack": {
      "type": "object",
      "required": [
        "track_id",
        "mmsi",
        "time_start",
        "time_end",
        "observations_count",
        "trajectory_geojson",
        "bbox_wgs84",
        "total_distance_km",
        "avg_speed_knots",
        "max_speed_knots"
      ],
      "properties": {
        "track_id": { "type": "string", "format": "uuid" },
        "mmsi": { "type": "string", "pattern": "^[0-9]{9}$" },
        "time_start": { "type": "string", "format": "date-time" },
        "time_end": { "type": "string", "format": "date-time" },
        "observations_count": { "type": "integer", "minimum": 2 },
        "trajectory_geojson": {
          "type": "object",
          "required": ["type", "coordinates"],
          "properties": {
            "type": { "type": "string", "enum": ["LineString"] },
            "coordinates": {
              "type": "array",
              "items": {
                "type": "array",
                "minItems": 3,
                "maxItems": 3,
                "items": { "type": "number" },
                "description": "[longitude, latitude, epoch_timestamp_seconds]"
              },
              "minItems": 2
            }
          }
        },
        "bbox_wgs84": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 4,
          "maxItems": 4,
          "description": "[min_lon, min_lat, max_lon, max_lat]"
        },
        "total_distance_km": { "type": "number", "minimum": 0.0 },
        "avg_speed_knots": { "type": "number", "minimum": 0.0 },
        "max_speed_knots": { "type": "number", "minimum": 0.0 },
        "min_speed_knots": { "type": "number", "minimum": 0.0 },
        "gap_count": { "type": "integer", "minimum": 0 }
      }
    },

    "SARVesselDetection": {
      "type": "object",
      "required": [
        "detection_id",
        "source_granule_id",
        "detection_timestamp",
        "centroid_lat",
        "centroid_lon",
        "bounding_box_geojson",
        "estimated_length_meters",
        "estimated_width_meters",
        "radar_cross_section_db",
        "signal_to_clutter_ratio_db",
        "detection_confidence",
        "polarization_used"
      ],
      "properties": {
        "detection_id": { "type": "string", "format": "uuid" },
        "source_granule_id": { "type": "string" },
        "detection_timestamp": { "type": "string", "format": "date-time" },
        "centroid_lat": { "type": "number", "minimum": -90.0, "maximum": 90.0 },
        "centroid_lon": { "type": "number", "minimum": -180.0, "maximum": 180.0 },
        "bounding_box_geojson": {
          "type": "object",
          "required": ["type", "coordinates"],
          "properties": {
            "type": { "type": "string", "enum": ["Polygon"] },
            "coordinates": { "type": "array" }
          }
        },
        "estimated_length_meters": { "type": "number", "minimum": 5.0, "maximum": 500.0 },
        "estimated_width_meters": { "type": "number", "minimum": 2.0, "maximum": 100.0 },
        "estimated_heading_deg": { "type": ["number", "null"], "minimum": 0.0, "maximum": 360.0 },
        "radar_cross_section_db": { "type": "number" },
        "peak_backscatter_sigma0_db": { "type": "number" },
        "background_clutter_db": { "type": "number" },
        "signal_to_clutter_ratio_db": { "type": "number", "minimum": 0.0 },
        "detection_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "polarization_used": { "type": "string", "enum": ["VH", "VV", "DUAL_POL"] }
      }
    },

    "VesselMatch": {
      "type": "object",
      "required": [
        "match_id",
        "sar_detection_id",
        "matched_mmsi",
        "match_status",
        "match_confidence",
        "distance_offset_meters",
        "timestamp_offset_seconds",
        "heading_delta_deg",
        "speed_delta_knots",
        "dimension_match_score",
        "reconciliation_algorithm"
      ],
      "properties": {
        "match_id": { "type": "string", "format": "uuid" },
        "sar_detection_id": { "type": "string", "format": "uuid" },
        "matched_mmsi": { "type": "string", "pattern": "^[0-9]{9}$" },
        "match_status": {
          "type": "string",
          "enum": ["MATCHED", "UNCERTAIN_MATCH", "UNMATCHED"]
        },
        "match_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "distance_offset_meters": { "type": "number", "minimum": 0.0 },
        "timestamp_offset_seconds": { "type": "number", "minimum": 0.0 },
        "heading_delta_deg": { "type": ["number", "null"], "minimum": 0.0, "maximum": 180.0 },
        "speed_delta_knots": { "type": ["number", "null"], "minimum": 0.0 },
        "dimension_match_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "reconciliation_algorithm": {
          "type": "string",
          "enum": ["DETERMINISTIC_SPATIO_TEMPORAL_HEURISTIC_V1"]
        }
      }
    },

    "UnmatchedVessel": {
      "type": "object",
      "required": [
        "unmatched_id",
        "sar_detection_id",
        "source_granule_id",
        "detection_timestamp",
        "centroid_lat",
        "centroid_lon",
        "estimated_length_meters",
        "estimated_width_meters",
        "detection_confidence",
        "ais_search_radius_km",
        "ais_time_window_minutes",
        "candidate_vessels_searched_count",
        "dark_vessel_confidence"
      ],
      "properties": {
        "unmatched_id": { "type": "string", "format": "uuid" },
        "sar_detection_id": { "type": "string", "format": "uuid" },
        "source_granule_id": { "type": "string" },
        "detection_timestamp": { "type": "string", "format": "date-time" },
        "centroid_lat": { "type": "number", "minimum": -90.0, "maximum": 90.0 },
        "centroid_lon": { "type": "number", "minimum": -180.0, "maximum": 180.0 },
        "estimated_length_meters": { "type": "number", "minimum": 5.0, "maximum": 500.0 },
        "estimated_width_meters": { "type": "number", "minimum": 2.0, "maximum": 100.0 },
        "detection_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "ais_search_radius_km": { "type": "number", "minimum": 1.0, "maximum": 100.0 },
        "ais_time_window_minutes": { "type": "number", "minimum": 5.0, "maximum": 180.0 },
        "candidate_vessels_searched_count": { "type": "integer", "minimum": 0 },
        "dark_vessel_confidence": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "nearest_ais_vessel_mmsi": { "type": ["string", "null"], "pattern": "^[0-9]{9}$" },
        "distance_to_nearest_ais_meters": { "type": ["number", "null"], "minimum": 0.0 }
      }
    },

    "AnomalyEvent": {
      "type": "object",
      "required": [
        "anomaly_id",
        "mmsi",
        "anomaly_type",
        "severity_level",
        "time_start",
        "time_end",
        "duration_seconds",
        "location_start_lat",
        "location_start_lon",
        "geometry_geojson",
        "anomaly_score",
        "context_indicators",
        "description"
      ],
      "properties": {
        "anomaly_id": { "type": "string", "format": "uuid" },
        "mmsi": { "type": "string", "pattern": "^[0-9]{9}$" },
        "anomaly_type": {
          "type": "string",
          "enum": [
            "AIS_TRANSMISSION_GAP",
            "ABNORMAL_SPEED_DROP",
            "COURSE_DEVIATION_LOITERING",
            "SUDDEN_U_TURN",
            "DRAFT_CHANGE_DISCHARGE",
            "SUSPICIOUS_PROXIMITY_RENDEZVOUS"
          ]
        },
        "severity_level": {
          "type": "string",
          "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        },
        "time_start": { "type": "string", "format": "date-time" },
        "time_end": { "type": "string", "format": "date-time" },
        "duration_seconds": { "type": "number", "minimum": 0.0 },
        "location_start_lat": { "type": "number", "minimum": -90.0, "maximum": 90.0 },
        "location_start_lon": { "type": "number", "minimum": -180.0, "maximum": 180.0 },
        "location_end_lat": { "type": ["number", "null"], "minimum": -90.0, "maximum": 90.0 },
        "location_end_lon": { "type": ["number", "null"], "minimum": -180.0, "maximum": 180.0 },
        "geometry_geojson": {
          "type": "object",
          "description": "GeoJSON Point, LineString, or Polygon in EPSG:4326"
        },
        "anomaly_score": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
        "context_indicators": {
          "type": "object",
          "additionalProperties": { "type": ["number", "string", "boolean"] }
        },
        "description": { "type": "string" }
      }
    }
  }
}
```

---

## 4. Entity Specifications & Field Descriptions

### 4.1 `Vessel` (Master Vessel Registry)
- **`vessel_id`** *(UUID, Required)*: Unique surrogate primary key.
- **`mmsi`** *(string 9-digits, Required)*: Maritime Mobile Service Identity.
- **`imo`** *(string 7-digits, Optional)*: Official IMO registration number.
- **`vessel_name`** *(string, Required)*: Vessel commercial name.
- **`ship_type`** *(enum, Required)*: Classified vessel category (`TANKER_CRUDE_OIL`, `TANKER_PRODUCT`, `CARGO_BULK_CARRIER`, etc.). Critical for risk scoring in the Evidence Engine.
- **`length_meters` & `beam_meters`** *(float, Required)*: Physical dimensions used during AIS-SAR dimension reconciliation.
- **`risk_profile`** *(enum, Required)*: Operational risk classification.

### 4.2 `AISObservation` (Instantaneous Point Observation)
- **`observation_id`** *(UUID, Required)*: Unique record identifier.
- **`timestamp`** *(ISO 8601 UTC, Required)*: Transponder broadcast timestamp.
- **`latitude` & `longitude`** *(float, Required)*: Coordinate in `EPSG:4326`.
- **`speed_over_ground_knots`** *(float, Required)*: SOG in knots.
- **`course_over_ground_deg`** *(float, Required)*: COG $[0.0, 360.0)^\circ$.
- **`navigational_status`** *(enum, Required)*: Operational navigation status.

### 4.3 `AISTrack` (Spatial-Temporal Vessel Trajectory)
- **`track_id`** *(UUID, Required)*: Trajectory segment identifier.
- **`trajectory_geojson`** *(GeoJSON LineString, Required)*: Ordered sequence of $[lon, lat, epoch\_time]$ coordinate vertices in `EPSG:4326`.
- **`total_distance_km` & `avg_speed_knots`** *(float, Required)*: Kinematic metrics.
- **`gap_count`** *(integer, Required)*: Number of detected communication gaps ($>30\text{ min}$) along the track.

### 4.4 `SARVesselDetection` (Physical Ship Detection in SAR)
*Owned and produced by **Person 1 (Member 2)**; consumed by **Person 2 (Member 3)**.*
- **`detection_id`** *(UUID, Required)*: Unique detection identifier.
- **`source_granule_id`** *(string, Required)*: Parent SAR scene granule name.
- **`detection_timestamp`** *(ISO 8601 UTC, Required)*: Azimuth zero-Doppler epoch.
- **`centroid_lat` & `centroid_lon`** *(float, Required)*: Detected center position.
- **`estimated_length_meters` & `estimated_width_meters`** *(float, Required)*: Extracted physical radar bounding dimensions.
- **`signal_to_clutter_ratio_db`** *(float, Required)*: Target-to-sea-clutter contrast in $\text{dB}$.
- **`detection_confidence`** *(float $[0.0, 1.0]$, Required)*: Model detection certainty.

### 4.5 `VesselMatch` (Deterministic AIS–SAR Reconciliation)
*Owned and produced by **Person 2 (Member 3)**.*
- **`sar_detection_id`** *(UUID, Required)*: Reference to SAR detection.
- **`matched_mmsi`** *(string 9-digits, Required)*: Correlated AIS vessel.
- **`match_status`** *(enum, Required)*: `MATCHED` or `UNCERTAIN_MATCH`.
- **`distance_offset_meters`** *(float, Required)*: Spatial difference $\Delta d$ between SAR observed position and interpolated AIS track position at $t_{sar}$.
- **`timestamp_offset_seconds`** *(float, Required)*: Time delta $\Delta t$ to nearest verified AIS message.
- **`dimension_match_score`** *(float $[0.0, 1.0]$, Required)*: Geometric compatibility between SAR length/beam and AIS registered dimensions.

### 4.6 `UnmatchedVessel` (Dark Vessel Intelligence)
*Owned and produced by **Person 2 (Member 3)**.*
- **`unmatched_id`** *(UUID, Required)*: Unique dark vessel incident record.
- **`sar_detection_id`** *(UUID, Required)*: SAR vessel observation lacking AIS correlation.
- **`ais_search_radius_km`** *(float, Required)*: Spatial search buffer radius (e.g. $15.0\text{ km}$).
- **`ais_time_window_minutes`** *(float, Required)*: Temporal search buffer ($\pm 30\text{ min}$).
- **`dark_vessel_confidence`** *(float $[0.0, 1.0]$, Required)*: Confidence that absence of AIS was an intentional transponder deactivation rather than satellite reception outage.

### 4.7 `AnomalyEvent` (Vessel Behavior & Transmission Anomalies)
*Owned and produced by **Person 2 (Member 3)**.*
- **`anomaly_id`** *(UUID, Required)*: Unique anomaly event identifier.
- **`mmsi`** *(string 9-digits, Required)*: Subject vessel.
- **`anomaly_type`** *(enum, Required)*:
  - `AIS_TRANSMISSION_GAP`: Significant unannounced blackout during transit.
  - `ABNORMAL_SPEED_DROP`: Sudden deceleration (e.g. dropping from $14\text{ kts} \to 2\text{ kts}$) in open ocean.
  - `COURSE_DEVIATION_LOITERING`: S-curving, circles, or drift patterns indicating discharge/operations.
  - `SUDDEN_U_TURN`: Abrupt $180^\circ$ reversal without port destination.
  - `DRAFT_CHANGE_DISCHARGE`: Major draught alteration between reporting intervals.
  - `SUSPICIOUS_PROXIMITY_RENDEZVOUS`: Two vessels loitering within $500\text{ m}$ (ship-to-ship transfer).
- **`severity_level`** *(enum, Required)*: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- **`anomaly_score`** *(float $[0.0, 1.0]$, Required)*: Behavioral deviation magnitude feeding into the Evidence + Contradiction Engine ($S_{behavior}$).

---

## 5. Sample Canonical Vessel Payloads

```json
{
  "sample_vessel": {
    "vessel_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "mmsi": "412345678",
    "imo": "9384721",
    "callsign": "VRAB8",
    "vessel_name": "PACIFIC GLORY",
    "ship_type": "TANKER_CRUDE_OIL",
    "flag_country": "Liberia",
    "flag_iso2": "LR",
    "length_meters": 274.0,
    "beam_meters": 48.0,
    "draft_meters": 16.5,
    "gross_tonnage": 84500,
    "deadweight_tonnage": 159000,
    "risk_profile": "HIGH_RISK_CARRIER"
  },
  "sample_sar_detection": {
    "detection_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "source_granule_id": "S1A_IW_GRDH_1SDV_20240115T053000_20240115T053025_052110_064D3F_A89B",
    "detection_timestamp": "2024-01-15T05:30:12.500Z",
    "centroid_lat": 18.924510,
    "centroid_lon": 72.821450,
    "bounding_box_geojson": {
      "type": "Polygon",
      "coordinates": [[[72.820, 18.923], [72.823, 18.923], [72.823, 18.926], [72.820, 18.926], [72.820, 18.923]]]
    },
    "estimated_length_meters": 268.0,
    "estimated_width_meters": 45.0,
    "estimated_heading_deg": 142.5,
    "radar_cross_section_db": 42.5,
    "peak_backscatter_sigma0_db": 8.4,
    "background_clutter_db": -22.1,
    "signal_to_clutter_ratio_db": 30.5,
    "detection_confidence": 0.96,
    "polarization_used": "VH"
  },
  "sample_vessel_match": {
    "match_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "sar_detection_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "matched_mmsi": "412345678",
    "match_status": "MATCHED",
    "match_confidence": 0.94,
    "distance_offset_meters": 85.0,
    "timestamp_offset_seconds": 18.0,
    "heading_delta_deg": 3.2,
    "speed_delta_knots": 0.4,
    "dimension_match_score": 0.97,
    "reconciliation_algorithm": "DETERMINISTIC_SPATIO_TEMPORAL_HEURISTIC_V1"
  },
  "sample_unmatched_vessel": {
    "unmatched_id": "c8d3e2f1-4b5a-6c7d-8e9f-0a1b2c3d4e5f",
    "sar_detection_id": "a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d",
    "source_granule_id": "S1A_IW_GRDH_1SDV_20240115T053000_20240115T053025_052110_064D3F_A89B",
    "detection_timestamp": "2024-01-15T05:30:12.500Z",
    "centroid_lat": 19.451200,
    "centroid_lon": 71.912400,
    "estimated_length_meters": 185.0,
    "estimated_width_meters": 32.0,
    "detection_confidence": 0.92,
    "ais_search_radius_km": 15.0,
    "ais_time_window_minutes": 30.0,
    "candidate_vessels_searched_count": 14,
    "dark_vessel_confidence": 0.88,
    "nearest_ais_vessel_mmsi": "352123456",
    "distance_to_nearest_ais_meters": 18450.0
  },
  "sample_anomaly_event": {
    "anomaly_id": "e7b9c1d2-3f4a-5b6c-7d8e-9f0a1b2c3d4e",
    "mmsi": "412345678",
    "anomaly_type": "ABNORMAL_SPEED_DROP",
    "severity_level": "HIGH",
    "time_start": "2024-01-15T02:15:00.000Z",
    "time_end": "2024-01-15T04:45:00.000Z",
    "duration_seconds": 9000.0,
    "location_start_lat": 18.850000,
    "location_start_lon": 72.750000,
    "location_end_lat": 18.890000,
    "location_end_lon": 72.790000,
    "geometry_geojson": {
      "type": "LineString",
      "coordinates": [[72.750, 18.850], [72.770, 18.870], [72.790, 18.890]]
    },
    "anomaly_score": 0.85,
    "context_indicators": {
      "speed_drop_knots": 11.2,
      "previous_speed_knots": 13.8,
      "anomalous_speed_knots": 2.6,
      "distance_to_estimated_release_zone_km": 4.2
    },
    "description": "Vessel exhibited an unannounced speed reduction from 13.8 kts to 2.6 kts in open sea intersecting estimated spill release window."
  }
}
```
