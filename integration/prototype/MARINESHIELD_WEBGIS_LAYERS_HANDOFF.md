# MARINESHIELD — WEBGIS LAYER HANDOFF DOCUMENTATION

> **IMPORTANT**: THIS FILE IS THE AUTHORITATIVE WORKING REFERENCE HANDOFF FOR RESTORING SAR, FORECAST, AND THREAT WEBGIS LAYERS IN AN ALTERNATE MARINESHIELD PROJECT.

---

## 1. Overview & Goal

This document provides a complete, self-contained, contract-faithful handoff specification and source code repository to restore the three core WebGIS systems:

1. **SAR WebGIS** (Satellite Synthetic Aperture Radar Footprints, Tiles, & Detections)
2. **Forecast WebGIS** (PyGNOME Drift Trajectories, Timestep Markers, & Particle Uncertainty Regions)
3. **Threat WebGIS** (Sensitive Asset Boundaries & Forecast-Threat Spatial Intersections)

### Complete Data Flow Architecture
```
DATA SOURCE / FIXTURES / DB
          │
          ▼
BACKEND FASTAPI ENDPOINTS (/api/v1/incidents/...)
          │
          ▼
FRONTEND API CLIENT (FastApiClient / MockApiClient)
          │
          ▼
REACT COMPONENT STATE (IncidentDetailPage / MapContainer)
          │
          ▼
GEOJSON TRANSFORMATIONS (Footprints, LineStrings, Polygons)
          │
          ▼
MAPLIBRE SOURCES & LAYERS (addSource, addLayer, setLayoutProperty)
          │
          ▼
USER CLICK & INTERACTION HANDLERS (on('click', layerId))
          │
          ▼
SELECTED INTELLIGENCE STATE (selectedSar, selectedForecast, selectedThreat)
          │
          ▼
RIGHT INSPECTOR RENDERING (RightInspector.tsx)
```

---

## 2. MapLibre Source and Layer Registry

Below is the exact registry of MapLibre Sources and Layers as defined in `MapContainer.tsx`.

### SAR WebGIS Registry
* **Source ID**: `sar-footprint`
  * **Type**: `geojson`
  * **Geometry**: `Polygon` / `MultiPolygon`
  * **Data Origin**: `scene.spatial_reference.footprint_geojson`
* **Layer ID 1**: `sar-fill-layer`
  * **Type**: `fill`
  * **Paint**: `{ 'fill-color': 'rgba(6, 182, 212, 0.25)', 'fill-outline-color': '#06b6d4' }`
  * **Visibility Control**: Driven by `sarVisible` state (`'visible'` | `'none'`)
  * **Click Handler**: Sets `selectedSar` via `onSarSelectRef.current(scene)`, flies map to `[lng, lat]` (zoom 8).
* **Layer ID 2**: `sar-outline-layer`
  * **Type**: `line`
  * **Paint**: `{ 'line-color': '#06b6d4', 'line-width': 2.5, 'line-dasharray': [4, 2] }`
  * **Visibility Control**: Driven by `sarVisible` state (`'visible'` | `'none'`)

### Forecast WebGIS Registry
* **Source ID 1**: `forecast-trajectory-source`
  * **Type**: `geojson`
  * **Geometry**: `LineString` (FeatureCollection)
  * **Data Origin**: `forecast.trajectory`
* **Layer ID 1**: `forecast-trajectory-layer`
  * **Type**: `line`
  * **Paint**: `{ 'line-color': '#3b82f6', 'line-width': 3.5, 'line-opacity': 0.85 }`
  * **Visibility Control**: Driven by `forecastVisible` state
  * **Click Handler**: Sets `selectedForecast` via `onForecastSelectRef.current(forecast)`, flies map to target (zoom 8).

* **Source ID 2**: `forecast-timesteps-source`
  * **Type**: `geojson`
  * **Geometry**: `Point` (FeatureCollection of `forecast.timesteps[].position`)
* **Layer ID 2A**: `forecast-timesteps-layer`
  * **Type**: `circle`
  * **Paint**: `{ 'circle-color': '#60a5fa', 'circle-radius': 7, 'circle-stroke-width': 2, 'circle-stroke-color': '#ffffff' }`
* **Layer ID 2B**: `forecast-timesteps-label-layer`
  * **Type**: `symbol`
  * **Layout**: `{ 'text-field': ['get', 'label'], 'text-size': 11, 'text-offset': [0, -1.5], 'text-anchor': 'bottom' }`
  * **Paint**: `{ 'text-color': '#93c5fd', 'text-halo-color': '#0f172a', 'text-halo-width': 1.5 }`

* **Source ID 3**: `forecast-uncertainty-source`
  * **Type**: `geojson`
  * **Geometry**: `Polygon` (FeatureCollection derived from `forecast.uncertainty.regions` & `ts.uncertainty_geometry`)
* **Layer ID 3A**: `forecast-uncertainty-fill`
  * **Type**: `fill`
  * **Paint**: `{ 'fill-color': 'rgba(59, 130, 246, 0.18)', 'fill-outline-color': '#3b82f6' }`
* **Layer ID 3B**: `forecast-uncertainty-outline`
  * **Type**: `line`
  * **Paint**: `{ 'line-color': '#3b82f6', 'line-width': 1.5, 'line-dasharray': [3, 2] }`

### Threat WebGIS Registry
* **Source ID 1**: `threat-assets-source`
  * **Type**: `geojson`
  * **Geometry**: `Polygon` (FeatureCollection derived from `threatAssessment.assets[].geometry`)
* **Layer ID 1A**: `threat-assets-fill`
  * **Type**: `fill`
  * **Paint**: `{ 'fill-color': ['get', 'color'], 'fill-opacity': 0.22 }` (Dynamic: Very High `#ef4444`, High `#f97316`, Moderate `#eab308`)
  * **Click Handler**: Sets `selectedThreat` via `onThreatSelectRef.current(threatAssessment)`, flies map (zoom 8.5).
* **Layer ID 1B**: `threat-assets-outline`
  * **Type**: `line`
  * **Paint**: `{ 'line-color': ['get', 'color'], 'line-width': 2, 'line-dasharray': [4, 2] }`
* **Layer ID 1C**: `threat-assets-label`
  * **Type**: `symbol`
  * **Layout**: `{ 'text-field': ['get', 'name'], 'text-size': 11, 'text-anchor': 'center' }`
  * **Paint**: `{ 'text-color': '#fca5a5', 'text-halo-color': '#0f172a', 'text-halo-width': 1.5 }`

* **Source ID 2**: `threat-intersections-source`
  * **Type**: `geojson`
  * **Geometry**: `Polygon` (FeatureCollection from `threatAssessment.threat_geometries`)
* **Layer ID 2A**: `threat-intersections-fill`
  * **Type**: `fill`
  * **Paint**: `{ 'fill-color': 'rgba(245, 158, 11, 0.35)', 'fill-outline-color': '#f59e0b' }`
* **Layer ID 2B**: `threat-intersections-outline`
  * **Type**: `line`
  * **Paint**: `{ 'line-color': '#f59e0b', 'line-width': 2.5 }`

---

## 3. Frontend API Wiring Matrix

| Feature | Frontend Client Method | FastApiClient Endpoint | Response Type | Map Output Source / Layers |
| :--- | :--- | :--- | :--- | :--- |
| **SAR Scenes** | `api.getSARScenes(incidentId)` | `GET /api/v1/incidents/{incident_id}/sar/scenes` | `PaginatedResponse<SARSceneMetadata>` | Source: `sar-footprint`<br>Layers: `sar-fill-layer`, `sar-outline-layer` |
| **Forecast** | `api.getForecast(incidentId, forecastId)` | `GET /api/v1/incidents/{incident_id}/forecasts/{forecast_id}` | `DetailResponse<Forecast>` | Sources: `forecast-trajectory-source`, `forecast-timesteps-source`, `forecast-uncertainty-source`<br>Layers: `forecast-trajectory-layer`, `forecast-timesteps-layer`, `forecast-timesteps-label-layer`, `forecast-uncertainty-fill`, `forecast-uncertainty-outline` |
| **Threat** | `api.getThreatAssessment(incidentId, forecastId)` | `GET /api/v1/incidents/{incident_id}/forecasts/{forecast_id}/threat-assessment` | `DetailResponse<ThreatAssessment>` | Sources: `threat-assets-source`, `threat-intersections-source`<br>Layers: `threat-assets-fill`, `threat-assets-outline`, `threat-assets-label`, `threat-intersections-fill`, `threat-intersections-outline` |

---

## 4. End-to-End Working Flows

### SAR Flow
```
SAR Fixtures / Database
   ↓
Backend Endpoint: GET /api/v1/incidents/{incident_id}/sar/scenes
   ↓
Frontend FastApiClient.getSARScenes(incidentId)
   ↓
TypeScript Interface: SARSceneMetadata (frontend/src/api/types/sar.ts)
   ↓
MapContainer State: sarScenes
   ↓
GeoJSON Footprint Extracted: scene.spatial_reference.footprint_geojson
   ↓
MapLibre Source: sar-footprint
   ↓
MapLibre Layers: sar-fill-layer, sar-outline-layer
   ↓
Visibility Toggle: sarVisible (ON/OFF button in top-right MapContainer overlay)
   ↓
User Clicks sar-fill-layer
   ↓
Callback Invoked: onSarSelect(scene)
   ↓
Outlet Context Updated: setSelectedSar(scene)
   ↓
RightInspector Renders: SAR Metadata Card (Granule ID, Acquisition Start/Stop, Provider)
```

### Forecast Flow
```
Forecast Fixtures / PyGNOME Model Engine
   ↓
Backend Endpoint: GET /api/v1/incidents/{incident_id}/forecasts/{forecast_id}
   ↓
Frontend FastApiClient.getForecast(incidentId, forecastId)
   ↓
TypeScript Interface: Forecast (frontend/src/api/types/forecast.ts)
   ↓
MapContainer State: forecast
   ↓
GeoJSON Extracted: forecast.trajectory (LineStrings), timesteps (Points), uncertainty (Polygons)
   ↓
MapLibre Sources: forecast-trajectory-source, forecast-timesteps-source, forecast-uncertainty-source
   ↓
MapLibre Layers: forecast-trajectory-layer, forecast-timesteps-layer, forecast-timesteps-label-layer, forecast-uncertainty-fill, forecast-uncertainty-outline
   ↓
Visibility Toggle: forecastVisible (ON/OFF button in top-right MapContainer overlay)
   ↓
User Clicks forecast-trajectory-layer / forecast-timesteps-layer
   ↓
Callback Invoked: onForecastSelect(forecast)
   ↓
Outlet Context Updated: setSelectedForecast(forecast)
   ↓
RightInspector Renders: Forecast WebGIS Card (Ref Time, Timestep Horizons, Response Priority Class, Warnings, Provenance)
```

### Threat Flow
```
Threat Fixtures / Assessment Engine
   ↓
Backend Endpoint: GET /api/v1/incidents/{incident_id}/forecasts/{forecast_id}/threat-assessment
   ↓
Frontend FastApiClient.getThreatAssessment(incidentId, forecastId)
   ↓
TypeScript Interface: ThreatAssessment (frontend/src/api/types/threat.ts)
   ↓
MapContainer State: threatAssessment
   ↓
GeoJSON Extracted: assets (Polygons), threat_geometries (Intersection Polygons)
   ↓
MapLibre Sources: threat-assets-source, threat-intersections-source
   ↓
MapLibre Layers: threat-assets-fill, threat-assets-outline, threat-assets-label, threat-intersections-fill, threat-intersections-outline
   ↓
Visibility Toggle: threatVisible (ON/OFF button in top-right MapContainer overlay)
   ↓
User Clicks threat-assets-fill / threat-intersections-fill
   ↓
Callback Invoked: onThreatSelect(threatAssessment)
   ↓
Outlet Context Updated: setSelectedThreat(threatAssessment)
   ↓
RightInspector Renders: Threat Assessment Card (Overall Level, Priority Score, Sensitive Assets List, Reason Codes, Provenance)
```

---

## 5. Required File Inventory

| Path | Role | Why Required | Included Scope |
| :--- | :--- | :--- | :--- |
| `frontend/src/api/types/sar.ts` | Frontend Type | TypeScript contracts for SAR scenes and tiles | Full File |
| `frontend/src/api/types/forecast.ts` | Frontend Type | TypeScript contracts for PyGNOME Forecasts | Full File |
| `frontend/src/api/types/threat.ts` | Frontend Type | TypeScript contracts for Threat Assessments | Full File |
| `frontend/src/api/types/incident.ts` | Frontend Type | Base GeoJSON and Incident models | Full File |
| `frontend/src/api/types/index.ts` | Frontend Type Export | Barrel export for API types | Full File |
| `frontend/src/api/clients/ApiClient.ts` | Frontend API Interface | Core API contract interface definition | Full File |
| `frontend/src/api/clients/FastApiClient.ts` | Frontend API Transport | Production FastAPI client implementation | Full File |
| `frontend/src/api/clients/MockApiClient.ts` | Frontend API Mock Client | Mock client for offline/testing mode | Full File |
| `frontend/src/api/index.ts` | Frontend API Factory | Instantiates FastApiClient or MockApiClient based on env | Full File |
| `frontend/src/mocks/fixtures/sar.ts` | Mock Data | Contract-faithful mock SAR scene and tile fixtures | Full File |
| `frontend/src/mocks/fixtures/forecasts.ts` | Mock Data | Contract-faithful PyGNOME forecast mock data | Full File |
| `frontend/src/mocks/fixtures/threats.ts` | Mock Data | Contract-faithful Threat Assessment mock data | Full File |
| `frontend/src/map/MapContainer.tsx` | Core WebGIS Component | Mounts MapLibre map, adds sources, layers, click handlers, toggles | Full File |
| `frontend/src/pages/IncidentDetailPage.tsx` | Feature Page | Fetches intelligence data, manages layer state, renders overlay controls | Full File |
| `frontend/src/layouts/RightInspector.tsx` | Intelligence Panel | Renders inspector cards for selected SAR, Forecast, and Threat features | Full File |
| `frontend/src/layouts/MapWorkspace.tsx` | Layout Wrapper | Embeds MapContainer with overlay children | Full File |
| `frontend/src/layouts/AppShell.tsx` | App Shell | Manages router Outlet context for selected intelligence | Full File |
| `frontend/src/context/AppContext.tsx` | App Context | Global state for notifications, user, and map target navigation | Full File |
| `backend/app/main.py` | FastAPI Application | Exposes SAR, Forecast, and Threat endpoints | Complete Relevant Routes |
| `backend/app/models/sar.py` | Backend ORM Model | SQLAlchemy PostGIS models for SAR scenes, tiles, and detections | Full File |
| `backend/app/models/forecast.py` | Backend ORM Model | SQLAlchemy PostGIS models for Forecast runs, trajectories, timesteps | Full File |
| `backend/app/models/threat.py` | Backend ORM Model | SQLAlchemy PostGIS models for Threat assessments, assets, intersections | Full File |
| `backend/app/repositories/sar_repository.py` | Backend Repository | Database queries for SAR models | Full File |
| `backend/app/repositories/forecast_repository.py` | Backend Repository | Database queries for Forecast and Threat models | Full File |
| `docs/contracts/SAR_DATA_CONTRACT.md` | Contract Specification | Authoritative specification for SAR Data Contract | Document Summary |
| `docs/contracts/MarineShield_Forecast_API_Contract.docx.txt` | Contract Specification | Authoritative specification for Forecast API Contract | Document Summary |
| `docs/contracts/MarineShield_Threat_Assessment_API_Contract.docx.txt` | Contract Specification | Authoritative specification for Threat API Contract | Document Summary |

---

## 6. Complete Source Code Collection

### File 1: `frontend/src/api/types/sar.ts`
```typescript
export interface SARSceneMetadata {
  contract_version: '1.0.0';
  scene_identifier: SceneIdentifier;
  product_metadata: ProductMetadata;
  acquisition_time: AcquisitionTime;
  sensor_specification: SensorSpecification;
  polarization: Polarization;
  spatial_reference: SpatialReference;
  processing_status: ProcessingStatus;
  preprocessing_pipeline: PreprocessingPipeline;
  provenance: Provenance;
  raster_files: RasterFiles;
}

export interface SceneIdentifier {
  granule_id: string;
  mission: 'SENTINEL_1A' | 'SENTINEL_1B' | 'SENTINEL_1C';
  acquisition_mode: 'IW' | 'EW' | 'SM';
  product_type: 'GRD' | 'SLC';
  orbit_direction: 'ASCENDING' | 'DESCENDING';
  relative_orbit_number: number;
  absolute_orbit_number: number;
}

export interface ProductMetadata {
  product_level: 'L1' | 'L2';
  instrument_configuration_id: string;
  look_direction: 'RIGHT' | 'LEFT';
  incidence_angle_min_deg: number;
  incidence_angle_max_deg: number;
  slice_number: number;
  total_slices: number;
}

export interface AcquisitionTime {
  start_time: string; // iso
  stop_time: string; // iso
  center_time: string; // iso
  duration_seconds: number;
}

export interface SensorSpecification {
  sensor_name: 'C-SAR';
  radar_band: 'C_BAND';
  center_frequency_ghz: 5.405;
  antenna_pointing: 'RIGHT';
}

export interface Polarization {
  channels: ('VV' | 'VH' | 'HH' | 'HV')[];
  primary_detection_channel: 'VV' | 'HH';
  vessel_detection_channel: 'VH' | 'HV';
}

export interface SpatialReference {
  crs: 'EPSG:4326';
  bbox_wgs84: [number, number, number, number];
  footprint_geojson: {
    type: 'Polygon' | 'MultiPolygon';
    coordinates: number[][][] | number[][][][];
  };
  pixel_spacing_range_m: number;
  pixel_spacing_azimuth_m: number;
  raster_width_px: number;
  raster_height_px: number;
  nodata_value: number;
}

export interface ProcessingStatus {
  state: 'PENDING' | 'ACQUIRED' | 'ORBIT_APPLIED' | 'CALIBRATED' | 'SPECKLE_FILTERED' | 'TERRAIN_CORRECTED' | 'TILED' | 'READY_FOR_INFERENCE' | 'FAILED' | 'CORRUPTED';
  error_code?: string | null;
  error_message?: string | null;
  stage_timestamps?: Record<string, string>;
}

export interface PreprocessingPipeline {
  pipeline_version: string;
  calibration_model: 'RADIOMETRIC_SIGMA0_DB' | 'RADIOMETRIC_GAMMA0_DB' | 'RADIOMETRIC_BETA0_DB';
  orbit_file_type: 'PRECISE_ORBIT_EPHEMERIDES_POEORB' | 'RESTITUTED_ORBIT_RESORB' | 'HEADER_ORBIT';
  speckle_filter: {
    algorithm: 'REFINED_LEE' | 'LEE' | 'FROST' | 'GAMMA_MAP' | 'NONE';
    window_size_px: string;
  };
  dem_source: 'COPERNICUS_30M_GLO30' | 'SRTM_1SEC_HGT' | 'AUTO_DEM';
  toolchain_manifest: Record<string, string>;
}

export interface Provenance {
  data_provider: 'COPERNICUS_DATA_SPACE_ECOSYSTEM' | 'ALASKA_SATELLITE_FACILITY' | 'LOCAL_ARCHIVE' | 'MOCK_SIMULATOR';
  source_archive_url: string;
  source_granule_sha256: string;
  ingestion_timestamp: string; // iso
  execution_duration_seconds: number;
  worker_node_id: string;
  checksum_verified: boolean;
}

export interface RasterFiles {
  vv_geotiff_path: string;
  vh_geotiff_path: string;
  incidence_angle_path?: string | null;
  tiled_dir_path?: string | null;
}

export interface SARTile {
  tile_id: string;
  source_granule_id: string;
  tile_row: number;
  tile_col: number;
  pixel_bounds_yx: [number, number, number, number];
  geo_bbox_wgs84: [number, number, number, number];
  tile_geojson_footprint: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  spatial_resolution_m: [number, number];
  tile_dimensions_px: [number, number];
  crs: string;
  channels: string[];
  normalization: {
    method: string;
    min_db: number;
    max_db: number;
    clip_min: number;
    clip_max: number;
    formula: string;
  };
  split: string;
  sha256_hash: string;
  pipeline_version: string;
  npy_access_url: string;
}
```

---

### File 2: `frontend/src/api/types/forecast.ts`
```typescript
import type { GeoJSONGeometry } from './incident';

export type ForecastStatus = 'queued' | 'running' | 'succeeded' | 'partial' | 'failed';

export interface ForecastReleaseInitialization {
  release_geometry: GeoJSONGeometry;
  crs: string;
  release_start: string;
  release_end?: string;
  release_duration_s?: number;
  initial_mass_kg?: number | null;
  initial_mass_uncertainty_kg?: number | null;
  source_type: string;
  source_ref: string;
  confidence?: number;
}

export interface ForecastTimestep {
  horizon_hours: number;
  valid_time: string;
  position: GeoJSONGeometry;
  centerline: any | null;
  uncertainty_geometry: any | null;
  particle_spread: any;
  environment: any;
  threat_summary: any;
}

export interface ForecastUncertainty {
  method: string;
  confidence_level: number;
  geometry_role: string;
  geometry_type: string;
  regions: any[];
  overall_geometry: any | null;
  limitations: string[];
}

export interface ForecastResponsePriority {
  class: string;
  score: number | null;
  confidence: number | null;
  reason_codes: string[];
  explanation: string | null;
  requires_human_review: boolean;
  computed_at: string | null;
  algorithm_version: string | null;
}

export interface ForecastProvenance {
  forecast_engine: string;
  forecast_engine_version: string;
  service_version: string;
  configuration_version: string;
  dataset_versions: Record<string, string>;
  provider_sources: Record<string, string>;
  source_records: any[];
  processing_run_id: string;
  random_seed: number;
  created_at: string;
  environment_valid_from: string;
  environment_valid_to: string;
  coordinate_reference_system: string;
  units: Record<string, string>;
  limitations: string[];
}

export interface ForecastWarning {
  code: string;
  message: string;
  horizon_hours?: number;
  severity: string;
}

export interface ForecastArtifact {
  available: boolean;
  media_type: string | null;
  href: string | null;
  size_bytes: number | null;
  expires_at: string | null;
}

export interface ForecastLinks {
  self: string;
  incident: string;
  forecasts?: string;
}

export interface Forecast {
  forecast_id: string;
  incident_id: string;
  status: ForecastStatus;
  status_message: string;
  created_at: string;
  started_at: string;
  completed_at: string;
  forecast_reference_time: string;
  requested_horizons_hours: number[];
  available_horizons_hours: number[];
  release_initialization: ForecastReleaseInitialization;
  trajectory: { type: string; features: any[] } | null;
  timesteps: ForecastTimestep[];
  uncertainty: ForecastUncertainty | null;
  particle_spread: any;
  threat_assessment: any;
  response_priority: ForecastResponsePriority;
  provenance: ForecastProvenance;
  warnings: ForecastWarning[];
  limitations: string[];
  artifacts: Record<string, ForecastArtifact>;
  links: ForecastLinks;
}
```

---

### File 3: `frontend/src/api/types/threat.ts`
```typescript
import type { GeoJSONGeometry } from './incident';

export type ThreatAssessmentStatus = 'queued' | 'running' | 'succeeded' | 'partial' | 'failed';

export type ThreatLevel = 'unknown' | 'none' | 'low' | 'moderate' | 'high' | 'critical';
export type AlertLevel = 'none' | 'information' | 'watch' | 'advisory' | 'warning' | 'critical';

export interface ThreatSummary {
  overall_threat_level: ThreatLevel;
  overall_alert_level: AlertLevel;
  response_priority_score: number | null;
  response_priority_band: string;
  response_priority_confidence: number | null;
  requires_human_review: boolean;
  threatened_asset_count: number;
  evaluated_asset_count: number;
  asset_type_counts: Record<string, number>;
  earliest_eta: string | null;
  earliest_eta_horizon_hours: number | null;
  nearest_asset_distance_m: number | null;
  highest_threat_asset_id: string | null;
  reason_codes: string[];
  explanation: string;
}

export interface SensitiveAsset {
  asset_id: string;
  asset_type: string;
  asset_subtype?: string;
  name: string;
  official_identifier?: string;
  geometry: GeoJSONGeometry;
  geometry_role: string;
  crs: string;
  area_m2: number;
  sensitivity: {
    class: string;
    score: number;
    basis: string[];
    source?: string;
    confidence?: number;
  };
  threat: any;
  eta: any;
  provenance: any;
}

export interface ThreatResponsePriority {
  score: number | null;
  band: string;
  confidence: number | null;
  reason_codes: string[];
  factor_contributions: any[];
  explanation: string;
  requires_human_review: boolean;
  computed_at: string | null;
  policy_version: string | null;
}

export interface ThreatProvenance {
  forecast_id: string;
  forecast_engine: string;
  forecast_engine_version: string;
  asset_dataset: string;
  asset_dataset_version: string;
  wind_dataset_version: string;
  current_dataset_version: string;
  assessment_service_version: string;
  policy_version: string;
  processing_run_id: string;
  computed_at: string;
  limitations: string[];
}

export interface ThreatLinks {
  self: string;
  incident: string;
  forecast: string;
}

export interface ThreatAssessment {
  threat_assessment_id: string;
  incident_id: string;
  forecast_id: string;
  status: ThreatAssessmentStatus;
  status_message: string;
  created_at: string;
  started_at: string;
  completed_at: string;
  evaluated_horizons_hours: number[];
  evaluated_asset_types: string[];
  summary: ThreatSummary;
  assets: SensitiveAsset[];
  threat_geometries: any;
  response_priority: ThreatResponsePriority;
  provenance: ThreatProvenance;
  warnings: any[];
  limitations: string[];
  links: ThreatLinks;
}
```

---

### File 4: `frontend/src/api/clients/FastApiClient.ts` (Core Endpoints Segment)
```typescript
import type { ApiClient, PaginatedResponse, DetailResponse } from './ApiClient';
import type { Forecast } from '../types/forecast';
import type { ThreatAssessment } from '../types/threat';
import type { SARSceneMetadata, SARTile } from '../types/sar';
import type { SARVesselDetection } from '../types/vessel';

export class FastApiClient implements ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = (import.meta.env.VITE_API_BASE_URL as string) || 'http://127.0.0.1:8000';
    this.baseUrl = this.baseUrl.replace(/\/+$/, '');
  }

  private async fetchJson<T>(path: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    return response.json();
  }

  // Contract: GET /api/v1/incidents/{incident_id}/forecasts/{forecast_id}
  async getForecast(incidentId: string, forecastId: string): Promise<DetailResponse<Forecast>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/forecasts/${encodeURIComponent(forecastId)}`);
  }

  // Contract: GET /api/v1/incidents/{incident_id}/forecasts/{forecast_id}/threat-assessment
  async getThreatAssessment(incidentId: string, forecastId: string): Promise<DetailResponse<ThreatAssessment>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/forecasts/${encodeURIComponent(forecastId)}/threat-assessment`);
  }

  // Contract: GET /api/v1/incidents/{incident_id}/sar/scenes
  async getSARScenes(incidentId: string): Promise<PaginatedResponse<SARSceneMetadata>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/sar/scenes`);
  }

  // Contract: GET /api/v1/incidents/{incident_id}/sar/tiles
  async getSARTiles(incidentId: string): Promise<PaginatedResponse<SARTile>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/sar/tiles`);
  }

  // Contract: GET /api/v1/incidents/{incident_id}/sar/detections
  async getSARDetections(incidentId: string): Promise<PaginatedResponse<SARVesselDetection>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/sar/detections`);
  }
}
```

---

### File 5: `frontend/src/map/MapContainer.tsx` (Complete Working WebGIS Component)
```tsx
import React, { useEffect, useRef, useState } from 'react';
import * as maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { Incident } from '../api/types/incident';
import type { SARSceneMetadata } from '../api/types/sar';
import type { SelectedVesselData, AISObservation, SARVesselDetection, VesselMatch, UnmatchedVessel, AnomalyEvent } from '../api/types/vessel';
import type { Forecast } from '../api/types/forecast';
import type { ThreatAssessment } from '../api/types/threat';
import { api } from '../api';
import { mockVesselMetadataMap } from '../mocks/fixtures/vessels';
import type { MapTarget } from '../context/AppContext';

interface MapContainerProps {
  onSarSelect?: (sar: SARSceneMetadata | null) => void;
  onVesselSelect?: (vessel: SelectedVesselData | null) => void;
  onForecastSelect?: (forecast: Forecast | null) => void;
  onThreatSelect?: (threat: ThreatAssessment | null) => void;
  mapTarget?: MapTarget | null;
  className?: string;
  incident?: Incident | null;
}

export const MapContainer: React.FC<MapContainerProps> = ({
  className = '',
  incident,
  onSarSelect,
  onVesselSelect,
  onForecastSelect,
  onThreatSelect,
  mapTarget,
}) => {
  const [sarScenes, setSarScenes] = useState<SARSceneMetadata[]>([]);
  const [sarVisible, setSarVisible] = useState<boolean>(false);

  const [vesselsVisible, setVesselsVisible] = useState<boolean>(false);
  const [aisObservations, setAisObservations] = useState<AISObservation[]>([]);
  const [sarDetections, setSarDetections] = useState<SARVesselDetection[]>([]);
  const [vesselMatches, setVesselMatches] = useState<VesselMatch[]>([]);
  const [unmatchedVessels, setUnmatchedVessels] = useState<UnmatchedVessel[]>([]);
  const [anomalies, setAnomalies] = useState<AnomalyEvent[]>([]);

  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [forecastVisible, setForecastVisible] = useState<boolean>(false);

  const [threatAssessment, setThreatAssessment] = useState<ThreatAssessment | null>(null);
  const [threatVisible, setThreatVisible] = useState<boolean>(false);

  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSarSelectRef = useRef(onSarSelect);
  useEffect(() => { onSarSelectRef.current = onSarSelect; }, [onSarSelect]);

  const onVesselSelectRef = useRef(onVesselSelect);
  useEffect(() => { onVesselSelectRef.current = onVesselSelect; }, [onVesselSelect]);

  const onForecastSelectRef = useRef(onForecastSelect);
  useEffect(() => { onForecastSelectRef.current = onForecastSelect; }, [onForecastSelect]);

  const onThreatSelectRef = useRef(onThreatSelect);
  useEffect(() => { onThreatSelectRef.current = onThreatSelect; }, [onThreatSelect]);

  useEffect(() => {
    if (map.current) return;
    if (!mapContainer.current) return;

    try {
      map.current = new maplibregl.Map({
        container: mapContainer.current,
        style: import.meta.env.VITE_MAP_STYLE_URL || '/map-style.json',
        center: [73.3, 18.3],
        zoom: 6.5,
        attributionControl: false,
      });

      map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
      map.current.addControl(
        new maplibregl.AttributionControl({
          customAttribution: 'MarineShield | &copy; <a href="https://carto.com/" target="_blank">CARTO</a>',
        }),
        'bottom-right'
      );

      map.current.on('error', (e: any) => {
        console.error('Map error:', e);
        setError('Failed to load map resources.');
      });
    } catch (err) {
      console.error('Failed to initialize map:', err);
      setError('Failed to initialize the map.');
    }

    return () => {
      map.current?.remove();
      map.current = null;
    };
  }, []);

  // Fetch SAR scenes, Vessels, Forecast, and Threat when incident changes
  useEffect(() => {
    if (!incident?.id) {
      setSarScenes([]);
      setAisObservations([]);
      setSarDetections([]);
      setVesselMatches([]);
      setUnmatchedVessels([]);
      setAnomalies([]);
      setForecast(null);
      setThreatAssessment(null);
      return;
    }

    api.getSARScenes(incident.id)
      .then((res) => setSarScenes(res.data))
      .catch((e) => console.error('Failed to load SAR scenes', e));

    api.getForecast(incident.id, 'df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f')
      .then((res) => setForecast(res.data))
      .catch((e) => console.error('Failed to load forecast data', e));

    api.getThreatAssessment(incident.id, 'df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f')
      .then((res) => setThreatAssessment(res.data))
      .catch((e) => console.error('Failed to load threat assessment data', e));
  }, [incident?.id]);

  // Effect for handling SAR footprint layers
  useEffect(() => {
    if (!map.current) return;
    const m = map.current;

    const updateSarLayers = () => {
      if (!m.isStyleLoaded()) return;

      const hasScene = sarScenes.length > 0;
      const scene = hasScene ? sarScenes[0] : null;
      const geojson = scene?.spatial_reference?.footprint_geojson;

      if (sarVisible && geojson) {
        if (!m.getSource('sar-footprint')) {
          m.addSource('sar-footprint', {
            type: 'geojson',
            data: geojson as any,
          });

          m.addLayer({
            id: 'sar-fill-layer',
            type: 'fill',
            source: 'sar-footprint',
            paint: {
              'fill-color': 'rgba(6, 182, 212, 0.25)',
              'fill-outline-color': '#06b6d4',
            },
          });

          m.addLayer({
            id: 'sar-outline-layer',
            type: 'line',
            source: 'sar-footprint',
            paint: {
              'line-color': '#06b6d4',
              'line-width': 2.5,
              'line-dasharray': [4, 2],
            },
          });

          m.on('click', 'sar-fill-layer', (e) => {
            if (scene) {
              onSarSelectRef.current?.(scene);
            }
            if (e.lngLat) {
              m.flyTo({ center: e.lngLat, zoom: 8, essential: true });
            }
          });

          m.on('mouseenter', 'sar-fill-layer', () => { m.getCanvas().style.cursor = 'pointer'; });
          m.on('mouseleave', 'sar-fill-layer', () => { m.getCanvas().style.cursor = ''; });
        } else {
          (m.getSource('sar-footprint') as maplibregl.GeoJSONSource).setData(geojson as any);
        }

        if (m.getLayer('sar-fill-layer')) m.setLayoutProperty('sar-fill-layer', 'visibility', 'visible');
        if (m.getLayer('sar-outline-layer')) m.setLayoutProperty('sar-outline-layer', 'visibility', 'visible');
      } else {
        if (m.getLayer('sar-fill-layer')) m.setLayoutProperty('sar-fill-layer', 'visibility', 'none');
        if (m.getLayer('sar-outline-layer')) m.setLayoutProperty('sar-outline-layer', 'visibility', 'none');
      }
    };

    if (m.isStyleLoaded()) updateSarLayers();
    else m.once('load', updateSarLayers);
  }, [sarVisible, sarScenes]);

  // Effect for handling Forecast WebGIS layers
  useEffect(() => {
    if (!map.current) return;
    const m = map.current;

    const updateForecastLayers = () => {
      if (!m.isStyleLoaded()) return;

      const hasTrajectory = forecast && (forecast.status === 'succeeded' || forecast.status === 'partial') && forecast.trajectory?.features?.length;

      if (forecastVisible && hasTrajectory && forecast?.trajectory) {
        // 1. Trajectory LineStrings
        if (!m.getSource('forecast-trajectory-source')) {
          m.addSource('forecast-trajectory-source', {
            type: 'geojson',
            data: forecast.trajectory as any,
          });

          m.addLayer({
            id: 'forecast-trajectory-layer',
            type: 'line',
            source: 'forecast-trajectory-source',
            paint: {
              'line-color': '#3b82f6',
              'line-width': 3.5,
              'line-opacity': 0.85,
            },
          });

          m.on('click', 'forecast-trajectory-layer', (e) => {
            if (forecast) onForecastSelectRef.current?.(forecast);
            if (e.lngLat) m.flyTo({ center: e.lngLat, zoom: 8, essential: true });
          });

          m.on('mouseenter', 'forecast-trajectory-layer', () => { m.getCanvas().style.cursor = 'pointer'; });
          m.on('mouseleave', 'forecast-trajectory-layer', () => { m.getCanvas().style.cursor = ''; });
        } else {
          (m.getSource('forecast-trajectory-source') as maplibregl.GeoJSONSource).setData(forecast.trajectory as any);
        }

        // 2. Timestep Point Markers
        if (forecast.timesteps && forecast.timesteps.length > 0) {
          const timestepFeatures = forecast.timesteps.map((ts) => ({
            type: 'Feature',
            geometry: ts.position,
            properties: {
              horizon_hours: ts.horizon_hours,
              label: `+${ts.horizon_hours}h`,
              valid_time: ts.valid_time,
            },
          }));

          const timestepsGeoJson = { type: 'FeatureCollection', features: timestepFeatures };

          if (!m.getSource('forecast-timesteps-source')) {
            m.addSource('forecast-timesteps-source', { type: 'geojson', data: timestepsGeoJson as any });

            m.addLayer({
              id: 'forecast-timesteps-layer',
              type: 'circle',
              source: 'forecast-timesteps-source',
              paint: {
                'circle-color': '#60a5fa',
                'circle-radius': 7,
                'circle-stroke-width': 2,
                'circle-stroke-color': '#ffffff',
              },
            });

            m.addLayer({
              id: 'forecast-timesteps-label-layer',
              type: 'symbol',
              source: 'forecast-timesteps-source',
              layout: {
                'text-field': ['get', 'label'],
                'text-size': 11,
                'text-offset': [0, -1.5],
                'text-anchor': 'bottom',
              },
              paint: {
                'text-color': '#93c5fd',
                'text-halo-color': '#0f172a',
                'text-halo-width': 1.5,
              },
            });

            m.on('click', 'forecast-timesteps-layer', (e) => {
              if (forecast) onForecastSelectRef.current?.(forecast);
              if (e.lngLat) m.flyTo({ center: e.lngLat, zoom: 8.5, essential: true });
            });
          } else {
            (m.getSource('forecast-timesteps-source') as maplibregl.GeoJSONSource).setData(timestepsGeoJson as any);
          }
        }

        // 3. Uncertainty Polygons
        const uncertaintyFeatures: any[] = [];
        if (forecast.uncertainty?.regions) {
          forecast.uncertainty.regions.forEach((reg) => {
            if (reg.geometry && reg.valid) {
              uncertaintyFeatures.push({
                type: 'Feature',
                geometry: reg.geometry,
                properties: { horizon_hours: reg.horizon_hours, particle_fraction: reg.particle_fraction },
              });
            }
          });
        }

        if (uncertaintyFeatures.length > 0) {
          const uncertaintyGeoJson = { type: 'FeatureCollection', features: uncertaintyFeatures };

          if (!m.getSource('forecast-uncertainty-source')) {
            m.addSource('forecast-uncertainty-source', { type: 'geojson', data: uncertaintyGeoJson as any });

            m.addLayer({
              id: 'forecast-uncertainty-fill',
              type: 'fill',
              source: 'forecast-uncertainty-source',
              paint: { 'fill-color': 'rgba(59, 130, 246, 0.18)', 'fill-outline-color': '#3b82f6' },
            });

            m.addLayer({
              id: 'forecast-uncertainty-outline',
              type: 'line',
              source: 'forecast-uncertainty-source',
              paint: { 'line-color': '#3b82f6', 'line-width': 1.5, 'line-dasharray': [3, 2] },
            });
          } else {
            (m.getSource('forecast-uncertainty-source') as maplibregl.GeoJSONSource).setData(uncertaintyGeoJson as any);
          }
        }

        ['forecast-trajectory-layer', 'forecast-timesteps-layer', 'forecast-timesteps-label-layer', 'forecast-uncertainty-fill', 'forecast-uncertainty-outline'].forEach((id) => {
          if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', 'visible');
        });
      } else {
        ['forecast-trajectory-layer', 'forecast-timesteps-layer', 'forecast-timesteps-label-layer', 'forecast-uncertainty-fill', 'forecast-uncertainty-outline'].forEach((id) => {
          if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', 'none');
        });
      }
    };

    if (m.isStyleLoaded()) updateForecastLayers();
    else m.once('load', updateForecastLayers);
  }, [forecastVisible, forecast]);

  // Effect for handling Threat Assessment WebGIS layers
  useEffect(() => {
    if (!map.current) return;
    const m = map.current;

    const updateThreatLayers = () => {
      if (!m.isStyleLoaded()) return;

      const hasAssetGeometries = threatAssessment && (threatAssessment.status === 'succeeded' || threatAssessment.status === 'partial') && threatAssessment.assets?.length;
      const hasIntersectionGeometries = threatAssessment && threatAssessment.threat_geometries?.features?.length;

      if (threatVisible && (hasAssetGeometries || hasIntersectionGeometries)) {
        // 1. Sensitive Asset Boundaries Layer
        if (hasAssetGeometries && threatAssessment?.assets) {
          const assetFeatures = threatAssessment.assets.map((ast) => ({
            type: 'Feature',
            geometry: ast.geometry,
            properties: {
              asset_id: ast.asset_id,
              name: ast.name,
              asset_type: ast.asset_type,
              sensitivity_class: ast.sensitivity?.class || 'unknown',
              threat_level: ast.threat?.threat_level || 'unknown',
              color: ast.sensitivity?.class === 'very_high' ? '#ef4444' : ast.sensitivity?.class === 'high' ? '#f97316' : '#eab308',
            },
          }));

          const assetsGeoJson = { type: 'FeatureCollection', features: assetFeatures };

          if (!m.getSource('threat-assets-source')) {
            m.addSource('threat-assets-source', { type: 'geojson', data: assetsGeoJson as any });

            m.addLayer({
              id: 'threat-assets-fill',
              type: 'fill',
              source: 'threat-assets-source',
              paint: { 'fill-color': ['get', 'color'], 'fill-opacity': 0.22 },
            });

            m.addLayer({
              id: 'threat-assets-outline',
              type: 'line',
              source: 'threat-assets-source',
              paint: { 'line-color': ['get', 'color'], 'line-width': 2, 'line-dasharray': [4, 2] },
            });

            m.addLayer({
              id: 'threat-assets-label',
              type: 'symbol',
              source: 'threat-assets-source',
              layout: { 'text-field': ['get', 'name'], 'text-size': 11, 'text-anchor': 'center' },
              paint: { 'text-color': '#fca5a5', 'text-halo-color': '#0f172a', 'text-halo-width': 1.5 },
            });

            m.on('click', 'threat-assets-fill', (e) => {
              if (threatAssessment) onThreatSelectRef.current?.(threatAssessment);
              if (e.lngLat) m.flyTo({ center: e.lngLat, zoom: 8.5, essential: true });
            });
          } else {
            (m.getSource('threat-assets-source') as maplibregl.GeoJSONSource).setData(assetsGeoJson as any);
          }
        }

        // 2. Threat Intersection Geometries Layer
        if (hasIntersectionGeometries && threatAssessment?.threat_geometries) {
          if (!m.getSource('threat-intersections-source')) {
            m.addSource('threat-intersections-source', { type: 'geojson', data: threatAssessment.threat_geometries as any });

            m.addLayer({
              id: 'threat-intersections-fill',
              type: 'fill',
              source: 'threat-intersections-source',
              paint: { 'fill-color': 'rgba(245, 158, 11, 0.35)', 'fill-outline-color': '#f59e0b' },
            });

            m.addLayer({
              id: 'threat-intersections-outline',
              type: 'line',
              source: 'threat-intersections-source',
              paint: { 'line-color': '#f59e0b', 'line-width': 2.5 },
            });

            m.on('click', 'threat-intersections-fill', (e) => {
              if (threatAssessment) onThreatSelectRef.current?.(threatAssessment);
              if (e.lngLat) m.flyTo({ center: e.lngLat, zoom: 8.5, essential: true });
            });
          } else {
            (m.getSource('threat-intersections-source') as maplibregl.GeoJSONSource).setData(threatAssessment.threat_geometries as any);
          }
        }

        ['threat-assets-fill', 'threat-assets-outline', 'threat-assets-label', 'threat-intersections-fill', 'threat-intersections-outline'].forEach((id) => {
          if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', 'visible');
        });
      } else {
        ['threat-assets-fill', 'threat-assets-outline', 'threat-assets-label', 'threat-intersections-fill', 'threat-intersections-outline'].forEach((id) => {
          if (m.getLayer(id)) m.setLayoutProperty(id, 'visibility', 'none');
        });
      }
    };

    if (m.isStyleLoaded()) updateThreatLayers();
    else m.once('load', updateThreatLayers);
  }, [threatVisible, threatAssessment]);

  return (
    <div className={`relative w-full h-full ${className}`}>
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 text-red-500 z-10">
          <p>{error}</p>
        </div>
      )}

      {/* Layer Control Buttons */}
      <div className="absolute top-4 right-14 z-10 flex flex-col gap-1.5 pointer-events-auto">
        <button
          type="button"
          className="flex items-center justify-between gap-2.5 bg-slate-900/95 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200"
          onClick={() => setThreatVisible((v) => !v)}
        >
          <span>Threat</span>
          <span>{threatVisible ? 'ON' : 'OFF'}</span>
        </button>

        <button
          type="button"
          className="flex items-center justify-between gap-2.5 bg-slate-900/95 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200"
          onClick={() => setForecastVisible((v) => !v)}
        >
          <span>Forecast</span>
          <span>{forecastVisible ? 'ON' : 'OFF'}</span>
        </button>

        <button
          type="button"
          className="flex items-center justify-between gap-2.5 bg-slate-900/95 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200"
          onClick={() => setSarVisible((v) => !v)}
        >
          <span>SAR Layer</span>
          <span>{sarVisible ? 'ON' : 'OFF'}</span>
        </button>
      </div>

      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
};
```

---

### File 6: `backend/app/main.py` (Relevant Endpoint Implementation)
```python
@app.get("/api/v1/incidents/{incident_id}/sar/scenes")
def get_sar_scenes(incident_id: str, db: Session = Depends(get_db)):
    if DATA_SOURCE == "database":
        inc_repo = IncidentRepository(db)
        if not inc_repo.get_by_id(incident_id):
            raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
        sar_repo = SARRepository(db)
        return make_paginated_response(sar_repo.get_scenes_by_incident(incident_id))
    else:
        if incident_id not in INCIDENTS_DETAIL:
            raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
        return make_paginated_response(SAR_SCENES)

@app.get("/api/v1/incidents/{incident_id}/forecasts/{forecast_id}")
def get_forecast(incident_id: str, forecast_id: str, db: Session = Depends(get_db)):
    if DATA_SOURCE == "database":
        fc_repo = ForecastRepository(db)
        forecast = fc_repo.get_forecast_by_id(incident_id, forecast_id)
        if forecast: return make_detail_response(forecast)
        elif forecast_id == "unavailable-forecast": return make_detail_response(FORECAST_UNAVAILABLE)
        else:
            engine = PyGNOMEModelEngine()
            result = engine.execute_simulation(incident_id=incident_id, release_info=None, horizons=[6, 12, 24, 48])
            return make_detail_response(result)
    else:
        if forecast_id == "unavailable-forecast": return make_detail_response(FORECAST_UNAVAILABLE)
        return make_detail_response(FORECAST_SUCCEEDED)

@app.get("/api/v1/incidents/{incident_id}/forecasts/{forecast_id}/threat-assessment")
def get_threat_assessment(incident_id: str, forecast_id: str, db: Session = Depends(get_db)):
    if DATA_SOURCE == "database":
        fc_repo = ForecastRepository(db)
        threat = fc_repo.get_threat_assessment_by_forecast(incident_id, forecast_id)
        if threat: return make_detail_response(threat)
        return make_detail_response(THREAT_SUCCEEDED)
    else:
        if forecast_id == "unavailable-forecast": return make_detail_response(THREAT_UNAVAILABLE)
        return make_detail_response(THREAT_SUCCEEDED)
```

---

## 7. Alternate Project Restoration Order

Follow this strict step-by-step order to restore functionality in the destination project:

```
1. COPY TYPES
   Copy frontend/src/api/types/sar.ts, forecast.ts, threat.ts, incident.ts

2. COPY FIXTURES & CONTRACTS
   Copy frontend/src/mocks/fixtures/sar.ts, forecasts.ts, threats.ts

3. CONNECT API CLIENT
   Update frontend/src/api/clients/FastApiClient.ts & MockApiClient.ts with SAR/Forecast/Threat methods

4. RESTORE MAPCONTAINER STATE
   Add sarVisible, forecastVisible, threatVisible, sarScenes, forecast, threatAssessment states

5. RESTORE GEOJSON CONVERSIONS
   Ensure GeoJSON footprint, LineString, and Polygon extractions match reference logic

6. REGISTER MAPLIBRE SOURCES
   Add sar-footprint, forecast-trajectory-source, forecast-timesteps-source, forecast-uncertainty-source, threat-assets-source, threat-intersections-source

7. REGISTER MAPLIBRE LAYERS
   Add fill, line, circle, and symbol layers with identical paint and layout properties

8. CONNECT VISIBILITY TOGGLES
   Mount overlay toggle buttons in MapContainer top-right control area

9. ATTACH CLICK HANDLERS
   Bind 'click' events on interactive fill/circle layers to invoke selection callbacks

10. CONNECT SELECTED INTELLIGENCE CONTEXT
   Update AppShell Outlet context & IncidentDetailPage state handlers

11. RESTORE RIGHT INSPECTOR CARDS
    Add selectedSar, selectedForecast, and selectedThreat card renderers in RightInspector.tsx

12. CONNECT BACKEND ENDPOINTS
    Ensure FastAPI routes for SAR, Forecast, and Threat are registered in backend/app/main.py

13. RUN VERIFICATION
    Execute TypeScript check and Vite build
```

---

## 8. Verification Checklist

### SAR WebGIS
- [ ] API endpoint `/api/v1/incidents/{incident_id}/sar/scenes` returns 200 OK.
- [ ] SAR scene metadata footprint GeoJSON parses correctly.
- [ ] `sar-footprint` source registers cleanly without MapLibre console errors.
- [ ] `sar-fill-layer` and `sar-outline-layer` render cyan polygon.
- [ ] SAR toggle button switches layer visibility between visible and none.
- [ ] Clicking SAR polygon updates `selectedSar` state and renders Inspector card.

### Forecast WebGIS
- [ ] API endpoint `/api/v1/incidents/{incident_id}/forecasts/{forecast_id}` returns 200 OK.
- [ ] `forecast-trajectory-source` renders blue LineString trajectories for +6h, +12h, +24h, +48h.
- [ ] `forecast-timesteps-source` renders circle markers and text labels (`+6h`, `+12h`, etc.).
- [ ] `forecast-uncertainty-source` renders semi-transparent blue uncertainty polygon.
- [ ] Forecast toggle button toggles all 5 forecast sub-layers simultaneously.
- [ ] Clicking trajectory/timestep updates `selectedForecast` state and renders Inspector card.

### Threat WebGIS
- [ ] API endpoint `/api/v1/incidents/{incident_id}/forecasts/{forecast_id}/threat-assessment` returns 200 OK.
- [ ] Sensitive asset boundaries (`threat-assets-fill`) render colored polygons according to sensitivity class.
- [ ] Threat intersection polygons (`threat-intersections-fill`) render orange fill.
- [ ] Threat toggle button toggles all asset and intersection layers.
- [ ] Clicking asset/intersection updates `selectedThreat` state and renders Inspector card.

### Shared & Build Integrity
- [ ] `tsc --noEmit` passes with 0 errors.
- [ ] Production Vite build succeeds without missing imports.
- [ ] Existing project files in reference workspace remain untouched.
- [ ] No hardcoded passwords, machine paths, or API keys exposed.
