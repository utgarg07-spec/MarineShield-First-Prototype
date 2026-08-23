import type {
  AISObservation,
  SARVesselDetection,
  VesselMatch,
  UnmatchedVessel,
  AnomalyEvent
} from '../../api/types/vessel';

export const mockAISObservations: AISObservation[] = [
  {
    observation_id: "36959fc2-fc30-404e-a4c5-57325d78a378",
    mmsi: "413123456",
    timestamp: "2024-01-20T00:55:12.000Z",
    latitude: 18.5012,
    longitude: 73.2015,
    speed_over_ground_knots: 12.4,
    course_over_ground_deg: 240.0,
    heading_deg: 242.0,
    navigational_status: "UNDER_WAY_USING_ENGINE",
    rate_of_turn_deg_per_min: null,
    source_provider: "GLOBAL_FISHING_WATCH"
  },
  {
    observation_id: "be449c93-cfe2-4a1c-a0af-889a34a8ec18",
    mmsi: "413123456",
    timestamp: "2024-01-19T22:55:00.000Z",
    latitude: 18.62,
    longitude: 73.35,
    speed_over_ground_knots: 13.0,
    course_over_ground_deg: 235.0,
    heading_deg: 236.0,
    navigational_status: "UNDER_WAY_USING_ENGINE",
    rate_of_turn_deg_per_min: null,
    source_provider: "GLOBAL_FISHING_WATCH"
  },
  {
    observation_id: "af3fff3b-a066-440c-a586-6b0241ab484a",
    mmsi: "413987654",
    timestamp: "2024-01-19T19:55:00.000Z",
    latitude: 19.1,
    longitude: 72.8,
    speed_over_ground_knots: 14.5,
    course_over_ground_deg: 180.0,
    heading_deg: 181.0,
    navigational_status: "UNDER_WAY_USING_ENGINE",
    rate_of_turn_deg_per_min: null,
    source_provider: "GLOBAL_FISHING_WATCH"
  },
  {
    observation_id: "240cdb8f-9884-4852-9d71-4ee53d5efe63",
    mmsi: "413987654",
    timestamp: "2024-01-20T01:55:00.000Z",
    latitude: 18.2,
    longitude: 72.8,
    speed_over_ground_knots: 0.8,
    course_over_ground_deg: 180.0,
    heading_deg: 180.0,
    navigational_status: "ENGAGED_IN_FISHING",
    rate_of_turn_deg_per_min: null,
    source_provider: "GLOBAL_FISHING_WATCH"
  },
  {
    observation_id: "f5e5f969-7bd8-476d-b820-14ec20b4736b",
    mmsi: "413555888",
    timestamp: "2024-01-20T01:00:00.000Z",
    latitude: 19.8,
    longitude: 73.9,
    speed_over_ground_knots: 10.1,
    course_over_ground_deg: 90.0,
    heading_deg: 92.0,
    navigational_status: "UNDER_WAY_USING_ENGINE",
    rate_of_turn_deg_per_min: null,
    source_provider: "GLOBAL_FISHING_WATCH"
  }
];

export const mockSARDetections: SARVesselDetection[] = [
  {
    detection_id: "SAR_DET_20240120_001",
    source_granule_id: "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
    detection_timestamp: "2024-01-20T00:55:41.203Z",
    centroid_lat: 18.5,
    centroid_lon: 73.2,
    estimated_length_meters: 180.0,
    estimated_width_meters: 28.0,
    estimated_heading_deg: 240.0,
    radar_cross_section_db: 45.2,
    signal_to_clutter_ratio_db: 18.5,
    detection_confidence: 0.96,
    polarization_used: "VH",
    bounding_box_geojson: {
      type: "Polygon",
      coordinates: [[[73.19, 18.49], [73.21, 18.49], [73.21, 18.51], [73.19, 18.51], [73.19, 18.49]]]
    }
  },
  {
    detection_id: "SAR_DET_20240120_002",
    source_granule_id: "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
    detection_timestamp: "2024-01-20T00:55:41.203Z",
    centroid_lat: 18.85,
    centroid_lon: 73.55,
    estimated_length_meters: 95.0,
    estimated_width_meters: 16.0,
    estimated_heading_deg: 115.0,
    radar_cross_section_db: 38.7,
    signal_to_clutter_ratio_db: 12.1,
    detection_confidence: 0.89,
    polarization_used: "VH",
    bounding_box_geojson: {
      type: "Polygon",
      coordinates: [[[73.54, 18.84], [73.56, 18.84], [73.56, 18.86], [73.54, 18.86], [73.54, 18.84]]]
    }
  }
];

export const mockMatches: VesselMatch[] = [
  {
    match_id: "3974f21f-ec40-43dd-8305-7845427a1907",
    sar_detection_id: "SAR_DET_20240120_001",
    matched_mmsi: "413123456",
    match_status: "MATCHED",
    match_confidence: 0.9743,
    distance_offset_meters: 206.94,
    timestamp_offset_seconds: 29.2,
    heading_delta_deg: 2.0,
    speed_delta_knots: 12.4,
    dimension_match_score: 0.9865,
    reconciliation_algorithm: "DETERMINISTIC_SPATIO_TEMPORAL_HEURISTIC_V1"
  }
];

export const mockUnmatchedDetections: UnmatchedVessel[] = [
  {
    unmatched_id: "f306f292-ebc5-4e50-89f9-fe9aeb767faf",
    sar_detection_id: "SAR_DET_20240120_002",
    source_granule_id: "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
    detection_timestamp: "2024-01-20T00:55:41.203Z",
    centroid_lat: 18.85,
    centroid_lon: 73.55,
    estimated_length_meters: 95.0,
    estimated_width_meters: 16.0,
    detection_confidence: 0.89,
    ais_search_radius_km: 5.0,
    ais_time_window_minutes: 30.0,
    candidate_vessels_searched_count: 5,
    dark_vessel_confidence: 0.8
  }
];

export const mockAnomalies: AnomalyEvent[] = [
  {
    anomaly_id: "ac822f99-a1e2-4a1c-b337-8187dd4c89c5",
    mmsi: "413123456",
    anomaly_type: "AIS_TRANSMISSION_GAP",
    severity_level: "MEDIUM",
    time_start: "2024-01-19T22:55:00.000Z",
    time_end: "2024-01-20T00:55:12.000Z",
    duration_seconds: 7212.0,
    location_start_lat: 18.62,
    location_start_lon: 73.35,
    location_end_lat: 18.5012,
    location_end_lon: 73.2015,
    geometry_geojson: {
      type: "LineString",
      coordinates: [
        [73.35, 18.62],
        [73.2015, 18.5012]
      ]
    },
    anomaly_score: 0.0835,
    context_indicators: {
      gap_duration_hours: 2.0
    },
    description: "Transponder gap of 2.0 hours detected."
  },
  {
    anomaly_id: "495a50c8-4bdd-4711-a800-ab7bcd68c0f5",
    mmsi: "413987654",
    anomaly_type: "AIS_TRANSMISSION_GAP",
    severity_level: "HIGH",
    time_start: "2024-01-19T19:55:00.000Z",
    time_end: "2024-01-20T01:55:00.000Z",
    duration_seconds: 21600.0,
    location_start_lat: 19.1,
    location_start_lon: 72.8,
    location_end_lat: 18.2,
    location_end_lon: 72.8,
    geometry_geojson: {
      type: "LineString",
      coordinates: [
        [72.8, 19.1],
        [72.8, 18.2]
      ]
    },
    anomaly_score: 0.25,
    context_indicators: {
      gap_duration_hours: 6.0
    },
    description: "Transponder gap of 6.0 hours detected."
  },
  {
    anomaly_id: "b74aa7c9-e870-4d2c-8a2e-1402a32e3d5c",
    mmsi: "413987654",
    anomaly_type: "ABNORMAL_SPEED_DROP",
    severity_level: "MEDIUM",
    time_start: "2024-01-19T19:55:00.000Z",
    time_end: "2024-01-20T01:55:00.000Z",
    duration_seconds: 21600.0,
    location_start_lat: 19.1,
    location_start_lon: 72.8,
    location_end_lat: 18.2,
    location_end_lon: 72.8,
    geometry_geojson: {
      type: "Point",
      coordinates: [72.8, 18.2]
    },
    anomaly_score: 0.685,
    context_indicators: {
      initial_speed: 14.5,
      final_speed: 0.8
    },
    description: "Abnormal speed drop from 14.5 to 0.8 knots."
  }
];

export const mockVesselMetadataMap: Record<string, { vessel_name: string; ship_type: string }> = {
  "413123456": { vessel_name: "MV ARABIAN STAR", ship_type: "FISHING_VESSEL" }
};
