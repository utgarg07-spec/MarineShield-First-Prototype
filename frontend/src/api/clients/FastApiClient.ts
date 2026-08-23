import type { ApiClient, PaginatedResponse, DetailResponse } from './ApiClient';
import type { Incident, IncidentSummary } from '../types/incident';
import type { Forecast } from '../types/forecast';
import type { ThreatAssessment } from '../types/threat';
import type { SARVesselDetection, AISObservation, VesselMatch, UnmatchedVessel, AnomalyEvent } from '../types/vessel';
import type { SARSceneMetadata, SARTile } from '../types/sar';
import type { SpillDetectionResponse, SpillDetectionRequest } from '../types/oil_intelligence';
import type { InvestigationResult, InvestigationRequest, CounterfactualResult, CounterfactualRequest } from '../types/investigation';

export class FastApiClient implements ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  private async fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const res = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      ...options,
    });

    if (!res.ok) {
      let errorMsg = `HTTP Error ${res.status}: ${res.statusText}`;
      try {
        const body = await res.json();
        if (body.detail) {
          errorMsg = typeof body.detail === 'string' ? body.detail : JSON.stringify(body.detail);
        } else if (body.error?.message) {
          errorMsg = body.error.message;
        }
      } catch {
        // Ignore json parse failure on error response
      }
      throw new Error(errorMsg);
    }

    return res.json();
  }

  async getSystemStatus(): Promise<{ status: string }> {
    return this.fetchJson('/health');
  }

  // Contract: GET /api/v1/incidents
  async getIncidents(query?: string): Promise<PaginatedResponse<IncidentSummary>> {
    const queryParam = query ? `?q=${encodeURIComponent(query)}` : '';
    return this.fetchJson(`/api/v1/incidents${queryParam}`);
  }

  // Contract: GET /api/v1/incidents/{incident_id}
  async getIncident(id: string): Promise<DetailResponse<Incident>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(id)}`);
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

  // Contract: GET /api/v1/incidents/{incident_id}/vessels
  async getVessels(incidentId: string): Promise<PaginatedResponse<AISObservation>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/vessels`);
  }

  // Contract: GET /api/v1/incidents/{incident_id}/vessels/matches
  async getVesselMatches(incidentId: string): Promise<PaginatedResponse<VesselMatch>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/vessels/matches`);
  }

  // Contract: GET /api/v1/incidents/{incident_id}/vessels/unmatched
  async getUnmatchedVessels(incidentId: string): Promise<PaginatedResponse<UnmatchedVessel>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/vessels/unmatched`);
  }

  // Contract: GET /api/v1/incidents/{incident_id}/vessels/anomalies
  async getAnomalies(incidentId: string): Promise<PaginatedResponse<AnomalyEvent>> {
    return this.fetchJson(`/api/v1/incidents/${encodeURIComponent(incidentId)}/vessels/anomalies`);
  }

  // Canonical Person 1 Endpoint: POST /api/v1/oil-intelligence/detect
  async detectSpill(payload: SpillDetectionRequest): Promise<DetailResponse<SpillDetectionResponse>> {
    return this.fetchJson('/api/v1/oil-intelligence/detect', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // Canonical Person 1 Endpoint: POST /api/v1/investigation/reconstruct
  async reconstructRelease(payload: InvestigationRequest): Promise<DetailResponse<InvestigationResult>> {
    return this.fetchJson('/api/v1/investigation/reconstruct', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // Canonical Person 1 Endpoint: POST /api/v1/investigation/counterfactual
  async evaluateCounterfactual(payload: CounterfactualRequest): Promise<DetailResponse<CounterfactualResult>> {
    return this.fetchJson('/api/v1/investigation/counterfactual', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
}
