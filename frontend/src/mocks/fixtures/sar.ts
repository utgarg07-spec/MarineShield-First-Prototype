/**
 * SAR mock fixtures — contract-faithful adapters.
 * 
 * SOURCE: docs/handoffs/sar_scene_handoff.json (verbatim)
 * SOURCE: docs/handoffs/sar_tile_handoff.json (verbatim)
 * 
 * All values are SOURCE_DERIVED from the authoritative handoff artifacts.
 * The SAR scene metadata conforms to SAR_DATA_CONTRACT.md schema.
 */
import type { SARSceneMetadata, SARTile } from '../../api/types/sar';

/**
 * Single SAR scene from sar_scene_handoff.json.
 * Verbatim field mapping — no fabricated values.
 */
export const mockSARScene: SARSceneMetadata = {
  contract_version: '1.0.0',
  scene_identifier: {
    granule_id: 'S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2',
    mission: 'SENTINEL_1A',
    acquisition_mode: 'IW',
    product_type: 'GRD',
    orbit_direction: 'DESCENDING',
    relative_orbit_number: 136,
    absolute_orbit_number: 52183,
  },
  product_metadata: {
    product_level: 'L1',
    instrument_configuration_id: '7',
    look_direction: 'RIGHT',
    incidence_angle_min_deg: 29.1,
    incidence_angle_max_deg: 46.0,
    slice_number: 16,
    total_slices: 19,
  },
  acquisition_time: {
    start_time: '2024-01-20T00:55:28.704Z',
    stop_time: '2024-01-20T00:55:53.702Z',
    center_time: '2024-01-20T00:55:41.203Z',
    duration_seconds: 25.0,
  },
  sensor_specification: {
    sensor_name: 'C-SAR',
    radar_band: 'C_BAND',
    center_frequency_ghz: 5.405,
    antenna_pointing: 'RIGHT',
  },
  polarization: {
    channels: ['VV', 'VH'],
    primary_detection_channel: 'VV',
    vessel_detection_channel: 'VH',
  },
  spatial_reference: {
    crs: 'EPSG:4326',
    bbox_wgs84: [73.046, 17.1562, 75.7201, 19.0991],
    footprint_geojson: {
      type: 'Polygon',
      coordinates: [
        [
          [75.405884, 17.156162],
          [75.720078, 18.666897],
          [73.339149, 19.099094],
          [73.045975, 17.591869],
          [75.405884, 17.156162],
        ],
      ],
    },
    pixel_spacing_range_m: 10.0,
    pixel_spacing_azimuth_m: 10.0,
    raster_width_px: 25000,
    raster_height_px: 16500,
    nodata_value: -9999.0,
  },
  processing_status: {
    state: 'ACQUIRED',
    error_code: null,
    error_message: null,
    stage_timestamps: {
      ACQUIRED: '2026-08-21T11:52:32.736Z',
    },
  },
  preprocessing_pipeline: {
    pipeline_version: '1.0.0',
    calibration_model: 'RADIOMETRIC_SIGMA0_DB',
    orbit_file_type: 'PRECISE_ORBIT_EPHEMERIDES_POEORB',
    speckle_filter: {
      algorithm: 'REFINED_LEE',
      window_size_px: '7x7',
    },
    dem_source: 'COPERNICUS_30M_GLO30',
    toolchain_manifest: {
      marineshield_ingest: '1.0.0',
      copernicus_cdse_odata: 'v1',
    },
  },
  provenance: {
    data_provider: 'COPERNICUS_DATA_SPACE_ECOSYSTEM',
    source_archive_url:
      'https://catalogue.dataspace.copernicus.eu/odata/v1/Products(f65a2541-f4a5-48cf-8e20-5cf65b604a1b)/$value',
    source_granule_sha256: '86a34992e014e3f83597489cddb0409f52e4383e299e84f7da88185d82671b29',
    ingestion_timestamp: '2026-08-21T11:52:32.736Z',
    execution_duration_seconds: 4.44,
    worker_node_id: 'sar-worker-node-01',
    checksum_verified: true,
  },
  raster_files: {
    vv_geotiff_path:
      'data/sar_preprocessed/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_VV_sigma0_db.tif',
    vh_geotiff_path:
      'data/sar_preprocessed/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_VH_sigma0_db.tif',
    incidence_angle_path: null,
    tiled_dir_path: 'data/sar_preprocessed/tiles',
  },
};

export const mockSARScenes: SARSceneMetadata[] = [mockSARScene];

export const mockSARTiles: SARTile[] = [
  {
    tile_id: "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train",
    source_granule_id: "S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2",
    tile_row: 0,
    tile_col: 0,
    pixel_bounds_yx: [0, 512, 0, 512],
    geo_bbox_wgs84: [73.046, 18.6186, 74.4124, 19.0991],
    tile_geojson_footprint: {
      type: "Polygon",
      coordinates: [
        [
          [73.046, 18.6186],
          [74.4124, 18.6186],
          [74.4124, 19.0991],
          [73.046, 19.0991],
          [73.046, 18.6186]
        ]
      ]
    },
    spatial_resolution_m: [10.0, 10.0],
    tile_dimensions_px: [512, 512],
    crs: "EPSG:4326",
    channels: ["VV", "VH"],
    normalization: {
      method: "linear_clip_db",
      min_db: -30.0,
      max_db: 0.0,
      clip_min: 0.0,
      clip_max: 1.0,
      formula: "clip((sigma0 - min_db)/(max_db - min_db), clip_min, clip_max)"
    },
    split: "train",
    sha256_hash: "0117ac56eaa0b0c265691ea4aefbfefbdcf785bc4ca5e28a5faeb2352aeeb450",
    pipeline_version: "1.0.0",
    npy_access_url: "/api/v1/sar/tiles/S1A_IW_GRDH_1SDV_20240120T005528_20240120T005553_052183_064ED6_FAD2_tile_r000_c000_train.npy"
  }
];
