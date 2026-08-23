/**
 * Incident mock fixtures — contract-faithful.
 * 
 * Source: Incident API Contract (docs/contracts/MarineShield_Incident_API_Contract.docx)
 * + SAR scene handoff (docs/handoffs/sar_scene_handoff.json) for observation time context.
 * 
 * data_mode: MOCK_HYBRID — this is demonstration data assembled from
 * authoritative source artifacts, not live API data.
 * 
 * All values are either SOURCE_DERIVED or CONTRACT_STRUCTURAL.
 * No fabricated scientific data.
 */
import type { Incident, IncidentSummary } from '../../api/types/incident';

export const mockIncidents: IncidentSummary[] = [
  {
    id: '0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da',
    reference: 'MS-2024-000001',
    title: null, // No title fabricated; contract allows null
    status: 'new',
    status_label: 'New',
    severity: {
      class: 'unknown',
      score: null,
      confidence: null,
      basis: [],
      as_of: null,
    },
    response_priority: {
      class: 'unknown',
      score: null,
      confidence: null,
      reason_codes: [],
      explanation: null,
      requires_human_review: false,
      computed_at: null,
      algorithm_version: null,
    },
    location: {
      geometry: null, // No fabricated coordinates
      crs: 'EPSG:4326',
      accuracy_m: null,
      source: 'sentinel1_detection',
      source_ref: null,
    },
    observation_time_start: '2024-01-20T00:55:28.704Z', // SOURCE_DERIVED from sar_scene_handoff
    observation_time_end: '2024-01-20T00:55:53.702Z',   // SOURCE_DERIVED from sar_scene_handoff
    created_at: '2024-01-20T01:30:00.000Z',   // CONTRACT_STRUCTURAL (plausible ingestion delay)
    updated_at: '2024-01-20T01:30:00.000Z',
    last_activity_at: '2024-01-20T01:30:00.000Z',
    provenance: {
      created_from: 'sentinel1_detection',
      source_records: [],
      source_systems: ['Copernicus Data Space'],
      observation_time_start: '2024-01-20T00:55:28.704Z',
      observation_time_end: '2024-01-20T00:55:53.702Z',
      ingested_at: '2024-01-20T01:30:00.000Z',
      pipeline_version: 'incident-ingestion-1.0.0',
      dataset_versions: {
        sentinel1: 'S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2',
      },
      processing_run_id: null,
      is_complete: false,
      limitations: [
        'Initial incident created from SAR acquisition. Spill detection, vessel intelligence, and forecasting not yet executed.',
      ],
      data_mode: 'MOCK_HYBRID',
    },
    links: {
      self: '/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da',
      detail: '/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da',
    },
  },
];

/**
 * Returns a full Incident detail for a given ID.
 * Extends the summary with detail-only fields.
 */
export const getMockIncidentById = (id: string): Incident | undefined => {
  const summary = mockIncidents.find(inc => inc.id === id);
  if (!summary) return undefined;

  return {
    ...summary,
    description: null,
    status_changed_at: null,
    status_reason: null,
    closed_at: null,
    related: {
      spill: { count: 0, href: `${summary.links.self}/spill-detections` },
      forecast: { count: 0, href: `${summary.links.self}/forecasts` },
      threats: { count: 0, href: `${summary.links.self}/threats` },
      vessels: { count: 0, href: `${summary.links.self}/vessels` },
      evidence: { count: 0, href: `${summary.links.self}/evidence` },
    },
  };
};
