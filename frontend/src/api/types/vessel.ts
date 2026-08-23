export interface Vessel {
  vessel_id: string; // uuid
  mmsi: string;
  imo: string | null;
  callsign?: string | null;
  vessel_name: string;
  ship_type: 'TANKER_CRUDE_OIL' | 'TANKER_PRODUCT' | 'TANKER_CHEMICAL' | 'CARGO_CONTAINER' | 'CARGO_BULK_CARRIER' | 'CARGO_GENERAL' | 'FISHING_VESSEL' | 'PASSENGER_FERRY' | 'TUG_SERVICE' | 'SPECIALIZED_OFFSHORE' | 'OTHER' | 'UNKNOWN';
  flag_country?: string | null;
  flag_iso2?: string | null;
  length_meters: number;
  beam_meters: number;
  draft_meters?: number | null;
  gross_tonnage?: number | null;
  deadweight_tonnage?: number | null;
  risk_profile?: 'HIGH_RISK_CARRIER' | 'MODERATE_RISK' | 'STANDARD_COMMERCIAL' | 'LOW_RISK' | 'UNASSESSED';
}

export interface AISObservation {
  observation_id: string; // uuid
  mmsi: string;
  timestamp: string; // iso
  latitude: number;
  longitude: number;
  speed_over_ground_knots: number;
  course_over_ground_deg: number;
  heading_deg?: number | null;
  navigational_status: 'UNDER_WAY_USING_ENGINE' | 'AT_ANCHOR' | 'NOT_UNDER_COMMAND' | 'RESTRICTED_MANOEUVRABILITY' | 'CONSTRAINED_BY_DRAUGHT' | 'MOORED' | 'AGROUND' | 'ENGAGED_IN_FISHING' | 'UNDER_WAY_SAILING' | 'RESERVED_HSC' | 'RESERVED_WIG' | 'AIS_SART_ACTIVE' | 'UNDEFINED';
  rate_of_turn_deg_per_min?: number | null;
  source_provider: 'GLOBAL_FISHING_WATCH' | 'INCOIS' | 'DG_SHIPPING' | 'TERRESTRIAL_AIS' | 'SATELLITE_AIS' | 'MOCK_SIMULATOR';
}

export interface AISTrack {
  track_id: string; // uuid
  mmsi: string;
  time_start: string; // iso
  time_end: string; // iso
  observations_count: number;
  trajectory_geojson: {
    type: 'LineString';
    coordinates: number[][]; // [lon, lat, timestamp]
  };
  bbox_wgs84: [number, number, number, number];
  total_distance_km: number;
  avg_speed_knots: number;
  max_speed_knots: number;
  min_speed_knots?: number;
  gap_count?: number;
}

export interface SARVesselDetection {
  detection_id: string; // uuid
  source_granule_id: string;
  detection_timestamp: string; // iso
  centroid_lat: number;
  centroid_lon: number;
  bounding_box_geojson: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  estimated_length_meters: number;
  estimated_width_meters: number;
  estimated_heading_deg?: number | null;
  radar_cross_section_db: number;
  peak_backscatter_sigma0_db?: number;
  background_clutter_db?: number;
  signal_to_clutter_ratio_db: number;
  detection_confidence: number;
  polarization_used: 'VH' | 'VV' | 'DUAL_POL';
}

export interface VesselMatch {
  match_id: string; // uuid
  sar_detection_id: string; // uuid
  matched_mmsi: string;
  match_status: 'MATCHED' | 'UNCERTAIN_MATCH' | 'UNMATCHED';
  match_confidence: number;
  distance_offset_meters: number;
  timestamp_offset_seconds: number;
  heading_delta_deg?: number | null;
  speed_delta_knots?: number | null;
  dimension_match_score: number;
  reconciliation_algorithm: 'DETERMINISTIC_SPATIO_TEMPORAL_HEURISTIC_V1';
}

export interface UnmatchedVessel {
  unmatched_id: string; // uuid
  sar_detection_id: string; // uuid
  source_granule_id: string;
  detection_timestamp: string; // iso
  centroid_lat: number;
  centroid_lon: number;
  estimated_length_meters: number;
  estimated_width_meters: number;
  detection_confidence: number;
  ais_search_radius_km: number;
  ais_time_window_minutes: number;
  candidate_vessels_searched_count: number;
  dark_vessel_confidence: number;
  nearest_ais_vessel_mmsi?: string | null;
  distance_to_nearest_ais_meters?: number | null;
  description?: string;
}

export interface AnomalyEvent {
  anomaly_id: string; // uuid
  mmsi: string;
  anomaly_type: 'AIS_TRANSMISSION_GAP' | 'ABNORMAL_SPEED_DROP' | 'COURSE_DEVIATION_LOITERING' | 'SUDDEN_U_TURN' | 'DRAFT_CHANGE_DISCHARGE' | 'SUSPICIOUS_PROXIMITY_RENDEZVOUS';
  severity_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  time_start: string; // iso
  time_end: string; // iso
  duration_seconds: number;
  location_start_lat: number;
  location_start_lon: number;
  location_end_lat?: number | null;
  location_end_lon?: number | null;
  geometry_geojson?: any;
  anomaly_score: number;
  context_indicators: Record<string, number | string | boolean>;
  description: string;
}

export interface SelectedVesselData {
  id: string;
  category: 'MATCHED' | 'UNMATCHED' | 'AIS_ONLY' | 'SAR_ONLY';
  mmsi?: string | null;
  vessel_name?: string | null;
  ship_type?: string | null;
  coordinates: [number, number]; // [lon, lat]
  timestamp?: string | null;
  ais_obs?: AISObservation | null;
  sar_det?: SARVesselDetection | null;
  match?: VesselMatch | null;
  unmatched?: UnmatchedVessel | null;
  anomalies?: AnomalyEvent[];
}
