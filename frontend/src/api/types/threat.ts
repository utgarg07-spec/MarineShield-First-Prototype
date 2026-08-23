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
