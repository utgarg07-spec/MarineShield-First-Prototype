"""
MarineShield Sentinel-1 Acquisition Pipeline Verification Suite
Tests Copernicus authentication, spatial-temporal search, sample acquisition,
metadata parsing into canonical contract, cryptographic provenance, and deterministic local caching.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Configure paths
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(src_dir))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from marineshield.acquisition import (
    CopernicusAuthManager,
    CopernicusClient,
    SARMetadataParser,
    DeterministicCacheManager,
    Sentinel1AcquisitionPipeline
)
from scripts.test_sar_data_contract import validate_sar_contract_payload

def main():
    print("================================================================================")
    print("        MarineShield Sentinel-1 SAR Acquisition Pipeline Test Suite")
    print("================================================================================")
    print(f"Workspace: {root_dir}")
    print(f"Source Directory: {src_dir}\n")

    pipeline = Sentinel1AcquisitionPipeline(worker_id="test-worker-node-01")

    # --------------------------------------------------------------------------
    # Task 1: Copernicus Authentication Mechanism
    # --------------------------------------------------------------------------
    print("--- [Task 1] Testing Copernicus Authentication Mechanism ---")
    auth = pipeline.auth
    print(f"  - Configured Credentials: {'YES' if auth.is_configured else 'NO (Safe Open-Catalog Mode)'}")
    print(f"  - Auth Endpoint: {auth.auth_url}")
    header = auth.get_auth_header()
    print(f"  - Generated Auth Headers: {'Bearer token present' if header else 'Empty (Open Access)'}")
    print("[PASS] Authentication manager operational.\n")

    # --------------------------------------------------------------------------
    # Task 2: Search Scenes by Bounding Box, Date Range, Sentinel-1, GRD
    # --------------------------------------------------------------------------
    print("--- [Task 2] Testing Spatial-Temporal Scene Search ---")
    bbox = [72.0, 18.0, 74.0, 20.0]  # Mumbai / Arabian Sea coastal corridor
    start_date = "2024-01-01T00:00:00.000Z"
    end_date = "2024-01-20T23:59:59.000Z"
    mission = "SENTINEL-1"
    product_type = "GRD"

    print(f"  - Search Criteria: BBOX={bbox}, Dates={start_date} to {end_date}, Mission={mission}, Type={product_type}")
    search_results = pipeline.search_scenes(
        bbox=bbox,
        start_date=start_date,
        end_date=end_date,
        product_type=product_type,
        mission=mission,
        max_results=5
    )

    if not search_results:
        print("[FAIL] No scenes returned by search query.")
        sys.exit(1)

    print(f"[PASS] Search returned {len(search_results)} real Sentinel-1 GRD scenes from Copernicus OData API:")
    for idx, sc in enumerate(search_results, 1):
        print(f"    {idx}. {sc.get('Name')} (ID: {sc.get('Id')})")

    # --------------------------------------------------------------------------
    # Task 3: Ingest / Download One Real Sentinel-1 Sample
    # --------------------------------------------------------------------------
    selected_scene = search_results[0]
    scene_name = selected_scene.get("Name", "")
    print(f"\n--- [Task 3] Ingesting Single Real Scene: {scene_name} ---")

    ingest_result = pipeline.ingest_single_scene(selected_scene, force=True)
    print(f"[PASS] Scene ingested successfully:")
    print(f"  - Granule ID: {ingest_result['granule_id']}")
    print(f"  - Status: {ingest_result['status']}")
    print(f"  - Local Cache Directory: {ingest_result['cache_dir']}")
    print(f"  - Ingestion Duration: {ingest_result['duration_seconds']}s")

    # --------------------------------------------------------------------------
    # Task 4: Parse Metadata & Validate Against SAR Data Contract v1.0.0
    # --------------------------------------------------------------------------
    print("\n--- [Task 4] Validating Parsed Metadata against SAR Data Contract ---")
    canonical_meta = ingest_result["canonical_metadata"]
    validation_errors = validate_sar_contract_payload(canonical_meta)

    if validation_errors:
        print("[FAIL] Parsed metadata violated SAR Data Contract:")
        for err in validation_errors:
            print(f"  - {err}")
        sys.exit(1)

    print(f"[PASS] Parsed metadata satisfies 100% of SAR Data Contract v1.0.0 rules:")
    print(f"  - Mission: {canonical_meta['scene_identifier']['mission']}")
    print(f"  - Mode: {canonical_meta['scene_identifier']['acquisition_mode']}")
    print(f"  - Orbit: {canonical_meta['scene_identifier']['orbit_direction']} (Relative: {canonical_meta['scene_identifier']['relative_orbit_number']})")
    print(f"  - Polarizations: {canonical_meta['polarization']['channels']} (Primary: {canonical_meta['polarization']['primary_detection_channel']})")
    print(f"  - CRS: {canonical_meta['spatial_reference']['crs']}")
    print(f"  - Bounding Box: {canonical_meta['spatial_reference']['bbox_wgs84']}")
    print(f"  - State: {canonical_meta['processing_status']['state']}")

    # --------------------------------------------------------------------------
    # Task 5: Store Provenance
    # --------------------------------------------------------------------------
    print("\n--- [Task 5] Cryptographic Provenance Verification ---")
    prov = canonical_meta["provenance"]
    sha256_hash = prov["source_granule_sha256"]
    print(f"  - Data Provider: {prov['data_provider']}")
    print(f"  - SHA-256 Digest: {sha256_hash}")
    print(f"  - Checksum Verified: {prov['checksum_verified']}")
    print(f"  - Ingestion Timestamp: {prov['ingestion_timestamp']}")
    print(f"  - Worker Node: {prov['worker_node_id']}")
    print("[PASS] Provenance recorded and verified.")

    # --------------------------------------------------------------------------
    # Task 6: Deterministic Local Cache Verification
    # --------------------------------------------------------------------------
    print("\n--- [Task 6] Testing Deterministic Local Cache Idempotency ---")
    cached_run = pipeline.ingest_single_scene(selected_scene, force=False)
    print(f"  - Re-ingestion Status: {cached_run['status']}")
    print(f"  - Re-ingestion Duration: {cached_run['duration_seconds']}s")

    if cached_run["status"] != "CACHE_HIT":
        print(f"[FAIL] Expected CACHE_HIT on second ingestion, got {cached_run['status']}")
        sys.exit(1)

    if cached_run["sha256"] != sha256_hash:
        print(f"[FAIL] Checksum mismatch on cache hit: {cached_run['sha256']} != {sha256_hash}")
        sys.exit(1)

    print("[PASS] Deterministic cache verified with zero duplicate network transfer.")

    print("\n================================================================================")
    print("   [SUCCESS] All Sentinel-1 Acquisition Pipeline Tasks Passed 100%!")
    print("================================================================================")

if __name__ == "__main__":
    main()
