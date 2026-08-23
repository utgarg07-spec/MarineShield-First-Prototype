# Person 1 Backend Request Contracts

**Target Subsystem:** Person 1 Presentation Services (Oil Intelligence & Source Investigation)  
**Authoritative Contracts Reference:** `docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md`  
**Specification Date:** 2026-08-23 (UTC)  
**Status:** AUTHORITATIVE BACKEND REQUEST SPECIFICATION

---

## 1. Executive Summary

This document specifies the exact request payload structures, field validation rules, coordinate reference system (CRS) requirements, and timestamp conventions supported by Person 1's backend implementations in `marineshield/oil_intelligence/` and `marineshield/investigation/`.

These request specifications provide Person 3 with the exact parameter contracts required to mount and wire the FastAPI endpoint handlers replacing the HTTP 501 placeholders:

- `POST /api/v1/oil-intelligence/detect`
- `POST /api/v1/investigation/reconstruct`
- `POST /api/v1/investigation/counterfactual`

---

## 2. Route A: `POST /api/v1/oil-intelligence/detect`

### Canonical Request Payload
```json
{
  "sar_granule_id": "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
  "tile_id": "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train",
  "incident_id": "phase6-val-inc-20260821-001",
  "tile_bounds": [72.0, 18.0, 72.5, 18.5],
  "data_quality": {
    "index": 0.95,
    "quality_flags": []
  },
  "prompts": {
    "box_prompt": [100, 100, 300, 300]
  }
}
```

### Detailed Request Field Specification Table

| Field Name | Type | Required / Optional | Default Value | Allowed Values / Range | Units / Format | Source File & Line | Fixture Source |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `sar_granule_id` | String | Required | N/A | Valid Sentinel-1 Granule ID | String | `marineshield/oil_intelligence/service.py:112` | Person 2 SAR Granule |
| `tile_id` | String | Optional | Auto-generated UUID | Sub-tile ID string | String | `marineshield/oil_intelligence/service.py:111` | Person 2 SAR Tile |
| `incident_id` | String (UUID) | Optional | Auto-generated UUID | Valid UUID v4 string | String | `marineshield/oil_intelligence/service.py:110` | Main Incident Record |
| `tile_bounds` | Array of Float | Optional | `(72.0, 18.0, 72.5, 18.5)` | `[min_lon, min_lat, max_lon, max_lat]` | EPSG:4326 WGS 84 degrees | `marineshield/oil_intelligence/service.py:113` | Person 2 Tile Bounding Box |
| `data_quality` | Object / Float | Optional | `1.0` | DQI score ($0.0 - 1.0$) and quality flag strings | DQI Index | `marineshield/oil_intelligence/service.py:116` | Person 2 SAR Quality Flag |
| `prompts` | Object | Optional | None | `{ "box_prompt": [x1, y1, x2, y2] }` | 512x512 Pixel Bounding Box | `marineshield/oil_intelligence/service.py:161` | Segmentation Candidate Prompt |

---

## 3. Route B: `POST /api/v1/investigation/reconstruct`

### Canonical Request Payload
```json
{
  "spill_centroid": [73.2015, 18.5012],
  "t_observation_utc": "2024-01-20T00:55:41Z",
  "environmental_history": {
    "wind_speed_ms": 8.5,
    "wind_direction_deg": 225.0,
    "current_u_ms": 0.12,
    "current_v_ms": -0.08,
    "lookback_hours": 6.0,
    "wind_dataset_id": "ERA5-REANALYSIS-2024",
    "current_dataset_id": "HYCOM-GLOBAL-2024",
    "data_quality_index": 0.95
  },
  "vessel_observations": [
    {
      "observation_id": "obs-001",
      "vessel_mmsi": "413123456",
      "vessel_name": "Cooperative Vessel MMSI-413123456",
      "vessel_type": "CARGO",
      "timestamp_utc": "2024-01-20T00:10:00Z",
      "latitude": 18.4950,
      "longitude": 73.1950,
      "speed_knots": 12.5,
      "heading_deg": 45.0
    }
  ],
  "ais_coverage_percentage": 100.0,
  "data_quality_index": 0.90,
  "incident_id": "MS-PHASE6-DEV-001",
  "spill_geometry_id": "geom-001",
  "scenario_id": "SCENARIO-LIVE"
}
```

### Detailed Request Field Specification Table

| Field Name | Type | Required / Optional | Default Value | Allowed Values / Range | Units / Format | Source File & Line | Fixture Source |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `spill_centroid` | Tuple `[Float, Float]` | Required | N/A | `[longitude, latitude]` | EPSG:4326 WGS 84 degrees | `marineshield/investigation/engine.py:40` | Person 1 Geometry Centroid |
| `t_observation_utc` | String (ISO 8601) | Required | N/A | RFC 3339 UTC string | `YYYY-MM-DDTHH:MM:SSZ` | `marineshield/investigation/engine.py:41` | SAR Acquisition Timestamp |
| `environmental_history` | Object / Dict | Required | N/A | Environmental parameters or `EnvironmentalHistory` dict | m/s, degrees, DQI | `marineshield/investigation/engine.py:42` | Person 3 Environment Handoff |
| `vessel_observations` | Array of Objects | Optional | `[]` | List of `VesselObservation` objects | AIS Telemetry | `marineshield/investigation/engine.py:43` | Person 2 Member 3 Vessel AIS |
| `ais_coverage_percentage` | Float | Optional | `100.0` | Coverage percentage ($0.0 - 100.0$) | Percent | `marineshield/investigation/engine.py:44` | Person 2 AIS Quality Index |
| `data_quality_index` | Float | Optional | `0.90` | DQI score ($0.0 - 1.0$) | DQI Index | `marineshield/investigation/engine.py:45` | Overall Pipeline DQI |
| `incident_id` | String (UUID) | Optional | Auto-generated UUID | Valid UUID v4 string | String | `marineshield/investigation/engine.py:46` | Main Incident Record |
| `spill_geometry_id` | String | Optional | Auto-generated UUID | Unique geometry ID | String | `marineshield/investigation/engine.py:47` | Detection Geometry Reference |
| `scenario_id` | String | Optional | `"SCENARIO-LIVE"` | Scenario string | String | `marineshield/investigation/engine.py:48` | Replay / Live Scenario Tag |

---

## 4. Route C: `POST /api/v1/investigation/counterfactual`

### Canonical Request Payload
```json
{
  "incident_id": "inc-cf-test-01",
  "spill_geometry_geojson": {
    "type": "Polygon",
    "coordinates": [
      [
        [73.18, 18.48],
        [73.22, 18.48],
        [73.22, 18.52],
        [73.18, 18.52],
        [73.18, 18.48]
      ]
    ]
  },
  "spill_timestamp_utc": "2024-01-20T00:55:41Z",
  "vessel_observations": [
    {
      "observation_id": "obs-001",
      "vessel_mmsi": "413111111",
      "vessel_name": "Primary Suspect MMSI-413111111",
      "vessel_type": "TANKER",
      "timestamp_utc": "2024-01-20T00:10:00Z",
      "latitude": 18.4950,
      "longitude": 73.1950
    },
    {
      "observation_id": "obs-002",
      "vessel_mmsi": "413222222",
      "vessel_name": "Secondary Candidate MMSI-413222222",
      "vessel_type": "CARGO",
      "timestamp_utc": "2024-01-20T00:15:00Z",
      "latitude": 18.5100,
      "longitude": 73.2100
    }
  ],
  "env_history": {
    "wind_speed_ms": 8.0,
    "wind_direction_deg": 220.0,
    "current_u_ms": 0.10,
    "current_v_ms": -0.05,
    "lookback_hours": 6.0
  },
  "replay_timestamp_utc": null
}
```

### Detailed Request Field Specification Table

| Field Name | Type | Required / Optional | Default Value | Allowed Values / Range | Units / Format | Source File & Line | Fixture Source |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| `incident_id` | String (UUID) | Required | N/A | Valid UUID v4 string | String | `marineshield/investigation/counterfactual.py:84` | Main Incident Record |
| `spill_geometry_geojson` | Object (GeoJSON) | Required | N/A | EPSG:4326 GeoJSON Polygon | `[lon, lat]` degrees | `marineshield/investigation/counterfactual.py:85` | Person 1 Detection Feature |
| `spill_timestamp_utc` | String (ISO 8601) | Required | N/A | RFC 3339 UTC string | `YYYY-MM-DDTHH:MM:SSZ` | `marineshield/investigation/counterfactual.py:86` | SAR Acquisition Timestamp |
| `vessel_observations` | Array of Objects | Required | N/A | List of `VesselObservation` objects | AIS Telemetry | `marineshield/investigation/counterfactual.py:87` | Person 2 Member 3 Vessel AIS |
| `env_history` | Object / Dict | Optional | Fallback default dict | Environmental parameters or `EnvironmentalHistory` dict | m/s, degrees, DQI | `marineshield/investigation/counterfactual.py:88` | Person 3 Environment Handoff |
| `replay_timestamp_utc` | String / Null | Optional | `None` | ISO 8601 UTC string or `null` | `YYYY-MM-DDTHH:MM:SSZ` | `marineshield/investigation/counterfactual.py:89` | Replay Time Slicing Tag |
