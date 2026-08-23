// Contract: MarineShield_Incident_API_Contract.docx
// All types mirror the authoritative JSON schemas exactly.

export type IncidentStatus =
  | 'new'
  | 'verifying'
  | 'investigating'
  | 'attributing'
  | 'forecasting'
  | 'threat_assessment'
  | 'response_prioritized'
  | 'human_review'
  | 'reported'
  | 'closed'
  | 'reopened'
  | 'unknown';

export type SeverityClass = 'unknown' | 'low' | 'moderate' | 'high' | 'critical';
export type PriorityClass = 'unknown' | 'P1' | 'P2' | 'P3' | 'P4';

export interface GeoJSONGeometry {
  type: 'Point' | 'Polygon' | 'MultiPolygon' | 'LineString';
  coordinates: any[];
}

export interface IncidentSeverity {
  class: SeverityClass;
  score: number | null;
  confidence: number | null;
  basis: string[];
  as_of: string | null; // RFC 3339
}

export interface IncidentPriority {
  class: PriorityClass;
  score: number | null;
  confidence: number | null;
  reason_codes: string[];
  explanation: string | null;
  requires_human_review: boolean;
  computed_at: string | null; // RFC 3339
  algorithm_version: string | null;
}

export interface IncidentLocation {
  geometry: GeoJSONGeometry | null;
  crs: string; // 'EPSG:4326'
  accuracy_m?: number | null;
  source?: string;
  source_ref?: string | null;
}

export interface SourceRecord {
  type: string;
  id: string;
}

export interface IncidentProvenance {
  created_from: string;
  source_records: SourceRecord[];
  source_systems: string[];
  observation_time_start: string | null; // RFC 3339
  observation_time_end: string | null; // RFC 3339
  ingested_at: string; // RFC 3339
  pipeline_version: string | null;
  dataset_versions: Record<string, string>;
  processing_run_id: string | null;
  is_complete: boolean;
  limitations: string[];
  // Extension for frontend provenance tracking (not in canonical contract)
  data_mode?: 'LIVE_API' | 'MOCK_HYBRID' | 'SIMULATION';
}

export interface IncidentLinks {
  self: string;
  detail?: string;
  collection?: string;
}

export interface RelatedResourceSummary {
  count: number;
  items?: Array<{ id: string; href: string }>;
  latest_id?: string;
  href?: string;
}

/**
 * IncidentSummary — returned by GET /api/v1/incidents
 * Per contract: excludes large SAR rasters, full vessel histories,
 * full evidence collections, full forecast trajectories, or report files.
 */
export interface IncidentSummary {
  id: string;
  reference: string;
  title: string | null;
  status: IncidentStatus;
  status_label: string;
  severity: IncidentSeverity;
  response_priority: IncidentPriority;
  location: IncidentLocation;
  observation_time_start: string | null; // RFC 3339
  observation_time_end: string | null; // RFC 3339
  created_at: string; // RFC 3339
  updated_at: string; // RFC 3339
  last_activity_at: string; // RFC 3339
  provenance: IncidentProvenance;
  links: IncidentLinks;
}

/**
 * Incident — returned by GET /api/v1/incidents/{incident_id}
 * Extends summary with description, status transition metadata,
 * and related resource summaries.
 */
export interface Incident extends IncidentSummary {
  description?: string | null;
  status_changed_at?: string | null; // RFC 3339
  status_reason?: string | null;
  closed_at?: string | null; // RFC 3339
  related?: {
    spill?: RelatedResourceSummary;
    forecast?: RelatedResourceSummary;
    threats?: RelatedResourceSummary;
    vessels?: RelatedResourceSummary;
    evidence?: RelatedResourceSummary;
  };
}
