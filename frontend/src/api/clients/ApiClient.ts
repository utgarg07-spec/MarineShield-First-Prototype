import type { Incident, IncidentSummary } from '../types/incident';
import type { Forecast } from '../types/forecast';
import type { ThreatAssessment } from '../types/threat';
import type { SARVesselDetection, AISObservation, VesselMatch, UnmatchedVessel, AnomalyEvent } from '../types/vessel';
import type { SARSceneMetadata, SARTile } from '../types/sar';
import type { SpillDetectionResponse, SpillDetectionRequest } from '../types/oil_intelligence';
import type { InvestigationResult, InvestigationRequest, CounterfactualResult, CounterfactualRequest } from '../types/investigation';

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    limit: number;
    next_cursor: string | null;
    previous_cursor: string | null;
    has_next: boolean;
    has_previous: boolean;
  };
  applied_filters?: any;
  request_id: string;
}

export interface DetailResponse<T> {
  data: T;
  request_id: string;
}

export interface ApiClient {
  getSystemStatus(): Promise<{ status: string }>;
  
  // Incidents
  getIncidents(query?: string): Promise<PaginatedResponse<IncidentSummary>>;
  getIncident(id: string): Promise<DetailResponse<Incident>>;
  
  // Forecasts
  getForecast(incidentId: string, forecastId: string): Promise<DetailResponse<Forecast>>;
  
  // Threats
  getThreatAssessment(incidentId: string, threatId: string): Promise<DetailResponse<ThreatAssessment>>;
  
  // SAR
  getSARScenes(incidentId: string): Promise<PaginatedResponse<SARSceneMetadata>>;
  getSARTiles(incidentId: string): Promise<PaginatedResponse<SARTile>>;
  getSARDetections(incidentId: string): Promise<PaginatedResponse<SARVesselDetection>>;
  
  // Vessels
  getVessels(incidentId: string): Promise<PaginatedResponse<AISObservation>>;
  getVesselMatches(incidentId: string): Promise<PaginatedResponse<VesselMatch>>;
  getUnmatchedVessels(incidentId: string): Promise<PaginatedResponse<UnmatchedVessel>>;
  getAnomalies(incidentId: string): Promise<PaginatedResponse<AnomalyEvent>>;

  // Person 1 Canonical Presentation Contracts
  detectSpill(payload: SpillDetectionRequest): Promise<DetailResponse<SpillDetectionResponse>>;
  reconstructRelease(payload: InvestigationRequest): Promise<DetailResponse<InvestigationResult>>;
  evaluateCounterfactual(payload: CounterfactualRequest): Promise<DetailResponse<CounterfactualResult>>;
}
