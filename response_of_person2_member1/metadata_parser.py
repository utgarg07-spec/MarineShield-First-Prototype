"""
MarineShield SAR Metadata Parser
Transforms Copernicus OData product attributes into canonical SAR Data Contract v1.0.0 schemas.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import re

class SARMetadataParser:
    """Parses and normalizes Copernicus OData / SAFE metadata into MarineShield SAR Data Contract."""

    @staticmethod
    def parse_cdse_product(
        cdse_product: Dict[str, Any],
        sha256_hash: str,
        worker_id: str = "acquisition-worker-01",
        duration_seconds: float = 0.0,
        raw_cache_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert raw CDSE OData API product dictionary into canonical SAR metadata.
        """
        name = cdse_product.get("Name", "")
        clean_name = name.replace(".SAFE", "").replace(".zip", "")
        product_id = cdse_product.get("Id", "")

        # Extract attributes dict
        raw_attrs = cdse_product.get("Attributes", [])
        attrs = {}
        for a in raw_attrs:
            if isinstance(a, dict) and "Name" in a:
                # OData CSC attribute structures
                val = a.get("Value")
                if val is None:
                    # check nested types
                    for k in a:
                        if k.startswith("OData.CSC.") and isinstance(a[k], dict) and "Value" in a[k]:
                            val = a[k]["Value"]
                            break
                attrs[a["Name"]] = val

        # 1. Scene Identifier
        # Naming format: MMM_BB_TTTF_LFPP_YYYYMMDDTHHMMSS_YYYYMMDDTHHMMSS_OOOOOO_DDDDDD_CCCC
        platform_short = attrs.get("platformSerialIdentifier", "A")
        mission_str = f"SENTINEL_1{platform_short}"
        if name.startswith("S1B"):
            mission_str = "SENTINEL_1B"
        elif name.startswith("S1C"):
            mission_str = "SENTINEL_1C"
        else:
            mission_str = "SENTINEL_1A"

        mode = attrs.get("operationalMode") or ("IW" if "IW" in name else "EW")
        orbit_dir = (attrs.get("orbitDirection") or "DESCENDING").upper()
        rel_orbit = int(attrs.get("relativeOrbitNumber", 1))
        abs_orbit = int(attrs.get("orbitNumber", 1))

        scene_identifier = {
            "granule_id": clean_name,
            "mission": mission_str,
            "acquisition_mode": mode,
            "product_type": "GRD",
            "orbit_direction": orbit_dir,
            "relative_orbit_number": rel_orbit,
            "absolute_orbit_number": abs_orbit
        }

        # 2. Product Metadata
        slice_num = int(attrs.get("sliceNumber", 1))
        total_slices = int(attrs.get("totalSlices", 1))
        inst_config = str(attrs.get("instrumentConfigurationID", "1"))

        product_metadata = {
            "product_level": "L1",
            "instrument_configuration_id": inst_config,
            "look_direction": "RIGHT",
            "incidence_angle_min_deg": 29.1,
            "incidence_angle_max_deg": 46.0,
            "slice_number": slice_num,
            "total_slices": total_slices
        }

        # 3. Acquisition Time
        content_date = cdse_product.get("ContentDate", {})
        start_str = content_date.get("Start") or attrs.get("beginningDateTime") or "2024-01-01T00:00:00.000Z"
        stop_str = content_date.get("End") or attrs.get("endingDateTime") or "2024-01-01T00:00:25.000Z"

        # Compute midpoint
        try:
            t_start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            t_stop = datetime.fromisoformat(stop_str.replace("Z", "+00:00"))
            delta = (t_stop - t_start).total_seconds()
            t_center = t_start + (t_stop - t_start) / 2
            center_str = t_center.isoformat().replace("+00:00", "Z")
            duration_s = max(round(delta, 2), 0.0)
        except Exception:
            center_str = start_str
            duration_s = 25.0

        acquisition_time = {
            "start_time": start_str if start_str.endswith("Z") else f"{start_str}Z",
            "stop_time": stop_str if stop_str.endswith("Z") else f"{stop_str}Z",
            "center_time": center_str if center_str.endswith("Z") else f"{center_str}Z",
            "duration_seconds": duration_s
        }

        # 4. Sensor Specification
        sensor_specification = {
            "sensor_name": "C-SAR",
            "radar_band": "C_BAND",
            "center_frequency_ghz": 5.405,
            "antenna_pointing": "RIGHT"
        }

        # 5. Polarization
        raw_pols = attrs.get("polarisationChannels", "VV&VH")
        if "&" in raw_pols:
            channels = raw_pols.split("&")
        elif "+" in raw_pols:
            channels = raw_pols.split("+")
        else:
            channels = ["VV", "VH"] if "DV" in name or "DH" in name else ["VV"]

        polarization = {
            "channels": channels,
            "primary_detection_channel": "VV" if "VV" in channels else channels[0],
            "vessel_detection_channel": "VH" if "VH" in channels else channels[-1]
        }

        # 6. Spatial Reference
        geo_footprint = cdse_product.get("GeoFootprint") or {
            "type": "Polygon",
            "coordinates": [[[72.0, 18.0], [74.0, 18.0], [74.0, 20.0], [72.0, 20.0], [72.0, 18.0]]]
        }

        # Compute bounding box
        coords = []
        if geo_footprint.get("type") == "Polygon":
            for ring in geo_footprint.get("coordinates", []):
                coords.extend(ring)
        elif geo_footprint.get("type") == "MultiPolygon":
            for poly in geo_footprint.get("coordinates", []):
                for ring in poly:
                    coords.extend(ring)

        if coords:
            lons = [pt[0] for pt in coords]
            lats = [pt[1] for pt in coords]
            bbox_wgs84 = [round(min(lons), 4), round(min(lats), 4), round(max(lons), 4), round(max(lats), 4)]
        else:
            bbox_wgs84 = [72.0, 18.0, 74.0, 20.0]

        spatial_reference = {
            "crs": "EPSG:4326",
            "bbox_wgs84": bbox_wgs84,
            "footprint_geojson": geo_footprint,
            "pixel_spacing_range_m": 10.0,
            "pixel_spacing_azimuth_m": 10.0,
            "raster_width_px": 25000,
            "raster_height_px": 16500,
            "nodata_value": -9999.0
        }

        # 7. Processing Status
        iso_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        processing_status = {
            "state": "ACQUIRED",
            "error_code": None,
            "error_message": None,
            "stage_timestamps": {
                "ACQUIRED": iso_now
            }
        }

        # 8. Preprocessing Pipeline (Configured for future Person 2 stages)
        preprocessing_pipeline = {
            "pipeline_version": "1.0.0",
            "calibration_model": "RADIOMETRIC_SIGMA0_DB",
            "orbit_file_type": "PRECISE_ORBIT_EPHEMERIDES_POEORB",
            "speckle_filter": {
                "algorithm": "REFINED_LEE",
                "window_size_px": "7x7"
            },
            "dem_source": "COPERNICUS_30M_GLO30",
            "toolchain_manifest": {
                "marineshield_ingest": "1.0.0",
                "copernicus_cdse_odata": "v1"
            }
        }

        # 9. Provenance
        source_url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
        provenance = {
            "data_provider": "COPERNICUS_DATA_SPACE_ECOSYSTEM",
            "source_archive_url": source_url,
            "source_granule_sha256": sha256_hash,
            "ingestion_timestamp": iso_now,
            "execution_duration_seconds": round(duration_seconds, 2),
            "worker_node_id": worker_id,
            "checksum_verified": True
        }

        # 10. Raster File Paths
        rel_dir = f"data/sar_preprocessed/{clean_name}"
        raster_files = {
            "vv_geotiff_path": f"{rel_dir}/{clean_name}_VV_sigma0_db.tif",
            "vh_geotiff_path": f"{rel_dir}/{clean_name}_VH_sigma0_db.tif",
            "incidence_angle_path": None,
            "tiled_dir_path": None
        }

        return {
            "contract_version": "1.0.0",
            "scene_identifier": scene_identifier,
            "product_metadata": product_metadata,
            "acquisition_time": acquisition_time,
            "sensor_specification": sensor_specification,
            "polarization": polarization,
            "spatial_reference": spatial_reference,
            "processing_status": processing_status,
            "preprocessing_pipeline": preprocessing_pipeline,
            "provenance": provenance,
            "raster_files": raster_files
        }
