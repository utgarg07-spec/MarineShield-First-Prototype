import type { ApiClient, PaginatedResponse, DetailResponse } from './ApiClient';
import type { Incident, IncidentSummary } from '../types/incident';
import type { Forecast } from '../types/forecast';
import type { ThreatAssessment } from '../types/threat';
import { mockIncidents, getMockIncidentById } from '../../mocks/fixtures/incidents';
import { mockAISObservations, mockSARDetections, mockMatches, mockUnmatchedDetections, mockAnomalies } from '../../mocks/fixtures/vessels';
import { mockForecastUnavailable, mockForecastSucceeded } from '../../mocks/fixtures/forecasts';
import { mockThreatUnavailable, mockThreatSucceeded } from '../../mocks/fixtures/threats';
import type { SARVesselDetection, AISObservation, VesselMatch, UnmatchedVessel, AnomalyEvent } from '../types/vessel';
import { mockSARScenes, mockSARTiles } from '../../mocks/fixtures/sar';
import type { SARSceneMetadata, SARTile } from '../types/sar';
import type { SpillDetectionResponse, SpillDetectionRequest } from '../types/oil_intelligence';
import type { InvestigationResult, InvestigationRequest, CounterfactualResult, CounterfactualRequest } from '../types/investigation';

export const mockSpillDetection: SpillDetectionResponse = {
  incident_id: "MS-PHASE6-DEV-001",
  tile_id: "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train",
  sar_granule_id: "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
  status: "OIL_DETECTED",
  is_abstained: false,
  abstention_details: null,
  spill_mask: null,
  spill_geometry: {
    type: "Polygon",
    coordinates: [
      [
        [73.18, 18.48],
        [73.22, 18.48],
        [73.22, 18.52],
        [73.18, 18.52],
        [73.18, 18.48]
      ]
    ]
  },
  lookalike_verification: {
    predicted_class: "PETROLEUM_OIL",
    pipeline_decision: "CONFIRM_AS_OIL",
    class_probabilities: {
      "PETROLEUM_OIL": 0.88,
      "BIOGENIC_SLICK": 0.05,
      "LOW_WIND_AREA": 0.03,
      "SHIP_WAKE": 0.02,
      "NATURAL_FILM": 0.01,
      "UNCERTAIN": 0.01
    },
    model_confidence: {
      max_class_probability: 0.88,
      entropy: 0.35,
      margin: 0.83
    }
  },
  severity: {
    severity_class: "MODERATE",
    severity_basis: {
      mean_backscatter_db: -14.2,
      backscatter_suppression_db: 4.8,
      estimated_area_km2: 12.4,
      texture_features_used: true
    },
    explicit_non_claims: [
      "This classification does not represent estimated oil volume in tonnes or litres.",
      "This classification does not constitute ecological damage assessment.",
      "This classification does not imply legal severity of a MARPOL violation."
    ]
  },
  data_quality: {
    data_quality_index: 0.95,
    quality_flags: []
  },
  metrics_metadata_ref: "METRICS-SAR-SAM-ADAPT-v1.0",
  provenance: {
    sar_scene: {
      granule_id: "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
      polarization: "VV_VH",
      source_api: "Copernicus Sentinel-1 SAR"
    },
    preprocessing: {
      pipeline_version: "sar-preprocess-v1.0.0",
      processing_steps_applied: [
        "RADIOMETRIC_CALIBRATION_SIGMA0",
        "DB_CONVERSION",
        "SPECKLE_FILTERING_REFINED_LEE",
        "DETERMINISTIC_TILING_AND_NORMALIZATION"
      ]
    },
    model: {
      model_version_id: "sam-vit-b-sar-adapter-v1.0.0",
      module: "OIL_INTELLIGENCE_DUAL_STAGE",
      inference_device: "cuda (PyTorch)"
    },
    training_dataset: {
      dataset_version_id: "DARTIS-2019-v1.0",
      dataset_name: "DARTIS-2019"
    }
  }
};

export const mockInvestigationResult: InvestigationResult = {
  incident_id: "MS-PHASE6-DEV-001",
  mode: "MODE_A_PARTIAL_INTEGRATION_NO_ENVIRONMENT",
  investigation_timestamp_utc: "2024-01-20T00:55:41Z",
  attribution_status: "SOURCE_UNKNOWN",
  unknown_trigger_reason: "PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED",
  release_reconstruction: {
    release_region_status: "UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY",
    release_time_window_status: "UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY",
    reconstruction_polygon_geojson: {
      type: "Polygon",
      coordinates: [
        [
          [73.15, 18.45],
          [73.25, 18.45],
          [73.25, 18.55],
          [73.15, 18.55],
          [73.15, 18.45]
        ]
      ]
    }
  },
  vessel_input_summary: {
    total_ais_candidates_ingested: 5,
    accepted_observations_count: 3,
    excluded_future_observations_count: 2,
    excluded_observation_ids: [
      "240cdb8f-9884-4852-9d71-4ee53d5efe63",
      "f5e5f969-7bd8-476d-b820-14ec20b4736b"
    ],
    vessel_matches_count: 1,
    unmatched_dark_vessels_count: 1
  },
  environmental_evidence_status: {
    status: "BLOCKED",
    reason_code: "PERSON3_ENVIRONMENTAL_HANDOFF_NOT_PROVIDED",
    provenance_status: "NOT_AVAILABLE"
  },
  source_ranking_status: "NOT_COMPUTED",
  evaluated_candidates: [
    {
      candidate_id: "cand-vsl-mmsi-413123456",
      hypothesis_label: "H_1",
      source_category: "VESSEL_IDENTIFIED",
      candidate_entity: {
        vessel_mmsi: "413123456",
        vessel_name: "Cooperative Vessel MMSI-413123456",
        vessel_type: "CARGO"
      },
      component_scores: {
        spatial: 90.0,
        temporal: 85.0,
        trajectory: 80.0,
        drift: "UNAVAILABLE_PENDING_ENVIRONMENTAL_HISTORY",
        vessel: 75.0,
        behavior: 45.0
      },
      supporting_evidence: [
        {
          evidence_type: "SPATIAL_PROXIMITY",
          polarity: "SUPPORTING",
          summary: "Vessel transit points recorded near target region"
        }
      ],
      contradictory_evidence: []
    }
  ],
  non_guilt_clause: "This partial evaluation reflects maritime observations only. Absence of environmental drift history suppresses definitive source ranking. Unmatched dark targets carry analytical investigation flags only and do not constitute proof of responsibility.",
  data_provenance: {
    vessel_data_mode: "SYNTHETIC_DEVELOPMENT_FIXTURE",
    vessel_provenance_hash: "demo_run_dff3e36e4f111353",
    environmental_data_mode: "NOT_AVAILABLE"
  }
};

export const mockCounterfactualResult: CounterfactualResult = {
  incident_id: "MS-PHASE6-DEV-001",
  status: "SUCCESS",
  reason: "COUNTERFACTUAL_EVALUATION_COMPLETED",
  replay_timestamp_utc: "2024-01-20T00:55:41Z",
  original_candidate_count: 2,
  counterfactual_candidate_count: 1,
  removed_candidate_id: "cand-vsl-mmsi-413123456",
  removed_candidate_label: "H_1",
  original_top_hypothesis_label: "H_1",
  original_top_hypothesis_score: 74.69,
  original_attribution_status: "ATTRIBUTED_CANDIDATES_EVALUATED",
  counterfactual_attribution_status: "SOURCE_UNKNOWN",
  is_top_hypothesis_dominant: true,
  is_result_weak_or_tied: false,
  rank_changes: [
    {
      hypothesis_label: "H_1",
      candidate_id: "cand-vsl-mmsi-413999999",
      original_rank: 1,
      original_score: 74.69,
      counterfactual_rank: 1,
      counterfactual_score: 25.80,
      rank_change: 0,
      score_change: -48.89
    }
  ],
  non_guilt_clause: "Counterfactual attribution is a deterministic sensitivity analysis of the source-ranking engine. It does not establish legal causality, responsibility, or illegal behavior.",
  data_mode: "SYNTHETIC_DEVELOPMENT_FIXTURE"
};

export class MockApiClient implements ApiClient {
  async getSystemStatus(): Promise<{ status: string }> {
    return { status: 'mock-ok' };
  }

  async getIncidents(query?: string): Promise<PaginatedResponse<IncidentSummary>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    let items = mockIncidents as IncidentSummary[];
    if (query) {
      const lowerQuery = query.toLowerCase();
      items = items.filter(inc => 
        (inc.title || '').toLowerCase().includes(lowerQuery) || 
        inc.reference.toLowerCase().includes(lowerQuery) ||
        inc.id.toLowerCase().includes(lowerQuery)
      );
    }
    return {
      data: items,
      pagination: {
        limit: 25,
        next_cursor: null,
        previous_cursor: null,
        has_next: false,
        has_previous: false
      },
      request_id: 'mock-request-id'
    };
  }

  async getIncident(id: string): Promise<DetailResponse<Incident>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    const incident = getMockIncidentById(id);
    if (!incident) throw new Error('Incident not found');
    return {
      data: incident,
      request_id: 'mock-request-id'
    };
  }

  async getForecast(_incidentId: string, forecastId: string): Promise<DetailResponse<Forecast>> {
    await new Promise(resolve => setTimeout(resolve, 400));
    const forecast = forecastId === 'unavailable-forecast' ? mockForecastUnavailable : mockForecastSucceeded;
    return {
      data: forecast,
      request_id: 'mock-request-id'
    };
  }

  async getThreatAssessment(_incidentId: string, forecastId: string): Promise<DetailResponse<ThreatAssessment>> {
    await new Promise(resolve => setTimeout(resolve, 400));
    const threat = forecastId === 'unavailable-forecast' ? mockThreatUnavailable : mockThreatSucceeded;
    return {
      data: threat,
      request_id: 'mock-request-id'
    };
  }

  async getSARScenes(_incidentId: string): Promise<PaginatedResponse<SARSceneMetadata>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockSARScenes,
      pagination: { limit: 25, next_cursor: null, previous_cursor: null, has_next: false, has_previous: false },
      request_id: 'mock-request-id'
    };
  }

  async getSARTiles(_incidentId: string): Promise<PaginatedResponse<SARTile>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockSARTiles,
      pagination: { limit: 25, next_cursor: null, previous_cursor: null, has_next: false, has_previous: false },
      request_id: 'mock-request-id'
    };
  }

  async getSARDetections(_incidentId: string): Promise<PaginatedResponse<SARVesselDetection>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockSARDetections,
      pagination: { limit: 25, next_cursor: null, previous_cursor: null, has_next: false, has_previous: false },
      request_id: 'mock-request-id'
    };
  }

  async getVessels(_incidentId: string): Promise<PaginatedResponse<AISObservation>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockAISObservations,
      pagination: { limit: 25, next_cursor: null, previous_cursor: null, has_next: false, has_previous: false },
      request_id: 'mock-request-id'
    };
  }

  async getVesselMatches(_incidentId: string): Promise<PaginatedResponse<VesselMatch>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockMatches,
      pagination: { limit: 25, next_cursor: null, previous_cursor: null, has_next: false, has_previous: false },
      request_id: 'mock-request-id'
    };
  }

  async getUnmatchedVessels(_incidentId: string): Promise<PaginatedResponse<UnmatchedVessel>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockUnmatchedDetections,
      pagination: { limit: 25, next_cursor: null, previous_cursor: null, has_next: false, has_previous: false },
      request_id: 'mock-request-id'
    };
  }

  async getAnomalies(_incidentId: string): Promise<PaginatedResponse<AnomalyEvent>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockAnomalies,
      pagination: { limit: 25, next_cursor: null, previous_cursor: null, has_next: false, has_previous: false },
      request_id: 'mock-request-id'
    };
  }

  async detectSpill(_payload: SpillDetectionRequest): Promise<DetailResponse<SpillDetectionResponse>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockSpillDetection,
      request_id: 'mock-request-id'
    };
  }

  async reconstructRelease(_payload: InvestigationRequest): Promise<DetailResponse<InvestigationResult>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockInvestigationResult,
      request_id: 'mock-request-id'
    };
  }

  async evaluateCounterfactual(_payload: CounterfactualRequest): Promise<DetailResponse<CounterfactualResult>> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return {
      data: mockCounterfactualResult,
      request_id: 'mock-request-id'
    };
  }
}
