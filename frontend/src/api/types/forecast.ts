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
  activeTimestep?: ForecastTimestep | null;
}
