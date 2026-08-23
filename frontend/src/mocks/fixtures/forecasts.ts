import type { Forecast } from '../../api/types/forecast';

export const mockForecastUnavailable: Forecast = {
  forecast_id: "unavailable-forecast",
  incident_id: "0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da",
  status: "failed",
  status_message: "Forecast failed because current-data coverage was unavailable.",
  created_at: "2026-08-21T14:30:00Z",
  started_at: "2026-08-21T14:30:02Z",
  completed_at: "2026-08-21T14:30:02Z",
  forecast_reference_time: "2026-08-21T10:00:00Z",
  requested_horizons_hours: [6, 12, 24, 48],
  available_horizons_hours: [],
  release_initialization: {
    release_geometry: {
      type: "Point",
      coordinates: [4.5123, 51.9234]
    },
    crs: "EPSG:4326",
    release_start: "2026-08-21T10:00:00Z",
    source_type: "validated_release_hypothesis",
    source_ref: "3a8ef3b9-31f9-4e72-a756-df6b2e4d4d71"
  },
  trajectory: null,
  timesteps: [],
  uncertainty: null,
  particle_spread: null,
  threat_assessment: null,
  response_priority: {
    class: "unknown",
    score: null,
    confidence: null,
    reason_codes: ["forecast_unavailable"],
    explanation: "Response priority cannot be computed without a valid forecast.",
    requires_human_review: true,
    computed_at: null,
    algorithm_version: null
  },
  provenance: {
    forecast_engine: "PyGNOME",
    forecast_engine_version: "approved-version",
    service_version: "forecast-service-1.0.0",
    configuration_version: "forecast-config-1.0.0",
    dataset_versions: {},
    provider_sources: {},
    source_records: [],
    processing_run_id: "failed-run-id",
    random_seed: 42,
    created_at: "2026-08-21T14:30:00Z",
    environment_valid_from: "2026-08-21T10:00:00Z",
    environment_valid_to: "2026-08-23T10:00:00Z",
    coordinate_reference_system: "EPSG:4326",
    units: {
      distance: "m",
      area: "m2",
      speed: "m/s",
      time: "UTC"
    },
    limitations: ["No current data covers the requested forecast interval."]
  },
  warnings: [
    {
      code: "ENVIRONMENTAL_DATA_UNAVAILABLE",
      message: "No current data covers the requested forecast interval.",
      severity: "error"
    }
  ],
  limitations: ["Forecast unavailable due to missing environmental data."],
  artifacts: {},
  links: {
    self: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da/forecasts/unavailable-forecast",
    incident: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da"
  }
};

export const mockForecastSucceeded: Forecast = {
  forecast_id: "df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f",
  incident_id: "0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da",
  status: "succeeded",
  status_message: "Forecast completed successfully.",
  created_at: "2026-08-21T14:30:00Z",
  started_at: "2026-08-21T14:30:02Z",
  completed_at: "2026-08-21T14:31:18Z",
  forecast_reference_time: "2026-08-21T10:00:00Z",
  requested_horizons_hours: [6, 12, 24, 48],
  available_horizons_hours: [6, 12, 24, 48],
  release_initialization: {
    release_geometry: {
      type: "Point",
      coordinates: [72.8, 18.9]
    },
    crs: "EPSG:4326",
    release_start: "2026-08-21T10:00:00Z",
    release_end: "2026-08-21T10:15:00Z",
    release_duration_s: 900,
    initial_mass_kg: null,
    initial_mass_uncertainty_kg: null,
    source_type: "validated_release_hypothesis",
    source_ref: "3a8ef3b9-31f9-4e72-a756-df6b2e4d4d71",
    confidence: 0.73
  },
  trajectory: {
    type: "FeatureCollection",
    features: [
      {
        type: "Feature",
        id: "trajectory-6h",
        geometry: {
          type: "LineString",
          coordinates: [
            [72.8000, 18.9000],
            [72.8301, 18.9402],
            [72.8512, 18.9588],
            [72.8777, 18.9811],
            [72.9018, 19.0021],
            [72.9251, 19.0214],
            [72.9512, 19.0431]
          ]
        },
        properties: {
          layer: "forecast_centerline",
          horizon_hours: 6,
          valid_time_start: "2026-08-21T10:00:00Z",
          valid_time_end: "2026-08-21T16:00:00Z",
          coordinate_reference_system: "EPSG:4326",
          line_role: "centerline",
          confidence: 0.90
        }
      },
      {
        type: "Feature",
        id: "trajectory-12h",
        geometry: {
          type: "LineString",
          coordinates: [
            [72.8000, 18.9000],
            [72.8777, 18.9811],
            [72.9512, 19.0431],
            [73.0355, 19.1092],
            [73.1221, 19.1755]
          ]
        },
        properties: {
          layer: "forecast_centerline",
          horizon_hours: 12,
          valid_time_start: "2026-08-21T10:00:00Z",
          valid_time_end: "2026-08-21T22:00:00Z",
          coordinate_reference_system: "EPSG:4326",
          line_role: "centerline",
          confidence: 0.90
        }
      },
      {
        type: "Feature",
        id: "trajectory-24h",
        geometry: {
          type: "LineString",
          coordinates: [
            [72.8000, 18.9000],
            [72.9512, 19.0431],
            [73.1221, 19.1755],
            [73.3012, 19.3421]
          ]
        },
        properties: {
          layer: "forecast_centerline",
          horizon_hours: 24,
          valid_time_start: "2026-08-21T10:00:00Z",
          valid_time_end: "2026-08-22T10:00:00Z",
          coordinate_reference_system: "EPSG:4326",
          line_role: "centerline",
          confidence: 0.90
        }
      },
      {
        type: "Feature",
        id: "trajectory-48h",
        geometry: {
          type: "LineString",
          coordinates: [
            [72.8000, 18.9000],
            [73.1221, 19.1755],
            [73.3012, 19.3421],
            [73.6221, 19.6821]
          ]
        },
        properties: {
          layer: "forecast_centerline",
          horizon_hours: 48,
          valid_time_start: "2026-08-21T10:00:00Z",
          valid_time_end: "2026-08-23T10:00:00Z",
          coordinate_reference_system: "EPSG:4326",
          line_role: "centerline",
          confidence: 0.90
        }
      }
    ]
  },
  timesteps: [
    {
      horizon_hours: 6,
      valid_time: "2026-08-21T16:00:00Z",
      position: {
        type: "Point",
        coordinates: [72.9512, 19.0431]
      },
      centerline: null,
      uncertainty_geometry: {
        type: "Feature",
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
          horizon_hours: 6,
          confidence_level: 0.90,
          geometry_role: "uncertainty_region"
        }
      },
      particle_spread: {
        particle_count: 1000,
        valid_particle_count: 998,
        invalid_particle_count: 2,
        centroid: { type: "Point", coordinates: [72.9512, 19.0431] },
        bbox: [72.9100, 19.0100, 73.0000, 19.0800],
        area_m2: 38200000,
        distance_from_release_m: { mean: 14800, median: 14600, p50: 14600, p90: 21800, p95: 24300, maximum: 30100 },
        radial_spread_m: { p50: 6200, p90: 11800, p95: 13200 },
        longitude_stats: { min: 72.9100, max: 73.0000, mean: 72.9512, median: 72.9500 },
        latitude_stats: { min: 19.0100, max: 19.0800, mean: 19.0431, median: 19.0420 }
      },
      environment: {
        wind_source: "approved-wind-provider",
        current_source: "approved-current-provider",
        wind_speed_mps: 5.2,
        wind_direction_deg: 238.0,
        current_speed_mps: 0.41,
        current_direction_deg: 112.0,
        coverage_status: "complete"
      },
      threat_summary: {
        threatened_asset_count: 1,
        highest_threat_level: "moderate",
        earliest_asset_eta: "2026-08-21T17:30:00Z"
      }
    },
    {
      horizon_hours: 12,
      valid_time: "2026-08-21T22:00:00Z",
      position: {
        type: "Point",
        coordinates: [73.1221, 19.1755]
      },
      centerline: null,
      uncertainty_geometry: null,
      particle_spread: {},
      environment: {},
      threat_summary: {}
    },
    {
      horizon_hours: 24,
      valid_time: "2026-08-22T10:00:00Z",
      position: {
        type: "Point",
        coordinates: [73.3012, 19.3421]
      },
      centerline: null,
      uncertainty_geometry: null,
      particle_spread: {},
      environment: {},
      threat_summary: {}
    },
    {
      horizon_hours: 48,
      valid_time: "2026-08-23T10:00:00Z",
      position: {
        type: "Point",
        coordinates: [73.6221, 19.6821]
      },
      centerline: null,
      uncertainty_geometry: null,
      particle_spread: {},
      environment: {},
      threat_summary: {}
    }
  ],
  uncertainty: {
    method: "particle_quantiles",
    confidence_level: 0.9,
    geometry_role: "region_containing_configured_particle_fraction",
    geometry_type: "per_timestep",
    regions: [
      {
        horizon_hours: 6,
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
        particle_fraction: 0.90,
        area_m2: 38200000,
        valid: true
      }
    ],
    overall_geometry: null,
    limitations: []
  },
  particle_spread: {
    particle_count: 1000,
    valid_particle_count_by_horizon: {
      "6": 998,
      "12": 998,
      "24": 995,
      "48": 990
    },
    particle_tracks_in_response: false
  },
  threat_assessment: {
    status: "complete",
    evaluated_asset_count: 42,
    threatened_asset_count: 3,
    assets: [],
    limitations: []
  },
  response_priority: {
    class: "P1",
    score: 0.91,
    confidence: 0.71,
    reason_codes: [
      "protected_area_threat",
      "arrival_within_24h",
      "high_spill_severity"
    ],
    explanation: "The forecast intersects a protected area within 24 hours. Priority remains subject to human review.",
    requires_human_review: true,
    computed_at: "2026-08-21T14:31:18Z",
    algorithm_version: "priority-rules-1.0.0"
  },
  provenance: {
    forecast_engine: "PyGNOME",
    forecast_engine_version: "approved-version",
    service_version: "forecast-service-1.0.0",
    configuration_version: "forecast-config-1.0.0",
    dataset_versions: {},
    provider_sources: {},
    source_records: [],
    processing_run_id: "f4a09541-f3e4-4c8a-98e9-df66a4db4a11",
    random_seed: 42,
    created_at: "2026-08-21T14:30:00Z",
    environment_valid_from: "2026-08-21T10:00:00Z",
    environment_valid_to: "2026-08-23T10:00:00Z",
    coordinate_reference_system: "EPSG:4326",
    units: {
      distance: "m",
      area: "m2",
      speed: "m/s",
      time: "UTC"
    },
    limitations: []
  },
  warnings: [],
  limitations: [],
  artifacts: {
    particle_tracks: {
      available: true,
      media_type: "application/geo+json",
      href: "/api/v1/forecasts/df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f/artifacts/particle-tracks",
      size_bytes: 24800000,
      expires_at: null
    }
  },
  links: {
    self: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da/forecasts/df22d41b-2323-4ee4-9b0b-6e2e1d2c5d8f",
    incident: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da",
    forecasts: "/api/v1/incidents/0b7f8af4-5e4f-4b57-86c1-a07f6e6fc8da/forecasts"
  }
};

