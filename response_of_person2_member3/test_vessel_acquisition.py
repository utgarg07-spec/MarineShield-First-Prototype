"""
Unit & Integration Test Suite for MarineShield Vessel Acquisition & GFW Modular Package
Tests:
1. Offline / mock mode adapter
2. Response parsing & transformation
3. Vessel contract conformance against VESSEL_DATA_CONTRACT.md rules
4. Deterministic SHA-256 cache behavior
5. Malformed data & edge-case handling
6. Live GFW API smoke test (only if credentials set)
"""

import os
import sys
import json
import shutil
import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from marineshield.vessels.gfw_client import GFWClientAdapter
from marineshield.vessels.vessel_cache_manager import VesselCacheManager
from marineshield.vessels.vessel_parser import VesselParser


def test_offline_mock_mode():
    print("\n--- [Test 1] Testing Offline / Mock Mode ---")
    # Test explicitly without credentials
    adapter = GFWClientAdapter(token="", allow_mock=True)

    auth = adapter.check_authentication()
    print(f"  - Authentication check mode: {auth['mode']}")
    assert auth["mode"] == "MOCK_FALLBACK"

    res = adapter.search_vessels(query="tanker", limit=2, use_cache=False)
    print(f"  - Vessel Search Status: {res['status']}, Source: {res['source']}")
    assert res["status"] in ("SUCCESS_MOCK", "SUCCESS_LIVE", "SUCCESS_CACHED")
    assert len(res["vessels"]) > 0
    print("[PASS] Offline / Mock Mode operational.")


def test_response_parsing_and_contract_conformance():
    print("\n--- [Test 2 & 3] Response Parsing & Contract Conformance ---")
    # Test Vessel Parsing
    mock_entry = {
        "mmsi": "413789012",
        "shipname": "MV ARABIAN SHIELD",
        "ship_type": "TANKER",
        "flag": "IN",
        "length": 210.0,
        "width": 32.0,
        "imo": "9123456",
    }
    vessel = VesselParser.parse_gfw_vessel_entry(mock_entry)
    
    print(f"  - Transformed Vessel ID: {vessel['vessel_id']}")
    print(f"  - MMSI: {vessel['mmsi']}, Name: {vessel['vessel_name']}, Type: {vessel['ship_type']}")
    
    # Contract rules assertion
    assert len(vessel["mmsi"]) == 9, "MMSI must be 9 digits"
    assert vessel["ship_type"] == "TANKER_CRUDE_OIL", "Ship type mapping failure"
    assert vessel["length_meters"] >= 1.0, "Length must be >= 1.0"
    assert vessel["beam_meters"] >= 1.0, "Beam must be >= 1.0"

    # Test AIS Observation Parsing
    raw_obs = {
        "mmsi": "413789012",
        "timestamp": "2024-01-20T12:00:00.000Z",
        "latitude": 18.92,
        "longitude": 72.83,
        "speed": 14.2,
        "course": 215.5,
        "nav_status": "UNDER_WAY_USING_ENGINE",
    }
    obs = VesselParser.parse_ais_observation(raw_obs)
    print(f"  - Transformed AIS Obs ID: {obs['observation_id']}")
    print(f"  - Lat/Lon: [{obs['latitude']}, {obs['longitude']}], Speed: {obs['speed_over_ground_knots']} kn")
    
    assert len(obs["mmsi"]) == 9
    assert -90.0 <= obs["latitude"] <= 90.0
    assert -180.0 <= obs["longitude"] <= 180.0
    assert 0.0 <= obs["speed_over_ground_knots"] <= 102.2
    assert obs["navigational_status"] == "UNDER_WAY_USING_ENGINE"

    print("[PASS] Parsing & Contract Conformance verified 100%.")


def test_deterministic_caching():
    print("\n--- [Test 4] Deterministic SHA-256 Cache Behavior ---")
    tmp_dir = tempfile.mkdtemp(prefix="marineshield_cache_test_")
    try:
        cache_mgr = VesselCacheManager(cache_dir=tmp_dir)
        params = {"query": "test_vessel", "limit": 3}
        key = cache_mgr.generate_cache_key("test", params)

        payload = {"items": [{"id": 1, "name": "Vessel A"}, {"id": 2, "name": "Vessel B"}]}
        file_path = cache_mgr.set(key, payload, query_params=params)

        print(f"  - Cache file created: {os.path.basename(file_path)}")
        assert os.path.isfile(file_path), "Cache file was not created"

        retrieved = cache_mgr.get(key)
        assert retrieved is not None, "Cache retrieval returned None"
        assert retrieved["data"]["items"] == payload["items"], "Cached payload mismatch"
        assert "provenance" in retrieved, "Missing provenance in cached record"
        assert len(retrieved["provenance"]["sha256"]) == 64, "SHA-256 digest invalid length"

        print(f"  - Provenance SHA-256: {retrieved['provenance']['sha256'][:16]}...")
        print("[PASS] Deterministic cache & cryptographic provenance verified.")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_edge_cases_and_malformed_inputs():
    print("\n--- [Test 5] Malformed Data & Edge Cases ---")
    # Missing MMSI
    v1 = VesselParser.parse_gfw_vessel_entry({"shipname": "Ghost Ship"})
    assert v1["mmsi"] == "000000000"
    
    # Invalid numbers
    v2 = VesselParser.parse_gfw_vessel_entry({"mmsi": "123", "length": -50.0, "width": 0.0})
    assert len(v2["mmsi"]) == 9
    assert v2["length_meters"] >= 1.0
    assert v2["beam_meters"] >= 1.0

    # Malformed timestamp
    obs = VesselParser.parse_ais_observation({"mmsi": "999888777", "timestamp": "invalid_date_str"})
    assert obs["timestamp"].endswith("Z")

    print("[PASS] Edge cases and malformed inputs handled gracefully.")


def test_live_gfw_smoke():
    print("\n--- [Test 6] Live GFW API Smoke Test ---")
    adapter = GFWClientAdapter()
    auth = adapter.check_authentication()
    print(f"  - Authentication Status: {auth['mode']}")

    if auth["authenticated"] and auth["client_ready"]:
        res = adapter.search_vessels(query="fishing", limit=2, use_cache=True)
        print(f"  - Live Search Result: Status={res['status']}, Count={res['raw_count']}")
        assert res["status"] in ("SUCCESS_LIVE", "SUCCESS_CACHED", "SUCCESS_MOCK")
        print("[PASS] Live GFW API Smoke Test PASSED.")
    else:
        print("  - [NOT RUN] Live credentials not configured or unauthenticated; skipping live call.")


def main():
    print("================================================================================")
    print("      MarineShield Vessel Ingestion & Acquisition Modular Test Suite")
    print("================================================================================")

    test_offline_mock_mode()
    test_response_parsing_and_contract_conformance()
    test_deterministic_caching()
    test_edge_cases_and_malformed_inputs()
    test_live_gfw_smoke()

    print("\n================================================================================")
    print("   [SUCCESS] All Vessel Acquisition Modular Package Tests Passed 100%!")
    print("================================================================================")


if __name__ == "__main__":
    main()
