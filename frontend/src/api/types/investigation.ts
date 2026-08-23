// Authoritative Person 1 Investigation Contract Types
// Documented in docs/api/PERSON1_PRESENTATION_DATA_CONTRACT.md

import type { OilGeoJSONGeometry } from './oil_intelligence';

export type InvestigationMode =
  | 'MODE_A_PARTIAL_INTEGRATION_NO_ENVIRONMENT'
  | 'MODE_B_FULL_INTEGRATION_WITH_ENVIRONMENT';

export type AttributionStatus =
  | 'ATTRIBUTED_CANDIDATES_EVALUATED'
  | 'SOURCE_UNKNOWN'
  | 'ABSTAINED';

export type CandidateSourceCategory = 'VESSEL_IDENTIFIED' | 'DARK_TARGET' | 'UNTRACKED';

export interface ComponentScores {
  spatial: number;
  temporal: number;
  trajectory: number;
  drift: number | string;
  vessel: number;
  behavior: number;
}

export interface EvidenceItem {
  evidence_type: string;
  polarity: 'SUPPORTING' | 'CONTRADICTORY';
  summary: string;
}

export interface EvaluatedCandidate {
  candidate_id: string;
  hypothesis_label: string;
  source_category: CandidateSourceCategory;
  candidate_entity: {
    vessel_mmsi?: string;
    vessel_name?: string;
    vessel_type?: string;
  };
  component_scores: ComponentScores;
  supporting_evidence: EvidenceItem[];
  contradictory_evidence: EvidenceItem[];
}

export interface ReleaseReconstruction {
  release_region_status: string;
  release_time_window_status: string;
  reconstruction_polygon_geojson: OilGeoJSONGeometry | null;
}

export interface VesselInputSummary {
  total_ais_candidates_ingested: number;
  accepted_observations_count: number;
  excluded_future_observations_count: number;
  excluded_observation_ids: string[];
  vessel_matches_count: number;
  unmatched_dark_vessels_count: number;
}

export interface InvestigationResult {
  incident_id: string;
  mode: InvestigationMode;
  investigation_timestamp_utc: string;
  attribution_status: AttributionStatus;
  unknown_trigger_reason: string | null;
  release_reconstruction: ReleaseReconstruction;
  vessel_input_summary: VesselInputSummary;
  environmental_evidence_status: {
    status: string;
    reason_code: string;
    provenance_status: string;
  };
  source_ranking_status: string;
  evaluated_candidates: EvaluatedCandidate[];
  non_guilt_clause: string;
  data_provenance: {
    vessel_data_mode: string;
    vessel_provenance_hash: string;
    environmental_data_mode: string;
  };
}

export interface RankChange {
  hypothesis_label: string;
  candidate_id: string;
  original_rank: number;
  original_score: number;
  counterfactual_rank: number;
  counterfactual_score: number;
  rank_change: number;
  score_change: number;
}

export interface CounterfactualResult {
  incident_id: string;
  status: 'SUCCESS' | 'NOT_APPLICABLE' | 'BLOCKED_TIE_POLICY_REQUIRED';
  reason: string;
  replay_timestamp_utc?: string | null;
  original_candidate_count: number;
  counterfactual_candidate_count: number;
  removed_candidate_id: string | null;
  removed_candidate_label: string | null;
  original_top_hypothesis_label?: string;
  original_top_hypothesis_score?: number;
  original_attribution_status?: AttributionStatus;
  counterfactual_attribution_status?: AttributionStatus;
  is_top_hypothesis_dominant: boolean;
  is_result_weak_or_tied: boolean;
  rank_changes: RankChange[];
  non_guilt_clause: string;
  data_mode: string;
}

export interface InvestigationRequest {
  incident_id: string;
  t_observation_utc: string;
  spill_centroid_lon_lat: [number, number];
}

export interface CounterfactualRequest {
  incident_id: string;
  remove_candidate_id: string;
}
