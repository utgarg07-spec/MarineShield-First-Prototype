export interface SARSceneMetadata {
  contract_version: '1.0.0';
  scene_identifier: SceneIdentifier;
  product_metadata: ProductMetadata;
  acquisition_time: AcquisitionTime;
  sensor_specification: SensorSpecification;
  polarization: Polarization;
  spatial_reference: SpatialReference;
  processing_status: ProcessingStatus;
  preprocessing_pipeline: PreprocessingPipeline;
  provenance: Provenance;
  raster_files: RasterFiles;
}

export interface SceneIdentifier {
  granule_id: string;
  mission: 'SENTINEL_1A' | 'SENTINEL_1B' | 'SENTINEL_1C';
  acquisition_mode: 'IW' | 'EW' | 'SM';
  product_type: 'GRD' | 'SLC';
  orbit_direction: 'ASCENDING' | 'DESCENDING';
  relative_orbit_number: number;
  absolute_orbit_number: number;
}

export interface ProductMetadata {
  product_level: 'L1' | 'L2';
  instrument_configuration_id: string;
  look_direction: 'RIGHT' | 'LEFT';
  incidence_angle_min_deg: number;
  incidence_angle_max_deg: number;
  slice_number: number;
  total_slices: number;
}

export interface AcquisitionTime {
  start_time: string; // iso
  stop_time: string; // iso
  center_time: string; // iso
  duration_seconds: number;
}

export interface SensorSpecification {
  sensor_name: 'C-SAR';
  radar_band: 'C_BAND';
  center_frequency_ghz: 5.405;
  antenna_pointing: 'RIGHT';
}

export interface Polarization {
  channels: ('VV' | 'VH' | 'HH' | 'HV')[];
  primary_detection_channel: 'VV' | 'HH';
  vessel_detection_channel: 'VH' | 'HV';
}

export interface SpatialReference {
  crs: 'EPSG:4326';
  bbox_wgs84: [number, number, number, number];
  footprint_geojson: {
    type: 'Polygon' | 'MultiPolygon';
    coordinates: number[][][] | number[][][][];
  };
  pixel_spacing_range_m: number;
  pixel_spacing_azimuth_m: number;
  raster_width_px: number;
  raster_height_px: number;
  nodata_value: number;
}

export interface ProcessingStatus {
  state: 'PENDING' | 'ACQUIRED' | 'ORBIT_APPLIED' | 'CALIBRATED' | 'SPECKLE_FILTERED' | 'TERRAIN_CORRECTED' | 'TILED' | 'READY_FOR_INFERENCE' | 'FAILED' | 'CORRUPTED';
  error_code?: string | null;
  error_message?: string | null;
  stage_timestamps?: Record<string, string>;
}

export interface PreprocessingPipeline {
  pipeline_version: string;
  calibration_model: 'RADIOMETRIC_SIGMA0_DB' | 'RADIOMETRIC_GAMMA0_DB' | 'RADIOMETRIC_BETA0_DB';
  orbit_file_type: 'PRECISE_ORBIT_EPHEMERIDES_POEORB' | 'RESTITUTED_ORBIT_RESORB' | 'HEADER_ORBIT';
  speckle_filter: {
    algorithm: 'REFINED_LEE' | 'LEE' | 'FROST' | 'GAMMA_MAP' | 'NONE';
    window_size_px: string;
  };
  dem_source: 'COPERNICUS_30M_GLO30' | 'SRTM_1SEC_HGT' | 'AUTO_DEM';
  toolchain_manifest: Record<string, string>;
}

export interface Provenance {
  data_provider: 'COPERNICUS_DATA_SPACE_ECOSYSTEM' | 'ALASKA_SATELLITE_FACILITY' | 'LOCAL_ARCHIVE' | 'MOCK_SIMULATOR';
  source_archive_url: string;
  source_granule_sha256: string;
  ingestion_timestamp: string; // iso
  execution_duration_seconds: number;
  worker_node_id: string;
  checksum_verified: boolean;
}

export interface RasterFiles {
  vv_geotiff_path: string;
  vh_geotiff_path: string;
  incidence_angle_path?: string | null;
  tiled_dir_path?: string | null;
}

export interface SARTile {
  tile_id: string;
  source_granule_id: string;
  tile_row: number;
  tile_col: number;
  pixel_bounds_yx: [number, number, number, number];
  geo_bbox_wgs84: [number, number, number, number];
  tile_geojson_footprint: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  spatial_resolution_m: [number, number];
  tile_dimensions_px: [number, number];
  crs: string;
  channels: string[];
  normalization: {
    method: string;
    min_db: number;
    max_db: number;
    clip_min: number;
    clip_max: number;
    formula: string;
  };
  split: string;
  sha256_hash: string;
  pipeline_version: string;
  npy_access_url: string;
}
