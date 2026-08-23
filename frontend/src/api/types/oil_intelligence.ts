// Authoritative Person 1 Presentation Contract Types for Oil Intelligence
// Documented in docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md

export type SpillDetectionStatus =
  | 'OIL_DETECTED'
  | 'LOOKALIKE_REJECTED'
  | 'UNCERTAIN_ANALYSIS'
  | 'ABSTAINED'
  | 'NO_CANDIDATE_FOUND';

export type LookalikeClass =
  | 'PETROLEUM_OIL'
  | 'BIOGENIC_SLICK'
  | 'LOW_WIND_AREA'
  | 'SHIP_WAKE'
  | 'NATURAL_FILM'
  | 'UNCERTAIN';

export type PipelineDecision = 'CONFIRM_AS_OIL' | 'REJECT_AS_LOOKALIKE' | 'FLAG_FOR_HUMAN_REVIEW';

export type OilSeverityClass = 'MINOR' | 'MODERATE' | 'MAJOR' | 'SEVERE' | 'UNKNOWN';

export interface OilGeoJSONGeometry {
  type: 'Point' | 'Polygon' | 'MultiPolygon' | 'LineString';
  coordinates: any[];
}

export interface LookalikeVerification {
  verification_id?: string;
  candidate_id?: string;
  sar_granule_id?: string;
  predicted_class: LookalikeClass;
  pipeline_decision: PipelineDecision;
  class_probabilities: Record<string, number>;
  model_confidence: {
    max_class_probability?: number;
    entropy: number;
    margin: number;
  };
}

export interface SpillSeverityBasis {
  mean_backscatter_db: number;
  backscatter_suppression_db: number;
  estimated_area_km2: number;
  texture_features_used: boolean;
}

export interface SpillSeverity {
  severity_class: OilSeverityClass;
  severity_basis: SpillSeverityBasis;
  explicit_non_claims: string[];
}

export interface DataQuality {
  data_quality_index: number;
  quality_flags: string[];
}

export interface SpillDetectionResponse {
  incident_id: string;
  tile_id: string;
  sar_granule_id: string;
  status: SpillDetectionStatus;
  is_abstained: boolean;
  abstention_details: string | null;
  spill_mask: any | null;
  spill_geometry: OilGeoJSONGeometry | null;
  lookalike_verification: LookalikeVerification;
  severity: SpillSeverity;
  data_quality: DataQuality;
  metrics_metadata_ref: string;
  provenance: {
    sar_scene: any;
    preprocessing: any;
    model: any;
    training_dataset: any;
  };
}

export interface SpillDetectionRequest {
  incident_id: string;
  sar_granule_id: string;
  tile_id?: string;
}
