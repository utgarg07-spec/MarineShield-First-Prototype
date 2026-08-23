import type { ThreatAssessment } from '../../api/types/threat';

export const mockThreatUnavailable: ThreatAssessment = {
  threat_assessment_id: "unavailable-threat",
  incident_id: "0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da",
  forecast_id: "unavailable-forecast",
  status: "failed",
  status_message: "Threat assessment failed because forecast was unavailable.",
  created_at: "2026-08-21T14:40:00Z",
  started_at: "2026-08-21T14:40:02Z",
  completed_at: "2026-08-21T14:40:02Z",
  evaluated_horizons_hours: [],
  evaluated_asset_types: [
    "mangrove",
    "protected_area",
    "fishery",
    "coastline",
    "port"
  ],
  summary: {
    overall_threat_level: "unknown",
    overall_alert_level: "none",
    response_priority_score: null,
    response_priority_band: "unknown",
    response_priority_confidence: null,
    requires_human_review: true,
    threatened_asset_count: 0,
    evaluated_asset_count: 0,
    asset_type_counts: {
      "mangrove": 0,
      "protected_area": 0,
      "fishery": 0,
      "coastline": 0,
      "port": 0
    },
    earliest_eta: null,
    earliest_eta_horizon_hours: null,
    nearest_asset_distance_m: null,
    highest_threat_asset_id: null,
    reason_codes: ["forecast_unavailable"],
    explanation: "Cannot compute threats without a valid forecast."
  },
  assets: [],
  threat_geometries: null,
  response_priority: {
    score: null,
    band: "unknown",
    confidence: null,
    reason_codes: ["forecast_unavailable"],
    factor_contributions: [],
    explanation: "Priority cannot be computed without a valid forecast.",
    requires_human_review: true,
    computed_at: null,
    policy_version: null
  },
  provenance: {
    forecast_id: "unavailable-forecast",
    forecast_engine: "unknown",
    forecast_engine_version: "unknown",
    asset_dataset: "approved-asset-dataset",
    asset_dataset_version: "asset-dataset-version",
    wind_dataset_version: "unknown",
    current_dataset_version: "unknown",
    assessment_service_version: "threat-service-1.0.0",
    policy_version: "threat-priority-policy-1.0.0",
    processing_run_id: "failed-run-id",
    computed_at: "2026-08-21T14:40:02Z",
    limitations: ["Forecast unavailable."]
  },
  warnings: [],
  limitations: ["Threat assessment is unavailable due to missing forecast."],
  links: {
    self: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da/forecasts/unavailable-forecast/threat-assessment",
    incident: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da",
    forecast: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da/forecasts/unavailable-forecast"
  }
};

export const mockThreatSucceeded: ThreatAssessment = {
  threat_assessment_id: "8e7d61c7-63c6-4e14-8ab6-e3cc1ad0bf3e",
  incident_id: "0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da",
  forecast_id: "df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f",
  status: "succeeded",
  status_message: "Threat assessment completed successfully.",
  created_at: "2026-08-21T14:40:00Z",
  started_at: "2026-08-21T14:40:02Z",
  completed_at: "2026-08-21T14:40:19Z",
  evaluated_horizons_hours: [6, 12, 24, 48],
  evaluated_asset_types: [
    "mangrove",
    "protected_area",
    "fishery",
    "coastline",
    "port"
  ],
  summary: {
    overall_threat_level: "high",
    overall_alert_level: "warning",
    response_priority_score: 86,
    response_priority_band: "critical",
    response_priority_confidence: 0.78,
    requires_human_review: true,
    threatened_asset_count: 2,
    evaluated_asset_count: 42,
    asset_type_counts: {
      "mangrove": 0,
      "protected_area": 1,
      "fishery": 1,
      "coastline": 0,
      "port": 0
    },
    earliest_eta: "2026-08-22T08:30:00Z",
    earliest_eta_horizon_hours: 24,
    nearest_asset_distance_m: 0,
    highest_threat_asset_id: "asset-uuid-protected-area",
    reason_codes: [
      "protected_area_intersection",
      "arrival_within_24h",
      "uncertainty_region_intersection"
    ],
    explanation: "The forecast uncertainty region intersects a protected area within 24 hours. The result requires analyst review because the uncertainty region is material."
  },
  assets: [
    {
      asset_id: "asset-uuid-protected-area",
      asset_type: "protected_area",
      asset_subtype: "marine_nature_reserve",
      name: "Example Protected Marine Reserve",
      official_identifier: "PA-IND-2026-01",
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [72.9000, 19.0000],
            [73.0500, 19.0000],
            [73.0500, 19.1000],
            [72.9000, 19.1000],
            [72.9000, 19.0000]
          ]
        ]
      },
      geometry_role: "asset_boundary",
      crs: "EPSG:4326",
      area_m2: 48000000,
      sensitivity: {
        class: "very_high",
        score: 0.95,
        basis: [
          "legal_protection",
          "biodiversity_value"
        ],
        source: "approved-asset-dataset",
        confidence: 0.91
      },
      threat: {
        status: "threatened",
        threat_level: "high",
        alert_level: "warning",
        response_priority_score: 86,
        response_priority_band: "critical",
        response_priority_contribution: 72,
        intersects_centerline: true,
        intersects_uncertainty_region: true,
        first_intersection_horizon_hours: 24,
        first_intersection_time: "2026-08-22T10:00:00Z",
        minimum_distance_m: 0,
        centerline_overlap_length_m: 3400,
        uncertainty_overlap_area_m2: 125000,
        uncertainty_overlap_fraction: 0.18,
        evaluated_horizons_hours: [6, 12, 24, 48],
        threat_factors: [
          {
            code: "protected_area_intersection",
            label: "Protected-area intersection",
            value: true,
            contribution: 30,
            explanation: "The forecast uncertainty region intersects the protected-area boundary."
          },
          {
            code: "arrival_within_24h",
            label: "Arrival within 24 hours",
            value: true,
            contribution: 25,
            explanation: "The earliest estimated arrival is within the 24-hour operational window."
          }
        ],
        requires_human_review: true,
        explanation: "High threat because the forecast uncertainty region intersects a very-high-sensitivity protected area and estimated arrival occurs within 24 hours."
      },
      eta: {
        status: "estimated",
        time: "2026-08-22T08:30:00Z",
        earliest_time: "2026-08-22T07:30:00Z",
        latest_time: "2026-08-22T10:00:00Z",
        uncertainty_hours: 1.25,
        first_intersection_horizon_hours: 24,
        method: "first_particle_intersection",
        particle_fraction_reaching_asset: 0.37,
        confidence: 0.82,
        reason: null
      },
      provenance: {
        forecast_id: "df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f",
        forecast_engine: "PyGNOME",
        forecast_engine_version: "approved-version",
        asset_dataset: "approved-asset-dataset",
        asset_dataset_version: "asset-dataset-version",
        wind_dataset_version: "wind-version",
        current_dataset_version: "current-version",
        assessment_service_version: "threat-service-1.0.0",
        policy_version: "threat-priority-policy-1.0.0",
        processing_run_id: "f4a09541-f3e4-4c8a-98e9-df66a4db4a11",
        computed_at: "2026-08-21T14:40:19Z",
        limitations: []
      }
    },
    {
      asset_id: "asset-uuid-fishery",
      asset_type: "fishery",
      asset_subtype: "commercial_fishing_ground",
      name: "Coastal Fishery Zone B",
      official_identifier: "FZ-IND-2026-02",
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [73.0500, 19.0500],
            [73.2000, 19.0500],
            [73.2000, 19.1800],
            [73.0500, 19.1800],
            [73.0500, 19.0500]
          ]
        ]
      },
      geometry_role: "asset_boundary",
      crs: "EPSG:4326",
      area_m2: 32000000,
      sensitivity: {
        class: "high",
        score: 0.80,
        basis: ["economic_importance", "fish_spawning_ground"],
        source: "approved-asset-dataset",
        confidence: 0.88
      },
      threat: {
        status: "threatened",
        threat_level: "moderate",
        alert_level: "advisory",
        response_priority_score: 65,
        response_priority_band: "high",
        response_priority_contribution: 55,
        intersects_centerline: true,
        intersects_uncertainty_region: true,
        first_intersection_horizon_hours: 12,
        first_intersection_time: "2026-08-21T22:00:00Z",
        minimum_distance_m: 0,
        centerline_overlap_length_m: 2100,
        uncertainty_overlap_area_m2: 85000,
        uncertainty_overlap_fraction: 0.12,
        evaluated_horizons_hours: [6, 12, 24, 48],
        threat_factors: [
          {
            code: "fishery_intersection",
            label: "Fishery intersection",
            value: true,
            contribution: 20,
            explanation: "Spill trajectory passes through active commercial fishing grounds."
          }
        ],
        requires_human_review: false,
        explanation: "Moderate threat due to direct trajectory intersection with high-sensitivity commercial fishing area."
      },
      eta: {
        status: "estimated",
        time: "2026-08-21T22:00:00Z",
        earliest_time: "2026-08-21T21:00:00Z",
        latest_time: "2026-08-21T23:00:00Z",
        uncertainty_hours: 1.0,
        first_intersection_horizon_hours: 12,
        method: "first_particle_intersection",
        particle_fraction_reaching_asset: 0.42,
        confidence: 0.85,
        reason: null
      },
      provenance: {
        forecast_id: "df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f",
        forecast_engine: "PyGNOME",
        forecast_engine_version: "approved-version",
        asset_dataset: "approved-asset-dataset",
        asset_dataset_version: "asset-dataset-version",
        wind_dataset_version: "wind-version",
        current_dataset_version: "current-version",
        assessment_service_version: "threat-service-1.0.0",
        policy_version: "threat-priority-policy-1.0.0",
        processing_run_id: "f4a09541-f3e4-4c8a-98e9-df66a4db4a11",
        computed_at: "2026-08-21T14:40:19Z",
        limitations: []
      }
    }
  ],
  threat_geometries: {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        id: "threat-asset-uuid-24h",
        geometry: {
          type: "Polygon",
          coordinates: [
            [
              [72.9200, 19.0200],
              [72.9830, 19.0180],
              [73.0000, 19.0650],
              [72.9500, 19.0780],
              [72.9200, 19.0200]
            ]
          ]
        },
        properties: {
          layer: "threat_intersection",
          asset_id: "asset-uuid-protected-area",
          asset_type: "protected_area",
          horizon_hours: 24,
          threat_level: "high",
          alert_level: "warning",
          response_priority_score: 86,
          eta: "2026-08-22T08:30:00Z",
          geometry_role: "forecast_uncertainty_intersection"
        }
      }
    ]
  },
  response_priority: {
    score: 86,
    band: "critical",
    confidence: 0.78,
    reason_codes: [
      "protected_area_intersection",
      "arrival_within_24h",
      "high_asset_sensitivity"
    ],
    factor_contributions: [
      {
        code: "protected_area_intersection",
        contribution: 30
      },
      {
        code: "arrival_within_24h",
        contribution: 25
      },
      {
        code: "high_asset_sensitivity",
        contribution: 22
      },
      {
        code: "uncertainty_intersection",
        contribution: 9
      }
    ],
    explanation: "Priority 86/100 is driven by a protected-area intersection, very-high asset sensitivity, and arrival within 24 hours.",
    requires_human_review: true,
    computed_at: "2026-08-21T14:40:19Z",
    policy_version: "threat-priority-policy-1.0.0"
  },
  provenance: {
    forecast_id: "df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f",
    forecast_engine: "PyGNOME",
    forecast_engine_version: "approved-version",
    asset_dataset: "approved-asset-dataset",
    asset_dataset_version: "asset-dataset-version",
    wind_dataset_version: "wind-version",
    current_dataset_version: "current-version",
    assessment_service_version: "threat-service-1.0.0",
    policy_version: "threat-priority-policy-1.0.0",
    processing_run_id: "f4a09541-f3e4-4c8a-98e9-df66a4db4a11",
    computed_at: "2026-08-21T14:40:19Z",
    limitations: []
  },
  warnings: [],
  limitations: [],
  links: {
    self: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da/forecasts/df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f/threat-assessment",
    incident: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da",
    forecast: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da/forecasts/df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f"
  }
};

