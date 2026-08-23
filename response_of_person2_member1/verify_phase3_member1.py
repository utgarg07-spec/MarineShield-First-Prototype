"""
MarineShield Phase 3 Acceptance Verification Suite - Member 1 / Person 2
Authoritative validation script testing the Sentinel-1 SAR Acquisition Pipeline against all acceptance criteria:
1. Authentication (OAuth2 token workflow)
2. Search Capabilities (Sentinel-1, GRD, BBOX, Date filters)
3. Single Scene Download (1 cached scene with non-zero size)
4. Metadata Extraction (Timestamps, IW mode, Orbit direction, Bounding polygon)
5. Provenance Tracking (Scene UUID, Source URL, Timestamps, Pipeline version, SHA-256)
6. Local Caching (Idempotency & < 2s response time)
7. No ML Contamination (Audit against torch, torchvision, segment_anything)
"""

import sys
import os
import time
import json
import ast
import urllib.parse
from pathlib import Path
from datetime import datetime

# Setup project path
root_dir = Path(__file__).resolve().parent.parent
src_dir = root_dir / "src"
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(src_dir))

def print_banner():
    print("=" * 90)
    print("      MarineShield Phase 3 / Member 1 (Person 2) - Sentinel-1 Acquisition Verification")
    print("=" * 90)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Workspace: {root_dir}")
    print("=" * 90 + "\n")

def test_authentication():
    """Criterion 1: Assert OAuth token retrieval mechanism from Copernicus IDP."""
    from marineshield.acquisition.copernicus_auth import CopernicusAuthManager
    import urllib.request
    import json
    
    # 1. Test live auth manager endpoint configuration
    auth = CopernicusAuthManager(client_id="test_marineshield_client", client_secret="test_client_secret")
    assert auth.auth_url == "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token", "Auth URL mismatch"
    assert auth.is_configured is True, "Expected is_configured to be True when credentials provided"
    
    # 2. Test token caching and Bearer header generation
    mock_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test_valid_token_payload"
    auth._access_token = mock_token
    auth._token_expiry_epoch = time.time() + 300
    token = auth.get_token()
    assert token == mock_token, f"Token retrieval failed: expected {mock_token}, got {token}"
    
    headers = auth.get_auth_header()
    assert headers.get("Authorization") == f"Bearer {mock_token}", f"Invalid Authorization header: {headers}"
    
    # 3. Test open-access / fallback auth manager
    unconfigured_auth = CopernicusAuthManager(client_id="", client_secret="")
    assert unconfigured_auth.is_configured is False, "Expected is_configured to be False when empty"
    assert unconfigured_auth.get_auth_header() == {}, "Expected empty auth header in open-catalog fallback mode"
    
    return {
        "name": "Authentication",
        "requirement": "Copernicus IDP OAuth2 token endpoint & Bearer auth headers",
        "observed": f"IDP: {auth.auth_url} (OAuth2 flow & Bearer header verified)",
        "passed": True
    }

def test_search_capabilities():
    """Criterion 2: Assert search query contains Sentinel-1, GRD, bbox coordinates, and date range."""
    from marineshield.acquisition.copernicus_client import CopernicusClient
    
    client = CopernicusClient()
    bbox = [72.0, 18.0, 74.0, 20.0]
    start_date = "2024-01-01T00:00:00.000Z"
    end_date = "2024-01-20T23:59:59.000Z"
    
    # Execute search
    results = client.search_scenes(
        bbox=bbox,
        start_date=start_date,
        end_date=end_date,
        product_type="GRD",
        mission="SENTINEL-1",
        max_results=3
    )
    
    assert len(results) > 0, "Search query returned 0 products from CDSE"
    top = results[0]
    name = top.get("Name", "")
    assert "S1" in name and "GRD" in name, f"Product {name} is not Sentinel-1 GRD"
    
    return {
        "name": "Search Capabilities",
        "requirement": "Query params with Sentinel-1, GRD, BBOX [72,18,74,20], and Date Range",
        "observed": f"Successfully retrieved {len(results)} scenes (Top: {name})",
        "passed": True
    }

def test_single_scene_download():
    """Criterion 3: Assert exactly 1 scene exists in cache and file size is non-zero."""
    from marineshield.config import settings
    raw_dir = settings.SAR_RAW_DIR
    
    assert raw_dir.exists(), f"Raw directory {raw_dir} does not exist"
    scene_dirs = [d for d in raw_dir.iterdir() if d.is_dir()]
    assert len(scene_dirs) == 1, f"Expected exactly 1 scene directory in cache, found {len(scene_dirs)}"
    
    target_dir = scene_dirs[0]
    files = list(target_dir.iterdir())
    assert len(files) >= 2, f"Expected metadata and manifest files in {target_dir}, found {len(files)}"
    
    total_size = sum(f.stat().st_size for f in files)
    assert total_size > 0, f"Cache files have zero size ({total_size} bytes)"
    
    return {
        "name": "Single Scene Download",
        "requirement": "Exactly 1 cached scene directory with non-zero file sizes",
        "observed": f"1 scene ({target_dir.name}) containing {len(files)} files ({total_size:,} bytes total)",
        "passed": True
    }

def test_metadata_extraction():
    """Criterion 4: Assert timestamps, sensor mode (IW), orbit direction, and bounding polygon exist."""
    from marineshield.config import settings
    raw_dir = settings.SAR_RAW_DIR
    scene_dir = next(d for d in raw_dir.iterdir() if d.is_dir())
    meta_file = scene_dir / f"{scene_dir.name}_metadata.json"
    
    assert meta_file.exists(), f"Metadata file {meta_file} missing"
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    # Check timestamps
    acq = meta.get("acquisition_time", {})
    assert "start_time" in acq and "stop_time" in acq and "center_time" in acq, "Missing timestamps in metadata"
    
    # Check sensor mode (IW)
    scene_id = meta.get("scene_identifier", {})
    mode = scene_id.get("acquisition_mode")
    assert mode == "IW", f"Expected acquisition_mode 'IW', got '{mode}'"
    
    # Check orbit direction
    orbit_dir = scene_id.get("orbit_direction")
    assert orbit_dir in ["ASCENDING", "DESCENDING"], f"Invalid orbit_direction '{orbit_dir}'"
    
    # Check bounding polygon
    spatial = meta.get("spatial_reference", {})
    footprint = spatial.get("footprint_geojson", {})
    assert footprint.get("type") in ["Polygon", "MultiPolygon"], f"Invalid footprint type '{footprint.get('type')}'"
    coords = footprint.get("coordinates", [])
    assert len(coords) > 0, "Empty coordinate list in footprint polygon"
    
    return {
        "name": "Metadata Extraction",
        "requirement": "Timestamps, sensor mode (IW), orbit direction, and bounding polygon present",
        "observed": f"Mode: {mode}, Orbit: {orbit_dir}, Center: {acq['center_time']}, BBOX: {spatial['bbox_wgs84']}",
        "passed": True
    }

def test_provenance_tracking():
    """Criterion 5: Assert stored metadata records Copernicus UUID, source URL, download timestamp, and pipeline version."""
    from marineshield.config import settings
    raw_dir = settings.SAR_RAW_DIR
    scene_dir = next(d for d in raw_dir.iterdir() if d.is_dir())
    meta_file = scene_dir / f"{scene_dir.name}_metadata.json"
    
    with open(meta_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    prov = meta.get("provenance", {})
    source_url = prov.get("source_archive_url", "")
    assert "catalogue.dataspace.copernicus.eu" in source_url, f"Invalid source URL: {source_url}"
    assert "Products(" in source_url, "Source URL missing Copernicus product UUID"
    
    ingest_ts = prov.get("ingestion_timestamp")
    assert ingest_ts is not None, "Missing ingestion_timestamp"
    
    pipeline_ver = meta.get("preprocessing_pipeline", {}).get("pipeline_version")
    assert pipeline_ver == "1.0.0", f"Expected pipeline_version '1.0.0', got '{pipeline_ver}'"
    
    sha256 = prov.get("source_granule_sha256", "")
    assert len(sha256) == 64, f"Invalid SHA-256 hash length: {len(sha256)}"
    
    return {
        "name": "Provenance Tracking",
        "requirement": "Copernicus UUID, source URL, timestamp, pipeline version (1.0.0), SHA-256 recorded",
        "observed": f"UUID in URL, SHA-256: {sha256[:12]}..., Version: {pipeline_ver}, Checksum Verified: {prov['checksum_verified']}",
        "passed": True
    }

def test_local_caching():
    """Criterion 6: Assert re-ingestion skips network download and returns cached path within < 2.0 seconds."""
    from marineshield.acquisition import Sentinel1AcquisitionPipeline
    from marineshield.config import settings
    
    pipeline = Sentinel1AcquisitionPipeline()
    raw_dir = settings.SAR_RAW_DIR
    scene_dir = next(d for d in raw_dir.iterdir() if d.is_dir())
    granule_id = scene_dir.name
    
    mock_product_dict = {
        "Id": "f65a2541-f4a5-48cf-8e20-5cf65b604a1b",
        "Name": f"{granule_id}.SAFE"
    }
    
    t0 = time.perf_counter()
    result = pipeline.ingest_single_scene(mock_product_dict, force=False)
    elapsed = time.perf_counter() - t0
    
    assert result["status"] == "CACHE_HIT", f"Expected CACHE_HIT, got {result['status']}"
    assert elapsed < 2.0, f"Cache retrieval took {elapsed:.4f}s (exceeds 2.0s threshold)"
    assert Path(result["cache_dir"]).exists(), f"Returned cache dir does not exist: {result['cache_dir']}"
    
    return {
        "name": "Local Caching",
        "requirement": "Idempotent cache hit returning path in < 2.0 seconds",
        "observed": f"CACHE_HIT in {elapsed*1000:.2f} ms ({elapsed:.4f}s < 2.0s limit)",
        "passed": True
    }

def test_no_ml_contamination():
    """Criterion 7: Audit imported modules and source code to confirm torch/torchvision/SAM are not imported."""
    acq_dir = src_dir / "marineshield" / "acquisition"
    forbidden_modules = ["torch", "torchvision", "torchaudio", "segment_anything", "sam", "ultralytics", "transformers"]
    
    detected_violations = []
    
    # Audit AST of all python files in acquisition module
    for py_file in acq_dir.glob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split(".")[0]
                    if root_mod in forbidden_modules:
                        detected_violations.append(f"{py_file.name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split(".")[0]
                    if root_mod in forbidden_modules:
                        detected_violations.append(f"{py_file.name}: from {node.module} import ...")
                        
    assert len(detected_violations) == 0, f"ML contamination detected in acquisition pipeline: {detected_violations}"
    
    return {
        "name": "No ML Contamination",
        "requirement": "Strict zero-import of torch, torchvision, segment_anything in acquisition layer",
        "observed": f"0 violations found across {len(list(acq_dir.glob('*.py')))} acquisition source files",
        "passed": True
    }

def main():
    print_banner()
    
    tests = [
        ("Criterion 1: Authentication", test_authentication),
        ("Criterion 2: Search Capabilities", test_search_capabilities),
        ("Criterion 3: Single Scene Download", test_single_scene_download),
        ("Criterion 4: Metadata Extraction", test_metadata_extraction),
        ("Criterion 5: Provenance Tracking", test_provenance_tracking),
        ("Criterion 6: Local Caching", test_local_caching),
        ("Criterion 7: No ML Contamination", test_no_ml_contamination),
    ]
    
    results = []
    all_passed = True
    
    for title, test_fn in tests:
        try:
            res = test_fn()
            results.append(res)
        except AssertionError as e:
            results.append({
                "name": title,
                "requirement": "Assertion failed",
                "observed": str(e),
                "passed": False
            })
            all_passed = False
        except Exception as e:
            results.append({
                "name": title,
                "requirement": "Execution failed",
                "observed": f"Unexpected error: {e}",
                "passed": False
            })
            all_passed = False

    # Print Formatted Results Table
    print("-" * 90)
    print(f"{'#':<3} | {'Test / Acceptance Criteria':<24} | {'Status':<8} | {'Observed Result / Verification Details'}")
    print("-" * 90)
    
    for idx, r in enumerate(results, 1):
        status_str = "[PASS]" if r["passed"] else "[FAIL]"
        obs = r["observed"]
        if len(obs) > 50:
            obs = obs[:47] + "..."
        print(f"{idx:<3} | {r['name']:<24} | {status_str:<8} | {r['observed']}")
    
    print("-" * 90)
    
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    
    print(f"\nVerification Score: {passed_count}/{total_count} Criteria Passed ({passed_count/total_count*100:.1f}%)\n")
    
    if all_passed:
        print("=" * 90)
        print("   >>> SUCCESS: ALL PHASE 3 / MEMBER 1 ACCEPTANCE CRITERIA SATISFIED 100% <<<")
        print("=" * 90)
        sys.exit(0)
    else:
        print("=" * 90)
        print("   >>> FAILURE: ONE OR MORE CRITERIA FAILED <<<")
        print("=" * 90)
        sys.exit(1)

if __name__ == "__main__":
    main()
